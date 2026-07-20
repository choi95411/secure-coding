import uuid

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from chat.models import Conversation
from moderation.models import AdminAuditLog, Report
from moderation.services import file_report, moderate_target
from products.models import Product
from wallets.models import Transfer
from wallets.services import transfer_points

User = get_user_model()


class CoreUserJourneyIntegrationTest(TestCase):
    password = "Integration-Password-123!"

    def signup(self, client, username, display_name):
        response = client.post(
            reverse("users:signup"),
            {
                "username": username,
                "display_name": display_name,
                "password1": self.password,
                "password2": self.password,
            },
        )
        self.assertRedirects(response, reverse("users:login"))
        return User.objects.get(username=username)

    def test_product_chat_transfer_report_and_admin_sanction_flow(self):
        alice_client, bob_client = Client(), Client()
        alice = self.signup(alice_client, "alice-flow", "앨리스")
        bob = self.signup(bob_client, "bob-flow", "밥")

        self.assertTrue(alice_client.login(username=alice.username, password=self.password))
        create = alice_client.post(
            reverse("products:create"),
            {
                "title": "통합 테스트 노트북",
                "description": "안전한 상품 설명",
                "price": 1500,
                "status": Product.Status.AVAILABLE,
                "visibility": Product.Visibility.PUBLIC,
            },
        )
        product = Product.objects.get(title="통합 테스트 노트북")
        self.assertRedirects(create, reverse("products:detail", args=[product.pk]))

        self.assertTrue(bob_client.login(username=bob.username, password=self.password))
        search = bob_client.get(reverse("products:list"), {"q": "노트북"})
        self.assertContains(search, product.title)
        self.assertEqual(
            bob_client.get(reverse("products:detail", args=[product.pk])).status_code,
            200,
        )

        direct = bob_client.post(reverse("chat:direct_start", args=[alice.username]))
        conversation = Conversation.objects.get(kind=Conversation.Kind.DIRECT)
        self.assertRedirects(direct, reverse("chat:detail", args=[conversation.pk]))

        transfer = transfer_points(
            sender=bob,
            recipient=alice,
            amount=500,
            idempotency_key=uuid.uuid4(),
        ).transfer
        self.assertEqual(transfer.status, Transfer.Status.SUCCEEDED)
        alice.wallet.refresh_from_db()
        bob.wallet.refresh_from_db()
        self.assertEqual((alice.wallet.balance, bob.wallet.balance), (10_500, 9_500))

        file_report(reporter=bob, target=product, reason="관리자 확인이 필요한 상품")
        self.assertEqual(Report.objects.filter(target_product=product).count(), 1)

        admin = User.objects.create_user("admin-flow", password=self.password, is_staff=True)
        self.assertEqual(bob_client.get(reverse("moderation:dashboard")).status_code, 403)
        moderate_target(
            actor=admin,
            target=product,
            action="block",
            reason="통합 테스트 관리자 차단",
        )
        product.refresh_from_db()
        self.assertEqual(product.status, Product.Status.BLOCKED)
        self.assertTrue(
            AdminAuditLog.objects.filter(actor=admin, target_id=str(product.pk)).exists()
        )
