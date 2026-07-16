import django.db.models.deletion
import products.models
import products.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(db_index=True, max_length=120)),
                ("description", models.TextField(max_length=3000)),
                ("price", models.PositiveBigIntegerField()),
                ("status", models.CharField(choices=[("draft", "임시 저장"), ("available", "판매 중"), ("reserved", "예약 중"), ("sold", "판매 완료"), ("blocked", "차단"), ("deleted", "삭제")], db_index=True, default="available", max_length=16)),
                ("visibility", models.CharField(choices=[("public", "공개"), ("private", "비공개")], db_index=True, default="public", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("seller", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to=products.models.product_image_path, validators=[products.validators.validate_product_image])),
                ("alt_text", models.CharField(blank=True, max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="products.product")),
            ],
            options={"ordering": ("id",)},
        ),
        migrations.AddConstraint(model_name="product", constraint=models.CheckConstraint(condition=models.Q(("price__gte", 0)), name="product_price_nonnegative")),
        migrations.AddIndex(model_name="product", index=models.Index(fields=["visibility", "status", "-created_at"], name="product_public_recent_idx")),
        migrations.AddIndex(model_name="product", index=models.Index(fields=["seller", "status"], name="product_seller_status_idx")),
    ]
