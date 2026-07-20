from django.contrib import admin

from .models import LoginThrottle


@admin.register(LoginThrottle)
class LoginThrottleAdmin(admin.ModelAdmin):
    list_display = ("identifier_hash", "failures", "locked_until", "updated_at")
    readonly_fields = (
        "identifier_hash",
        "failures",
        "window_started_at",
        "locked_until",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False
