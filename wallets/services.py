from dataclasses import dataclass
from uuid import UUID

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from users.models import User

from .models import LedgerEntry, Transfer, Wallet


@dataclass(frozen=True)
class TransferResult:
    transfer: Transfer
    replayed: bool = False


class IdempotencyConflict(ValueError):
    pass


def _failed(transfer, code):
    transfer.status = Transfer.Status.FAILED
    transfer.failure_code = code
    transfer.completed_at = timezone.now()
    transfer.save(update_fields=("status", "failure_code", "completed_at"))
    return TransferResult(transfer)


@transaction.atomic
def transfer_points(*, sender: User, recipient: User, amount: int, idempotency_key: UUID):
    amount = int(amount)
    if amount <= 0:
        raise ValueError("송금액은 양의 정수여야 합니다.")
    if amount > settings.MAX_POINT_TRANSACTION:
        raise ValueError("1회 송금 한도를 초과했습니다.")
    existing = Transfer.objects.filter(sender=sender, idempotency_key=idempotency_key).first()
    if existing:
        if existing.recipient_id != recipient.id or existing.amount != amount:
            raise IdempotencyConflict("같은 멱등 키를 다른 송금에 사용할 수 없습니다.")
        return TransferResult(existing, replayed=True)

    transfer = Transfer(
        sender=sender,
        recipient=recipient,
        amount=int(amount),
        idempotency_key=idempotency_key,
    )
    if sender.pk == recipient.pk:
        transfer.save()
        return _failed(transfer, "self_transfer")
    try:
        with transaction.atomic():
            transfer.save()
    except IntegrityError as exc:
        existing = Transfer.objects.get(sender=sender, idempotency_key=idempotency_key)
        if existing.recipient_id != recipient.id or existing.amount != amount:
            raise IdempotencyConflict("같은 멱등 키를 다른 송금에 사용할 수 없습니다.") from exc
        return TransferResult(existing, replayed=True)

    users = {
        user.pk: user
        for user in User.objects.select_for_update()
        .filter(pk__in=(sender.pk, recipient.pk))
        .order_by("pk")
    }
    if users[sender.pk].status != User.Status.ACTIVE or not users[sender.pk].is_active:
        return _failed(transfer, "sender_inactive")
    if users[recipient.pk].status != User.Status.ACTIVE or not users[recipient.pk].is_active:
        return _failed(transfer, "recipient_inactive")

    wallets = {
        wallet.user_id: wallet
        for wallet in Wallet.objects.select_for_update()
        .filter(user_id__in=(sender.pk, recipient.pk))
        .order_by("pk")
    }
    sender_wallet = wallets[sender.pk]
    recipient_wallet = wallets[recipient.pk]
    if sender_wallet.balance < amount:
        return _failed(transfer, "insufficient_balance")
    if recipient_wallet.balance > settings.MAX_WALLET_BALANCE - amount:
        return _failed(transfer, "recipient_balance_limit")

    sender_wallet.balance -= amount
    recipient_wallet.balance += amount
    sender_wallet.save(update_fields=("balance", "updated_at"))
    recipient_wallet.save(update_fields=("balance", "updated_at"))
    LedgerEntry.objects.bulk_create(
        [
            LedgerEntry(
                wallet=sender_wallet,
                transfer=transfer,
                direction=LedgerEntry.Direction.DEBIT,
                amount=amount,
                balance_after=sender_wallet.balance,
            ),
            LedgerEntry(
                wallet=recipient_wallet,
                transfer=transfer,
                direction=LedgerEntry.Direction.CREDIT,
                amount=amount,
                balance_after=recipient_wallet.balance,
            ),
        ]
    )
    transfer.status = Transfer.Status.SUCCEEDED
    transfer.completed_at = timezone.now()
    transfer.save(update_fields=("status", "completed_at"))
    return TransferResult(transfer)


def wallet_is_consistent(wallet):
    entries = wallet.ledger_entries.order_by("created_at", "id")
    if not entries.exists():
        return wallet.balance == 0
    return entries.last().balance_after == wallet.balance
