from django.contrib import admin
from .models import AuditTrail


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'table_name', 'record_id', 'timestamp']
    list_filter = ['action', 'table_name', 'timestamp']
    search_fields = ['actor__username', 'table_name', 'record_id']
    readonly_fields = ['actor', 'action', 'table_name', 'record_id', 'old_value', 'new_value', 'timestamp', 'ip_address', 'user_agent']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
