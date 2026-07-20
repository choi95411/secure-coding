from django import forms
from django.contrib import admin
from django.db import transaction

from moderation.models import AdminAuditLog

from .models import Conversation, ConversationMember, Message


class ReadOnlyChatAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Conversation)
class ConversationAdmin(ReadOnlyChatAdmin):
    list_display = ("id", "kind", "title", "is_active", "updated_at")
    list_filter = ("kind", "is_active")


@admin.register(ConversationMember)
class ConversationMemberAdmin(ReadOnlyChatAdmin):
    list_display = ("conversation", "user", "joined_at")
    search_fields = ("user__username",)


class MessageAdminForm(forms.ModelForm):
    moderation_reason = forms.CharField(
        required=False,
        min_length=5,
        max_length=1000,
        label="상태 변경 사유",
        help_text="메시지 상태를 변경할 때 5자 이상 입력해야 합니다.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = Message
        fields = ("status",)

    def clean(self):
        cleaned = super().clean()
        if "status" in self.changed_data and len(cleaned.get("moderation_reason", "").strip()) < 5:
            self.add_error("moderation_reason", "상태 변경 사유는 5자 이상이어야 합니다.")
        return cleaned


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    list_display = ("conversation", "sender", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("content", "sender__username")
    readonly_fields = ("conversation", "sender", "content", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        before_status = Message.objects.select_for_update().get(pk=obj.pk).status
        super().save_model(request, obj, form, change)
        if before_status != obj.status:
            AdminAuditLog.objects.create(
                actor=request.user,
                action="moderate_message",
                target_type="message",
                target_id=str(obj.pk),
                reason=form.cleaned_data["moderation_reason"].strip(),
                before={"status": before_status},
                after={"status": obj.status},
            )
