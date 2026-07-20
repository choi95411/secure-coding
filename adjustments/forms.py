from django import forms

from users.models import User


class WalletAdjustmentForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.order_by("username"), label="대상 사용자")
    amount = forms.IntegerField(label="조정 포인트", help_text="차감은 음수로 입력합니다.")
    reason = forms.CharField(
        min_length=5, max_length=1000, widget=forms.Textarea(attrs={"rows": 3})
    )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount == 0:
            raise forms.ValidationError("0은 입력할 수 없습니다.")
        return amount
