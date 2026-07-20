from django.contrib import admin

from .models import AdminAuditLog, ModerationAction, Report


class ReadOnlyAuditAdmin(admin.ModelAdmin):
    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Report)
class ReportAdmin(ReadOnlyAuditAdmin):
    list_display = ("id", "reporter", "status", "target_user", "target_product", "created_at")
    list_filter = ("status",)


@admin.register(ModerationAction)
class ModerationActionAdmin(ReadOnlyAuditAdmin):
    list_display = ("actor", "action", "target_type", "target_id", "created_at")


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(ReadOnlyAuditAdmin):
    list_display = ("actor", "action", "target_type", "target_id", "created_at")
