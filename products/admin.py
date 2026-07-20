from django.contrib import admin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    can_delete = False
    readonly_fields = tuple(field.name for field in ProductImage._meta.fields)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "price", "status", "visibility", "created_at")
    list_filter = ("status", "visibility")
    search_fields = ("title", "description", "seller__username")
    readonly_fields = tuple(field.name for field in Product._meta.fields)
    inlines = (ProductImageInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
