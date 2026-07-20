from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from moderation.models import AdminAuditLog, ModerationAction

User = get_user_model()


class AdminAuditImmutabilityTests(TestCase):
    def test_audit_log_cannot_be_updated_or_deleted(self):
        admin = User.objects.create_user(
            "admin-audit", password="Test-Password-123!", is_staff=True
        )
        log = AdminAuditLog.objects.create(
            actor=admin,
            action="test",
            target_type="user",
            target_id="1",
            reason="감사 로그 불변성 검증",
            before={},
            after={"status": "blocked"},
        )
        log.reason = "변조"
        with self.assertRaises(ValidationError):
            log.save()
        with self.assertRaises(ValidationError):
            log.delete()
        with self.assertRaises(ValidationError):
            AdminAuditLog.objects.all().delete()

    def test_moderation_action_cannot_be_changed_or_deleted(self):
        action = ModerationAction.objects.create(
            actor=None,
            action="auto_block_product",
            target_type="product",
            target_id="1",
            reason="자동 제재 불변성 검증",
            before={"status": "available"},
            after={"status": "blocked"},
        )
        action.reason = "변조"
        with self.assertRaises(ValidationError):
            action.save()
        with self.assertRaises(ValidationError):
            action.delete()
        with self.assertRaises(ValidationError):
            ModerationAction.objects.filter(pk=action.pk).update(reason="변조")
        with self.assertRaises(ValidationError):
            ModerationAction.objects.all().delete()
