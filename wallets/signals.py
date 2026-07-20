from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User

from .models import LedgerEntry, Wallet


@receiver(post_save, sender=User)
def create_initial_wallet(sender, instance, created, **kwargs):
    if not created:
        return
    initial = int(getattr(settings, "INITIAL_WALLET_POINTS", 10_000))
    wallet = Wallet.objects.create(user=instance, balance=initial)
    if initial:
        LedgerEntry.objects.create(
            wallet=wallet,
            direction=LedgerEntry.Direction.CREDIT,
            amount=initial,
            balance_after=initial,
        )
