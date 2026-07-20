from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from wallets.models import LedgerEntry, Wallet


class WalletAdjustmentQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("조정 거래는 수정할 수 없습니다.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError("조정 거래는 수정할 수 없습니다.")

    def delete(self):
        raise ValidationError("조정 거래는 삭제할 수 없습니다.")


class WalletAdjustment(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="adjustments")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="wallet_adjustments"
    )
    amount = models.BigIntegerField()
    reason = models.CharField(max_length=1000)
    ledger_entry = models.OneToOneField(
        LedgerEntry, on_delete=models.PROTECT, related_name="adjustment"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WalletAdjustmentQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(condition=~models.Q(amount=0), name="wallet_adjustment_nonzero")
        ]

    def __str__(self):
        return f"{self.wallet.user}: {self.amount:+d}"

    def save(self, *args, **kwargs):
        if self.pk and WalletAdjustment.objects.filter(pk=self.pk).exists():
            raise ValidationError("조정 거래는 수정할 수 없습니다.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("조정 거래는 삭제할 수 없습니다.")
