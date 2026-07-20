from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile


class ReadOnlyAdminMixin:
    """Keep Django admin useful for inspection without bypassing audited workflows."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class PlatformUserAdmin(ReadOnlyAdminMixin, UserAdmin):
    list_display = ("username", "status", "is_staff", "is_active", "date_joined")
    list_filter = ("status", "is_staff", "is_active")
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets + (("플랫폼 상태", {"fields": ("status",)}),)


@admin.register(UserProfile)
class UserProfileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "display_name", "updated_at")
    search_fields = ("user__username", "display_name")
