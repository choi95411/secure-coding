import uuid

from django import forms
from django.conf import settings

from users.models import User


class TransferForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.none(), label="받는 사용자")
    amount = forms.IntegerField(
        min_value=1, max_value=settings.MAX_POINT_TRANSACTION, label="포인트"
    )
    idempotency_key = forms.UUIDField(widget=forms.HiddenInput)

    def __init__(self, *args, sender=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        self.fields["recipient"].queryset = User.objects.filter(
            status=User.Status.ACTIVE, is_active=True
        ).exclude(pk=getattr(sender, "pk", None))
        if not self.is_bound:
            self.initial["idempotency_key"] = uuid.uuid4()
