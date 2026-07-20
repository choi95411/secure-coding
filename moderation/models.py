from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "대기"
        RESOLVED = "resolved", "처리"
        REJECTED = "rejected", "기각"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reports_made"
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reports_received",
    )
    target_product = models.ForeignKey(
        "products.Product", null=True, blank=True, on_delete=models.PROTECT, related_name="reports"
    )
    reason = models.CharField(max_length=1000)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(target_user__isnull=False, target_product__isnull=True)
                    | models.Q(target_user__isnull=True, target_product__isnull=False)
                ),
                name="report_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=("reporter", "target_user"),
                condition=models.Q(status="pending", target_user__isnull=False),
                name="pending_user_report_uniq",
            ),
            models.UniqueConstraint(
                fields=("reporter", "target_product"),
                condition=models.Q(status="pending", target_product__isnull=False),
                name="pending_product_report_uniq",
            ),
        ]

    def __str__(self):
        return f"report {self.pk} by {self.reporter}"


class ModerationAction(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.PROTECT,
        related_name="moderation_actions",
    )
    action = models.CharField(max_length=40)
    target_type = models.CharField(max_length=30)
    target_id = models.CharField(max_length=64)
    reason = models.CharField(max_length=1000)
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action}: {self.target_type} {self.target_id}"


class AdminAuditLogQuerySet(models.QuerySet):
    def delete(self):
        raise ValidationError("관리자 감사 로그는 삭제할 수 없습니다.")


class AdminAuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="admin_audit_logs"
    )
    action = models.CharField(max_length=80)
    target_type = models.CharField(max_length=40)
    target_id = models.CharField(max_length=64)
    reason = models.CharField(max_length=1000)
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AdminAuditLogQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.actor}: {self.action}"

    def save(self, *args, **kwargs):
        if self.pk and AdminAuditLog.objects.filter(pk=self.pk).exists():
            raise ValidationError("관리자 감사 로그는 수정할 수 없습니다.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("관리자 감사 로그는 삭제할 수 없습니다.")
