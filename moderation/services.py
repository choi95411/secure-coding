from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from products.models import Product
from users.models import User

from .models import AdminAuditLog, ModerationAction, Report


@transaction.atomic
def file_report(*, reporter, target, reason):
    reason = reason.strip()
    if len(reason) < 5:
        raise ValidationError("신고 사유는 5자 이상이어야 합니다.")
    fields = {"target_user": target} if isinstance(target, User) else {"target_product": target}
    if isinstance(target, User) and reporter.pk == target.pk:
        raise ValidationError("자기 자신을 신고할 수 없습니다.")
    if isinstance(target, Product) and reporter.pk == target.seller_id:
        raise ValidationError("자신의 상품을 신고할 수 없습니다.")
    try:
        report = Report.objects.create(reporter=reporter, reason=reason, **fields)
    except IntegrityError as exc:
        raise ValidationError("이미 처리 대기 중인 신고가 있습니다.") from exc
    threshold = int(getattr(settings, "REPORT_BLOCK_THRESHOLD", 3))
    pending = Report.objects.filter(status=Report.Status.PENDING, **fields).count()
    if pending >= threshold:
        if isinstance(target, Product) and target.status != Product.Status.BLOCKED:
            before = {"status": target.status}
            target.status = Product.Status.BLOCKED
            target.save(update_fields=("status", "updated_at"))
            ModerationAction.objects.create(
                actor=None,
                action="auto_block_product",
                target_type="product",
                target_id=str(target.pk),
                reason=f"pending reports >= {threshold}",
                before=before,
                after={"status": target.status},
            )
        elif isinstance(target, User) and target.status == User.Status.ACTIVE:
            before = {"status": target.status}
            target.status = User.Status.DORMANT
            target.save(update_fields=("status",))
            ModerationAction.objects.create(
                actor=None,
                action="auto_dormant_user",
                target_type="user",
                target_id=str(target.pk),
                reason=f"pending reports >= {threshold}",
                before=before,
                after={"status": target.status},
            )
    return report


@transaction.atomic
def moderate_target(*, actor, target, action, reason):
    if not actor.is_staff:
        raise PermissionDenied
    if len(reason.strip()) < 5:
        raise ValidationError("제재 사유는 5자 이상이어야 합니다.")
    if isinstance(target, User):
        allowed = {
            "dormant": User.Status.DORMANT,
            "block": User.Status.BLOCKED,
            "restore": User.Status.ACTIVE,
        }
        if action not in allowed:
            raise ValidationError("허용되지 않은 작업입니다.")
        before = {"status": target.status}
        target.status = allowed[action]
        target.save(update_fields=("status",))
        target_type = "user"
    else:
        allowed = {
            "block": Product.Status.BLOCKED,
            "hide": Product.Status.DRAFT,
            "restore": Product.Status.AVAILABLE,
            "delete": Product.Status.DELETED,
        }
        if action not in allowed:
            raise ValidationError("허용되지 않은 작업입니다.")
        before = {"status": target.status}
        target.status = allowed[action]
        if action == "delete":
            target.deleted_at = timezone.now()
            target.save(update_fields=("status", "deleted_at", "updated_at"))
        else:
            target.save(update_fields=("status", "updated_at"))
        target_type = "product"
    after = {"status": target.status}
    ModerationAction.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target.pk),
        reason=reason.strip(),
        before=before,
        after=after,
    )
    AdminAuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target.pk),
        reason=reason.strip(),
        before=before,
        after=after,
    )
    report_filter = {"target_user": target} if target_type == "user" else {"target_product": target}
    Report.objects.filter(status=Report.Status.PENDING, **report_filter).update(
        status=Report.Status.RESOLVED, resolved_at=timezone.now()
    )
    return target
