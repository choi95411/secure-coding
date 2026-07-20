from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product
from users.models import User

from .forms import ModerationActionForm, ReportForm
from .models import Report
from .services import file_report, moderate_target


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped


@login_required
def report_product(request, pk):
    target = get_object_or_404(Product.objects.publicly_visible(), pk=pk)
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            file_report(reporter=request.user, target=target, reason=form.cleaned_data["reason"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("products:detail", pk=pk)
    return render(request, "moderation/report_form.html", {"form": form, "target": target})


@login_required
def report_user(request, username):
    target = get_object_or_404(User, username=username, status=User.Status.ACTIVE)
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            file_report(reporter=request.user, target=target, reason=form.cleaned_data["reason"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("users:public_profile", username=username)
    return render(request, "moderation/report_form.html", {"form": form, "target": target})


@staff_required
def dashboard(request):
    return render(
        request,
        "moderation/dashboard.html",
        {
            "reports": Report.objects.select_related("reporter", "target_user", "target_product")[
                :100
            ],
            "users": User.objects.select_related("profile").order_by("username")[:100],
            "products": Product.objects.select_related("seller").order_by("-created_at")[:100],
        },
    )


@staff_required
def moderate_user(request, pk):
    target = get_object_or_404(User, pk=pk)
    form = ModerationActionForm(
        request.POST or None, choices=(("dormant", "휴면"), ("block", "차단"), ("restore", "복구"))
    )
    if request.method == "POST" and form.is_valid():
        moderate_target(actor=request.user, target=target, **form.cleaned_data)
        return redirect("moderation:dashboard")
    return render(request, "moderation/action_form.html", {"form": form, "target": target})


@staff_required
def moderate_product(request, pk):
    target = get_object_or_404(Product, pk=pk)
    form = ModerationActionForm(
        request.POST or None,
        choices=(("hide", "숨김"), ("block", "차단"), ("delete", "삭제"), ("restore", "복구")),
    )
    if request.method == "POST" and form.is_valid():
        moderate_target(actor=request.user, target=target, **form.cleaned_data)
        return redirect("moderation:dashboard")
    return render(request, "moderation/action_form.html", {"form": form, "target": target})
