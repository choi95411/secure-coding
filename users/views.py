from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActiveAuthenticationForm, ProfileForm, SafePasswordChangeForm, SignupForm
from .models import User


def signup(request):
    if request.user.is_authenticated:
        return redirect("products:list")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/signup.html", {"form": form})


class PlatformLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = ActiveAuthenticationForm
    redirect_authenticated_user = True


class PlatformLogoutView(LogoutView):
    http_method_names = ["post", "options"]


def public_profile(request, username):
    user = get_object_or_404(
        User.objects.select_related("profile"), username=username, status=User.Status.ACTIVE
    )
    return render(request, "users/public_profile.html", {"profile_user": user})


@login_required
def mypage(request):
    return render(request, "users/mypage.html")


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, instance=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:mypage")
    return render(request, "users/profile_form.html", {"form": form})


@login_required
def password_change(request):
    form = SafePasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:mypage")
    return render(request, "users/password_change.html", {"form": form})
