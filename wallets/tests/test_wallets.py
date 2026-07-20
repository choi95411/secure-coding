import threading
import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from wallets.models import LedgerEntry, Transfer
from wallets.services import IdempotencyConflict, transfer_points, wallet_is_consistent

User = get_user_model()


class WalletServiceTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="Test-Password-123!")
        self.bob = User.objects.create_user("bob", password="Test-Password-123!")

    def test_new_user_receives_initial_points_with_ledger(self):
        self.assertEqual(self.alice.wallet.balance, 10_000)
        entry = self.alice.wallet.ledger_entries.get()
        self.assertIsNone(entry.transfer)
        self.assertEqual(entry.direction, LedgerEntry.Direction.CREDIT)
        self.assertEqual(entry.balance_after, 10_000)

    def test_successful_transfer_updates_both_wallets_and_ledger_atomically(self):
        result = transfer_points(
            sender=self.alice,
            recipient=self.bob,
            amount=2_500,
            idempotency_key=uuid.uuid4(),
        )
        self.alice.wallet.refresh_from_db()
        self.bob.wallet.refresh_from_db()
        self.assertEqual(result.transfer.status, Transfer.Status.SUCCEEDED)
        self.assertEqual(self.alice.wallet.balance, 7_500)
        self.assertEqual(self.bob.wallet.balance, 12_500)
        self.assertEqual(result.transfer.ledger_entries.count(), 2)
        self.assertTrue(wallet_is_consistent(self.alice.wallet))
        self.assertTrue(wallet_is_consistent(self.bob.wallet))

    def test_insufficient_balance_fails_without_balance_or_ledger_change(self):
        result = transfer_points(
            sender=self.alice,
            recipient=self.bob,
            amount=10_001,
            idempotency_key=uuid.uuid4(),
        )
        self.alice.wallet.refresh_from_db()
        self.bob.wallet.refresh_from_db()
        self.assertEqual(result.transfer.status, Transfer.Status.FAILED)
        self.assertEqual(result.transfer.failure_code, "insufficient_balance")
        self.assertEqual(self.alice.wallet.balance, 10_000)
        self.assertEqual(self.bob.wallet.balance, 10_000)
        self.assertFalse(result.transfer.ledger_entries.exists())

    def test_self_and_inactive_recipient_are_rejected(self):
        self_transfer = transfer_points(
            sender=self.alice,
            recipient=self.alice,
            amount=1,
            idempotency_key=uuid.uuid4(),
        )
        self.assertEqual(self_transfer.transfer.failure_code, "self_transfer")
        self.bob.status = User.Status.BLOCKED
        self.bob.save(update_fields=("status",))
        inactive = transfer_points(
            sender=self.alice,
            recipient=self.bob,
            amount=1,
            idempotency_key=uuid.uuid4(),
        )
        self.assertEqual(inactive.transfer.failure_code, "recipient_inactive")

    def test_idempotency_replays_same_request_and_rejects_changed_payload(self):
        key = uuid.uuid4()
        first = transfer_points(
            sender=self.alice, recipient=self.bob, amount=500, idempotency_key=key
        )
        replay = transfer_points(
            sender=self.alice, recipient=self.bob, amount=500, idempotency_key=key
        )
        self.assertTrue(replay.replayed)
        self.assertEqual(first.transfer.pk, replay.transfer.pk)
        self.alice.wallet.refresh_from_db()
        self.assertEqual(self.alice.wallet.balance, 9_500)
        with self.assertRaises(IdempotencyConflict):
            transfer_points(sender=self.alice, recipient=self.bob, amount=501, idempotency_key=key)

    def test_nonpositive_amount_creates_no_transfer(self):
        with self.assertRaises(ValueError):
            transfer_points(
                sender=self.alice, recipient=self.bob, amount=0, idempotency_key=uuid.uuid4()
            )
        self.assertFalse(Transfer.objects.exists())

    def test_ledger_is_immutable(self):
        entry = self.alice.wallet.ledger_entries.get()
        entry.balance_after = 1
        with self.assertRaises(ValidationError):
            entry.save()
        with self.assertRaises(ValidationError):
            entry.delete()
        with self.assertRaises(ValidationError):
            LedgerEntry.objects.all().delete()

    def test_exception_rolls_back_transfer_and_balances(self):
        with mock.patch(
            "wallets.services.LedgerEntry.objects.bulk_create", side_effect=RuntimeError("db error")
        ):
            with self.assertRaises(RuntimeError):
                transfer_points(
                    sender=self.alice,
                    recipient=self.bob,
                    amount=100,
                    idempotency_key=uuid.uuid4(),
                )
        self.alice.wallet.refresh_from_db()
        self.bob.wallet.refresh_from_db()
        self.assertEqual((self.alice.wallet.balance, self.bob.wallet.balance), (10_000, 10_000))
        self.assertFalse(Transfer.objects.exists())


class WalletViewTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="Test-Password-123!")
        self.bob = User.objects.create_user("bob", password="Test-Password-123!")

    def test_wallet_requires_authentication(self):
        self.assertEqual(self.client.get(reverse("wallets:detail")).status_code, 302)

    def test_transfer_form_success_and_tampered_recipient_failure(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            reverse("wallets:transfer"),
            {"recipient": self.bob.pk, "amount": 100, "idempotency_key": uuid.uuid4()},
        )
        self.assertRedirects(response, reverse("wallets:detail"))
        self.bob.status = User.Status.BLOCKED
        self.bob.save(update_fields=("status",))
        response = self.client.post(
            reverse("wallets:transfer"),
            {"recipient": self.bob.pk, "amount": 100, "idempotency_key": uuid.uuid4()},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transfer.objects.count(), 1)


class PostgreSQLConcurrentTransferTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_transfers_never_overdraw(self):
        if connection.vendor != "postgresql":
            self.skipTest("PostgreSQL row-lock integration test")
        sender = User.objects.create_user("sender", password="Test-Password-123!")
        recipients = [
            User.objects.create_user("recipient1", password="Test-Password-123!"),
            User.objects.create_user("recipient2", password="Test-Password-123!"),
        ]
        barrier = threading.Barrier(2)
        statuses = []

        def run(recipient_id):
            close_old_connections()
            barrier.wait()
            result = transfer_points(
                sender=User.objects.get(pk=sender.pk),
                recipient=User.objects.get(pk=recipient_id),
                amount=8_000,
                idempotency_key=uuid.uuid4(),
            )
            statuses.append(result.transfer.status)
            connection.close()

        threads = [threading.Thread(target=run, args=(recipient.pk,)) for recipient in recipients]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        sender.wallet.refresh_from_db()
        self.assertEqual(statuses.count(Transfer.Status.SUCCEEDED), 1)
        self.assertEqual(statuses.count(Transfer.Status.FAILED), 1)
        self.assertEqual(sender.wallet.balance, 2_000)
