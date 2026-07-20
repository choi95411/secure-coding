import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="wallet"
    )
    balance = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.balance} points"


class Transfer(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "처리 중"
        SUCCEEDED = "succeeded", "성공"
        FAILED = "failed", "실패"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sent_transfers"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="received_transfers"
    )
    amount = models.PositiveBigIntegerField()
    idempotency_key = models.UUIDField()
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    failure_code = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("sender", "idempotency_key"), name="transfer_sender_idem_uniq"
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gt=0), name="transfer_amount_positive"
            ),
            models.CheckConstraint(
                condition=~(models.Q(status="succeeded") & models.Q(sender=models.F("recipient"))),
                name="successful_transfer_no_self",
            ),
        ]

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"


class LedgerEntryQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("원장 항목은 수정할 수 없습니다.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError("원장 항목은 수정할 수 없습니다.")

    def delete(self):
        raise ValidationError("원장 항목은 삭제할 수 없습니다.")


class LedgerEntry(models.Model):
    class Direction(models.TextChoices):
        DEBIT = "debit", "출금"
        CREDIT = "credit", "입금"

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="ledger_entries")
    transfer = models.ForeignKey(
        Transfer,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    direction = models.CharField(max_length=8, choices=Direction.choices)
    amount = models.PositiveBigIntegerField()
    balance_after = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = LedgerEntryQuerySet.as_manager()

    class Meta:
        ordering = ("created_at", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("transfer", "wallet"), name="ledger_transfer_wallet_uniq"
            ),
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="ledger_amount_positive"),
        ]

    def __str__(self):
        return f"{self.wallet} {self.direction} {self.amount}"

    def save(self, *args, **kwargs):
        if self.pk and LedgerEntry.objects.filter(pk=self.pk).exists():
            raise ValidationError("원장 항목은 수정할 수 없습니다.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("원장 항목은 삭제할 수 없습니다.")
