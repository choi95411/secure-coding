import uuid
from pathlib import Path

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_product_image


class ProductQuerySet(models.QuerySet):
    def publicly_visible(self):
        return self.filter(visibility=Product.Visibility.PUBLIC).exclude(
            status__in=[Product.Status.BLOCKED, Product.Status.DELETED, Product.Status.DRAFT]
        )


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "임시 저장"
        AVAILABLE = "available", "판매 중"
        RESERVED = "reserved", "예약 중"
        SOLD = "sold", "판매 완료"
        BLOCKED = "blocked", "차단"
        DELETED = "deleted", "삭제"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "공개"
        PRIVATE = "private", "비공개"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="products"
    )
    title = models.CharField(max_length=120, db_index=True)
    description = models.TextField(max_length=3000)
    price = models.PositiveBigIntegerField(validators=[MinValueValidator(0)])
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.AVAILABLE, db_index=True
    )
    visibility = models.CharField(
        max_length=16, choices=Visibility.choices, default=Visibility.PUBLIC, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="product_price_nonnegative"
            )
        ]
        indexes = [
            models.Index(
                fields=("visibility", "status", "-created_at"), name="product_public_recent_idx"
            ),
            models.Index(fields=("seller", "status"), name="product_seller_status_idx"),
        ]

    def __str__(self):
        return self.title


def product_image_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"products/{instance.product_id}/{uuid.uuid4().hex}{suffix}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_image_path, validators=[validate_product_image])
    alt_text = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.product}: {self.image.name}"
