from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from adjustments.models import WalletAdjustment
from adjustments.services import adjust_wallet
from moderation.models import AdminAuditLog
from wallets.models import LedgerEntry

User = get_user_model()


class WalletAdjustmentTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", password="Test-Password-123!", is_staff=True)
        self.user = User.objects.create_user("user", password="Test-Password-123!")

    def test_credit_and_debit_create_linked_ledger_and_audit(self):
        credit = adjust_wallet(
            actor=self.admin, user=self.user, amount=500, reason="고객 지원 보상 지급"
        )
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 10_500)
        self.assertEqual(credit.ledger_entry.direction, LedgerEntry.Direction.CREDIT)
        debit = adjust_wallet(
            actor=self.admin, user=self.user, amount=-200, reason="오지급 포인트 회수"
        )
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 10_300)
        self.assertEqual(debit.ledger_entry.direction, LedgerEntry.Direction.DEBIT)
        self.assertEqual(AdminAuditLog.objects.filter(action="wallet_adjustment").count(), 2)

    def test_nonstaff_zero_and_overdraft_are_rejected_without_changes(self):
        with self.assertRaises(PermissionDenied):
            adjust_wallet(actor=self.user, user=self.user, amount=1, reason="권한 없는 조정")
        with self.assertRaises(ValidationError):
            adjust_wallet(actor=self.admin, user=self.user, amount=0, reason="영점 조정 거절")
        with self.assertRaises(ValidationError):
            adjust_wallet(actor=self.admin, user=self.user, amount=-10_001, reason="잔액 초과 회수")
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 10_000)
        self.assertFalse(WalletAdjustment.objects.exists())

    def test_adjustment_amount_and_resulting_balance_are_bounded(self):
        with self.assertRaises(ValidationError):
            adjust_wallet(
                actor=self.admin,
                user=self.user,
                amount=1_000_000_001,
                reason="조정 한도 초과 검증",
            )
        with self.settings(MAX_WALLET_BALANCE=10_000):
            with self.assertRaises(ValidationError):
                adjust_wallet(
                    actor=self.admin,
                    user=self.user,
                    amount=1,
                    reason="잔액 한도 초과 검증",
                )
        self.assertFalse(WalletAdjustment.objects.exists())

    def test_failure_rolls_back_balance_ledger_adjustment_and_audit(self):
        initial_entries = self.user.wallet.ledger_entries.count()
        with mock.patch(
            "adjustments.services.AdminAuditLog.objects.create",
            side_effect=RuntimeError("audit unavailable"),
        ):
            with self.assertRaises(RuntimeError):
                adjust_wallet(
                    actor=self.admin,
                    user=self.user,
                    amount=100,
                    reason="감사 실패 롤백 검증",
                )
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 10_000)
        self.assertEqual(self.user.wallet.ledger_entries.count(), initial_entries)
        self.assertFalse(WalletAdjustment.objects.exists())

    def test_adjustment_is_immutable(self):
        adjustment = adjust_wallet(
            actor=self.admin, user=self.user, amount=10, reason="불변성 검증 거래"
        )
        adjustment.reason = "변조"
        with self.assertRaises(ValidationError):
            adjustment.save()
        with self.assertRaises(ValidationError):
            adjustment.delete()
        with self.assertRaises(ValidationError):
            WalletAdjustment.objects.all().delete()

    def test_admin_view_rejects_regular_user_and_accepts_staff(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("adjustments:list")).status_code, 403)
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("adjustments:create"),
            {"user": self.user.pk, "amount": 50, "reason": "관리 화면 조정 검증"},
        )
        self.assertRedirects(response, reverse("adjustments:list"))
