from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""
    list_display = ['student_id', 'user', 'course', 'year_level', 'status', 'archived']
    list_filter = ['archived', 'status', 'course', 'year_level']
    search_fields = ['student_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['student_id']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']

    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'student_id', 'course', 'year_level', 'status')
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'address')
        }),
        ('Dates', {
            'fields': ('date_enrolled', 'date_graduated')
        }),
        ('Documents', {
            'fields': ('documents',),
            'classes': ('collapse',)
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
