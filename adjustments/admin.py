from django.contrib import admin

from .models import WalletAdjustment


@admin.register(WalletAdjustment)
class WalletAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("wallet", "amount", "actor", "created_at")
    readonly_fields = tuple(field.name for field in WalletAdjustment._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
