from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from chat.models import Message
from chat.services import get_or_create_direct_conversation
from moderation.models import AdminAuditLog

User = get_user_model()


class ChatAdminAuditTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "chat-admin", password="Test-Password-123!", email="admin@example.test"
        )
        self.alice = User.objects.create_user("chat-user-a", password="Test-Password-123!")
        self.bob = User.objects.create_user("chat-user-b", password="Test-Password-123!")
        conversation = get_or_create_direct_conversation(self.alice, self.bob)
        self.message = Message.objects.create(
            conversation=conversation,
            sender=self.alice,
            content="관리 대상 메시지",
        )
        self.url = reverse("admin:chat_message_change", args=[self.message.pk])

    def test_nonstaff_cannot_open_message_admin(self):
        self.client.force_login(self.alice)
        self.assertNotEqual(self.client.get(self.url).status_code, 200)

    def test_status_change_requires_reason_and_creates_immutable_audit(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url,
            {
                "status": Message.Status.HIDDEN,
                "moderation_reason": "악성 메시지 숨김",
                "_save": "저장",
            },
        )
        self.assertRedirects(response, reverse("admin:chat_message_changelist"))
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.Status.HIDDEN)
        audit = AdminAuditLog.objects.get(action="moderate_message", target_id=str(self.message.pk))
        self.assertEqual(audit.actor, self.admin)
        self.assertEqual(audit.reason, "악성 메시지 숨김")
        self.assertEqual(audit.before, {"status": Message.Status.VISIBLE})
        self.assertEqual(audit.after, {"status": Message.Status.HIDDEN})

        response = self.client.post(
            self.url,
            {"status": Message.Status.DELETED, "moderation_reason": "짧음", "_save": "저장"},
        )
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.Status.HIDDEN)
