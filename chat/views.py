from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.models import User

from .models import Conversation, Message
from .services import (
    can_access_conversation,
    get_global_conversation,
    get_or_create_direct_conversation,
)


@login_required
def conversation_list(request):
    direct = Conversation.objects.filter(
        kind=Conversation.Kind.DIRECT,
        memberships__user=request.user,
        is_active=True,
    ).distinct()
    return render(request, "chat/list.html", {"conversations": direct})


@login_required
def global_chat(request):
    conversation = get_global_conversation(request.user)
    return redirect("chat:detail", pk=conversation.pk)


@login_required
@require_POST
def direct_start(request, username):
    other = get_object_or_404(User, username=username, status=User.Status.ACTIVE, is_active=True)
    conversation = get_or_create_direct_conversation(request.user, other)
    return redirect("chat:detail", pk=conversation.pk)


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, is_active=True)
    if not can_access_conversation(request.user, conversation):
        raise PermissionDenied
    if conversation.kind == Conversation.Kind.GLOBAL:
        conversation.memberships.get_or_create(user=request.user)
    messages = conversation.messages.filter(status=Message.Status.VISIBLE).select_related(
        "sender", "sender__profile"
    )
    page = Paginator(messages.order_by("-created_at", "-id"), 50).get_page(request.GET.get("page"))
    return render(request, "chat/detail.html", {"conversation": conversation, "page": page})
