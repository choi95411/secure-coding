from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

from security_controls.services import (
    clear_login_failures,
    is_login_locked,
    login_identifier,
    record_login_failure,
)

from .models import User, UserProfile


class SignupForm(UserCreationForm):
    display_name = forms.CharField(max_length=40, label="표시 이름")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "display_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.update_or_create(
                user=user, defaults={"display_name": self.cleaned_data["display_name"]}
            )
        return user


class ActiveAuthenticationForm(AuthenticationForm):
    def clean(self):
        identifier = login_identifier(
            self.data.get("username", ""),
            self.request.META.get("REMOTE_ADDR") if self.request else None,
        )
        if is_login_locked(identifier):
            raise forms.ValidationError("로그인 시도가 너무 많습니다. 잠시 후 다시 시도하세요.")
        try:
            cleaned_data = super().clean()
        except forms.ValidationError:
            record_login_failure(identifier)
            raise
        clear_login_failures(identifier)
        return cleaned_data

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.status != User.Status.ACTIVE:
            raise forms.ValidationError("사용할 수 없는 계정입니다.", code="inactive")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("display_name", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}


class SafePasswordChangeForm(PasswordChangeForm):
    pass
