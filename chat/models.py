from django.conf import settings
from django.db import models


class Conversation(models.Model):
    class Kind(models.TextChoices):
        GLOBAL = "global", "전체 채팅"
        DIRECT = "direct", "1대1 채팅"

    kind = models.CharField(max_length=12, choices=Kind.choices, db_index=True)
    title = models.CharField(max_length=120, blank=True)
    direct_key = models.CharField(max_length=80, null=True, blank=True, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.PROTECT,
        related_name="created_conversations",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-id")
        constraints = [
            models.UniqueConstraint(
                fields=("kind",),
                condition=models.Q(kind="global"),
                name="single_global_conversation",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(kind="direct", direct_key__isnull=False)
                    | models.Q(kind="global", direct_key__isnull=True)
                ),
                name="conversation_kind_key_valid",
            ),
        ]

    def __str__(self):
        return self.title or f"{self.get_kind_display()} #{self.pk}"


class ConversationMember(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="conversation_memberships"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("conversation", "user"), name="conversation_member_uniq"
            )
        ]
        indexes = [models.Index(fields=("user", "conversation"), name="chat_member_lookup_idx")]

    def __str__(self):
        return f"{self.conversation}: {self.user}"


class Message(models.Model):
    class Status(models.TextChoices):
        VISIBLE = "visible", "표시"
        HIDDEN = "hidden", "숨김"
        DELETED = "deleted", "삭제"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.PROTECT, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="chat_messages"
    )
    content = models.CharField(max_length=1000)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.VISIBLE, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "id")
        indexes = [
            models.Index(
                fields=("conversation", "status", "-created_at"), name="chat_message_recent_idx"
            ),
            models.Index(fields=("sender", "-created_at"), name="chat_sender_rate_idx"),
        ]

    def __str__(self):
        return f"{self.sender}: {self.content[:40]}"
