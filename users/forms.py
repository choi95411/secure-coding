from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

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
