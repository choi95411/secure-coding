from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect, render

from .forms import WalletAdjustmentForm
from .models import WalletAdjustment
from .services import adjust_wallet


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped


@staff_required
def adjustment_list(request):
    adjustments = WalletAdjustment.objects.select_related("wallet__user", "actor")[:100]
    return render(request, "adjustments/list.html", {"adjustments": adjustments})


@staff_required
def adjustment_create(request):
    form = WalletAdjustmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            adjust_wallet(actor=request.user, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("adjustments:list")
    return render(request, "adjustments/form.html", {"form": form})
