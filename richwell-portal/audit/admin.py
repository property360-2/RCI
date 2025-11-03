from django.contrib import admin
from .models import AuditTrail


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    """
    Admin interface for AuditTrail model.
    Read-only to preserve audit integrity.
    """
    list_display = ['timestamp', 'actor', 'action', 'table_name', 'record_id']
    list_filter = ['action', 'table_name', 'timestamp']
    search_fields = ['actor__username', 'table_name', 'record_id']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    # Make all fields read-only
    readonly_fields = [
        'actor', 'action', 'table_name', 'record_id',
        'old_value', 'new_value', 'timestamp', 'ip_address', 'user_agent'
    ]

    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent modification of audit logs."""
        return False
