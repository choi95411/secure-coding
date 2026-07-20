from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from moderation.models import AdminAuditLog, ModerationAction, Report
from moderation.services import file_report, moderate_target
from products.models import Product

User = get_user_model()


class ReportTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user("seller", password="Test-Password-123!")
        self.product = Product.objects.create(
            seller=self.seller, title="상품", description="설명", price=100
        )
        self.reporters = [
            User.objects.create_user(f"reporter{i}", password="Test-Password-123!")
            for i in range(3)
        ]

    def test_duplicate_and_self_reports_are_rejected(self):
        file_report(reporter=self.reporters[0], target=self.product, reason="충분한 신고 사유")
        with self.assertRaises(ValidationError):
            file_report(reporter=self.reporters[0], target=self.product, reason="중복 신고 사유")
        with self.assertRaises(ValidationError):
            file_report(reporter=self.seller, target=self.product, reason="자기 상품 신고")

    def test_threshold_blocks_product_and_dormants_user(self):
        for reporter in self.reporters:
            file_report(reporter=reporter, target=self.product, reason="악성 상품 신고")
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, Product.Status.BLOCKED)
        self.assertTrue(ModerationAction.objects.filter(action="auto_block_product").exists())
        target = User.objects.create_user("target", password="Test-Password-123!")
        for reporter in self.reporters:
            file_report(reporter=reporter, target=target, reason="악성 사용자 신고")
        target.refresh_from_db()
        self.assertEqual(target.status, User.Status.DORMANT)

    def test_report_view_requires_login_and_validates_reason(self):
        url = reverse("moderation:report_product", args=[self.product.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.reporters[0])
        self.assertEqual(self.client.post(url, {"reason": "짧음"}).status_code, 200)
        self.assertFalse(Report.objects.exists())

    @override_settings(REPORTS_PER_HOUR=2, REPORT_BLOCK_THRESHOLD=99)
    def test_hourly_report_limit_and_inactive_reporter(self):
        targets = [
            Product.objects.create(
                seller=self.seller, title=f"상품 {index}", description="설명", price=100
            )
            for index in range(3)
        ]
        for target in targets[:2]:
            file_report(reporter=self.reporters[0], target=target, reason="정당한 신고 사유")
        with self.assertRaises(ValidationError):
            file_report(reporter=self.reporters[0], target=targets[2], reason="신고 도배 제한 확인")
        self.reporters[1].status = User.Status.BLOCKED
        self.reporters[1].save(update_fields=("status",))
        with self.assertRaises(PermissionDenied):
            file_report(reporter=self.reporters[1], target=targets[2], reason="차단 사용자 신고")


class AdminModerationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", password="Test-Password-123!", is_staff=True)
        self.user = User.objects.create_user("user", password="Test-Password-123!")
        self.product = Product.objects.create(
            seller=self.user, title="상품", description="설명", price=100
        )

    def test_nonstaff_cannot_access_or_call_service(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("moderation:dashboard")).status_code, 403)
        with self.assertRaises(PermissionDenied):
            moderate_target(
                actor=self.user, target=self.product, action="block", reason="권한 없는 제재"
            )

    def test_dashboard_links_report_to_audited_management_flow(self):
        file_report(
            reporter=User.objects.create_user("dashboard-reporter", password="Test-Password-123!"),
            target=self.product,
            reason="관리자 화면 연결 확인",
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse("moderation:dashboard"))
        self.assertContains(
            response,
            reverse("moderation:moderate_product", args=[self.product.pk]),
        )

    def test_admin_action_records_before_after_and_audit(self):
        moderate_target(
            actor=self.admin, target=self.product, action="block", reason="악성 상품 확인"
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, Product.Status.BLOCKED)
        action = ModerationAction.objects.get(actor=self.admin)
        audit = AdminAuditLog.objects.get(actor=self.admin)
        self.assertEqual(action.before, {"status": Product.Status.AVAILABLE})
        self.assertEqual(action.after, {"status": Product.Status.BLOCKED})
        self.assertEqual(audit.reason, "악성 상품 확인")

    def test_admin_can_block_and_restore_user(self):
        moderate_target(actor=self.admin, target=self.user, action="block", reason="반복 악성 행위")
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, User.Status.BLOCKED)
        moderate_target(
            actor=self.admin, target=self.user, action="restore", reason="이의 제기 승인"
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, User.Status.ACTIVE)

    def test_dashboard_lists_users_and_products_for_management(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("moderation:dashboard"))
        self.assertContains(response, reverse("moderation:moderate_user", args=[self.user.pk]))
        self.assertContains(
            response, reverse("moderation:moderate_product", args=[self.product.pk])
        )

    def test_django_admin_cannot_bypass_audited_management(self):
        superuser = User.objects.create_superuser(
            "root-admin", password="Test-Password-123!", email="root@example.com"
        )
        reporter = User.objects.create_user("admin-reporter", password="Test-Password-123!")
        report = file_report(reporter=reporter, target=self.product, reason="관리자 우회 차단 검증")
        self.client.force_login(superuser)
        user_response = self.client.post(
            reverse("admin:users_user_change", args=[self.user.pk]), {"status": "blocked"}
        )
        product_response = self.client.post(
            reverse("admin:products_product_change", args=[self.product.pk]),
            {"status": "blocked"},
        )
        report_response = self.client.post(
            reverse("admin:moderation_report_change", args=[report.pk]),
            {"status": "resolved"},
        )
        self.assertEqual(
            (user_response.status_code, product_response.status_code, report_response.status_code),
            (403, 403, 403),
        )
        self.user.refresh_from_db()
        self.product.refresh_from_db()
        report.refresh_from_db()
        self.assertEqual(self.user.status, User.Status.ACTIVE)
        self.assertEqual(self.product.status, Product.Status.AVAILABLE)
        self.assertEqual(report.status, Report.Status.PENDING)
        self.assertFalse(AdminAuditLog.objects.exists())
