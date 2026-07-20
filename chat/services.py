from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction

from .models import Conversation, ConversationMember


@transaction.atomic
def get_global_conversation(user):
    if not user.can_use_platform:
        raise PermissionDenied
    try:
        conversation = Conversation.objects.get(kind=Conversation.Kind.GLOBAL)
    except Conversation.DoesNotExist:
        try:
            with transaction.atomic():
                conversation = Conversation.objects.create(
                    kind=Conversation.Kind.GLOBAL,
                    title="전체 채팅",
                    created_by=user,
                )
        except IntegrityError:
            conversation = Conversation.objects.get(kind=Conversation.Kind.GLOBAL)
    ConversationMember.objects.get_or_create(conversation=conversation, user=user)
    return conversation


@transaction.atomic
def get_or_create_direct_conversation(user, other):
    if not user.can_use_platform or not other.can_use_platform:
        raise PermissionDenied
    if user.pk == other.pk:
        raise ValidationError("자기 자신과 1대1 채팅을 만들 수 없습니다.")
    first_id, second_id = sorted((user.pk, other.pk))
    key = f"{first_id}:{second_id}"
    try:
        conversation = Conversation.objects.get(direct_key=key)
    except Conversation.DoesNotExist:
        try:
            with transaction.atomic():
                conversation = Conversation.objects.create(
                    direct_key=key,
                    kind=Conversation.Kind.DIRECT,
                    title="1대1 채팅",
                    created_by=user,
                )
        except IntegrityError:
            conversation = Conversation.objects.get(direct_key=key)
    ConversationMember.objects.bulk_create(
        [
            ConversationMember(conversation=conversation, user_id=first_id),
            ConversationMember(conversation=conversation, user_id=second_id),
        ],
        ignore_conflicts=True,
    )
    return conversation


def can_access_conversation(user, conversation):
    if not user.is_authenticated or not user.can_use_platform or not conversation.is_active:
        return False
    if conversation.kind == Conversation.Kind.GLOBAL:
        return True
    return conversation.memberships.filter(user=user).exists()
