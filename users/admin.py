from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile


@admin.register(User)
class PlatformUserAdmin(UserAdmin):
    list_display = ("username", "status", "is_staff", "is_active", "date_joined")
    list_filter = ("status", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("플랫폼 상태", {"fields": ("status",)}),)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "updated_at")
    search_fields = ("user__username", "display_name")
