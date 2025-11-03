# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with role and archive fields
    """
    list_display = ['username', 'email', 'role', 'is_active', 'archived', 'created_at']
    list_filter = ['role', 'is_active', 'archived', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Status', {
            'fields': ('role',)
        }),
        ('Archive Info', {
            'fields': ('archived', 'archived_at', 'archived_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']
    
    def get_queryset(self, request):
        """Include archived users in admin"""
        return super().get_queryset(request).select_related('archived_by')