from django.contrib import admin

from .models import AdminAuditLog, ModerationAction, Report

admin.site.register(Report)
admin.site.register(ModerationAction)


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "target_type", "target_id", "created_at")
    readonly_fields = tuple(field.name for field in AdminAuditLog._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
