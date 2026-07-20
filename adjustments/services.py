from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from moderation.models import AdminAuditLog
from wallets.models import LedgerEntry, Wallet

from .models import WalletAdjustment


@transaction.atomic
def adjust_wallet(*, actor, user, amount, reason):
    if not actor.is_active or not actor.is_staff:
        raise PermissionDenied
    amount = int(amount)
    reason = reason.strip()
    if amount == 0:
        raise ValidationError("조정 금액은 0일 수 없습니다.")
    if len(reason) < 5:
        raise ValidationError("조정 사유는 5자 이상이어야 합니다.")

    wallet = Wallet.objects.select_for_update().get(user=user)
    before_balance = wallet.balance
    after_balance = before_balance + amount
    if after_balance < 0:
        raise ValidationError("조정 후 잔액은 음수가 될 수 없습니다.")

    wallet.balance = after_balance
    wallet.save(update_fields=("balance", "updated_at"))
    ledger = LedgerEntry.objects.create(
        wallet=wallet,
        direction=(LedgerEntry.Direction.CREDIT if amount > 0 else LedgerEntry.Direction.DEBIT),
        amount=abs(amount),
        balance_after=after_balance,
    )
    adjustment = WalletAdjustment.objects.create(
        wallet=wallet,
        actor=actor,
        amount=amount,
        reason=reason,
        ledger_entry=ledger,
    )
    AdminAuditLog.objects.create(
        actor=actor,
        action="wallet_adjustment",
        target_type="wallet",
        target_id=str(wallet.pk),
        reason=reason,
        before={"balance": before_balance},
        after={"balance": after_balance, "adjustment": amount},
    )
    return adjustment
