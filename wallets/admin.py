from django.contrib import admin

from .models import LedgerEntry, Transfer, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")
    readonly_fields = ("user", "balance", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "recipient", "amount", "status", "created_at")
    readonly_fields = tuple(field.name for field in Transfer._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("wallet", "direction", "amount", "balance_after", "created_at")
    readonly_fields = tuple(field.name for field in LedgerEntry._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
