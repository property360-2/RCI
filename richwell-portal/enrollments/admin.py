from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for Enrollment model."""
    list_display = ['student', 'subject', 'section', 'term', 'status', 'units', 'archived']
    list_filter = ['archived', 'status', 'term', 'section__course']
    search_fields = ['student__student_id', 'subject__code', 'section__code']
    ordering = ['-term', 'student']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']

    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'subject', 'section', 'term', 'units')
        }),
        ('Status', {
            'fields': ('status', 'enrolled_by')
        }),
        ('Archive Status', {
            'fields': ('archived', 'archived_at', 'archived_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
