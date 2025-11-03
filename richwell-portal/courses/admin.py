from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model."""
    list_display = ['code', 'title', 'years', 'archived', 'created_at']
    list_filter = ['archived', 'years']
    search_fields = ['code', 'title']
    ordering = ['code']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']

    fieldsets = (
        ('Course Information', {
            'fields': ('code', 'title', 'description', 'years')
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
