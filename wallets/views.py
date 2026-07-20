from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import TransferForm
from .services import IdempotencyConflict, transfer_points


@login_required
def wallet_detail(request):
    transfers = request.user.sent_transfers.select_related("recipient")[:20]
    received = request.user.received_transfers.select_related("sender")[:20]
    return render(request, "wallets/detail.html", {"transfers": transfers, "received": received})


@login_required
def transfer_create(request):
    form = TransferForm(request.POST or None, sender=request.user)
    if request.method == "POST" and form.is_valid():
        try:
            result = transfer_points(
                sender=request.user,
                recipient=form.cleaned_data["recipient"],
                amount=form.cleaned_data["amount"],
                idempotency_key=form.cleaned_data["idempotency_key"],
            )
        except IdempotencyConflict as exc:
            form.add_error("idempotency_key", str(exc))
        else:
            if result.transfer.status == result.transfer.Status.SUCCEEDED:
                messages.success(request, "송금이 완료되었습니다.")
                return redirect("wallets:detail")
            form.add_error(None, f"송금 실패: {result.transfer.failure_code}")
    return render(request, "wallets/transfer_form.html", {"form": form})
