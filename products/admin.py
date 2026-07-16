from django.contrib import admin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "price", "status", "visibility", "created_at")
    list_filter = ("status", "visibility")
    search_fields = ("title", "description", "seller__username")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    inlines = (ProductImageInline,)
