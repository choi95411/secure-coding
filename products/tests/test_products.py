import io
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from products.models import Product

User = get_user_model()


def make_image(name="product.png"):
    stream = io.BytesIO()
    Image.new("RGB", (10, 10), "blue").save(stream, format="PNG")
    return SimpleUploadedFile(name, stream.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProductCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user("alice", password="Strong-Test-Password-123!")
        cls.bob = User.objects.create_user("bob", password="Strong-Test-Password-123!")
        for user in (cls.alice, cls.bob):
            user.profile.display_name = user.username
            user.profile.save()

    def test_create_requires_login(self):
        response = self.client.get(reverse("products:create"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_creates_product_and_valid_image(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            reverse("products:create"),
            {
                "title": "안전한 노트북",
                "description": "정상 상품",
                "price": 1200,
                "status": Product.Status.AVAILABLE,
                "visibility": Product.Visibility.PUBLIC,
                "image": make_image(),
            },
        )
        product = Product.objects.get(title="안전한 노트북")
        self.assertRedirects(response, reverse("products:detail", args=[product.pk]))
        self.assertEqual(product.seller, self.alice)
        self.assertEqual(product.images.count(), 1)

    def test_fake_image_is_rejected(self):
        self.client.force_login(self.alice)
        fake = SimpleUploadedFile("attack.png", b"not an image", content_type="image/png")
        response = self.client.post(
            reverse("products:create"),
            {
                "title": "가짜",
                "description": "파일",
                "price": 10,
                "status": Product.Status.AVAILABLE,
                "visibility": Product.Visibility.PUBLIC,
                "image": fake,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(title="가짜").exists())

    def test_other_user_cannot_update_or_delete_product(self):
        product = Product.objects.create(
            seller=self.alice, title="소유 상품", description="설명", price=100
        )
        self.client.force_login(self.bob)
        update = self.client.post(
            reverse("products:update", args=[product.pk]),
            {
                "title": "탈취",
                "description": "변조",
                "price": 1,
                "status": Product.Status.AVAILABLE,
                "visibility": Product.Visibility.PUBLIC,
            },
        )
        delete = self.client.post(reverse("products:delete", args=[product.pk]))
        self.assertEqual(update.status_code, 403)
        self.assertEqual(delete.status_code, 403)
        product.refresh_from_db()
        self.assertEqual(product.title, "소유 상품")
        self.assertNotEqual(product.status, Product.Status.DELETED)

    def test_delete_is_post_only_and_soft_deletes(self):
        product = Product.objects.create(
            seller=self.alice, title="삭제 상품", description="설명", price=100
        )
        self.client.force_login(self.alice)
        self.assertEqual(
            self.client.get(reverse("products:delete", args=[product.pk])).status_code, 405
        )
        self.assertEqual(
            self.client.post(reverse("products:delete", args=[product.pk])).status_code, 302
        )
        product.refresh_from_db()
        self.assertEqual(product.status, Product.Status.DELETED)
        self.assertIsNotNone(product.deleted_at)

    def test_private_blocked_deleted_products_are_hidden(self):
        private = Product.objects.create(
            seller=self.alice,
            title="비공개",
            description="x",
            price=1,
            visibility=Product.Visibility.PRIVATE,
        )
        blocked = Product.objects.create(
            seller=self.alice, title="차단", description="x", price=1, status=Product.Status.BLOCKED
        )
        deleted = Product.objects.create(
            seller=self.alice, title="삭제", description="x", price=1, status=Product.Status.DELETED
        )
        listing = self.client.get(reverse("products:list"))
        for product in (private, blocked, deleted):
            self.assertNotContains(listing, product.title)
            self.assertEqual(
                self.client.get(reverse("products:detail", args=[product.pk])).status_code, 404
            )

    def test_owner_can_view_private_product(self):
        product = Product.objects.create(
            seller=self.alice,
            title="비공개",
            description="x",
            price=1,
            visibility=Product.Visibility.PRIVATE,
        )
        self.client.force_login(self.alice)
        self.assertEqual(
            self.client.get(reverse("products:detail", args=[product.pk])).status_code, 200
        )


class ProductSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seller = User.objects.create_user("seller", password="Strong-Test-Password-123!")
        seller.profile.display_name = "판매자"
        seller.profile.save()
        Product.objects.create(
            seller=seller,
            title="노트북",
            description="개발용 컴퓨터",
            price=200,
            status=Product.Status.AVAILABLE,
        )
        Product.objects.create(
            seller=seller,
            title="키보드",
            description="노트북용 입력 장치",
            price=100,
            status=Product.Status.SOLD,
        )
        Product.objects.create(
            seller=seller,
            title="숨김 노트북",
            description="노출 금지",
            price=1,
            visibility=Product.Visibility.PRIVATE,
        )

    def test_searches_title_and_description(self):
        response = self.client.get(reverse("products:list"), {"q": "노트북"})
        self.assertContains(response, "노트북")
        self.assertContains(response, "키보드")
        self.assertNotContains(response, "숨김 노트북")

    def test_status_filter_and_price_sort(self):
        response = self.client.get(reverse("products:list"), {"status": Product.Status.SOLD})
        self.assertContains(response, "키보드")
        self.assertNotContains(response, ">노트북</a>", html=False)
        response = self.client.get(reverse("products:list"), {"sort": "price_asc"})
        items = list(response.context["page"].object_list)
        self.assertEqual([item.price for item in items], [100, 200])

    def test_empty_query_is_valid_and_sql_injection_is_data(self):
        self.assertEqual(self.client.get(reverse("products:list"), {"q": ""}).status_code, 200)
        response = self.client.get(reverse("products:list"), {"q": "' OR 1=1 --"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"].paginator.count, 0)

    def test_reflected_xss_is_escaped(self):
        response = self.client.get(reverse("products:list"), {"q": "<script>alert(1)</script>"})
        self.assertNotContains(response, "<script>", html=False)
