from django.contrib import admin
from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for Subject model."""
    list_display = ['code', 'title', 'course', 'units', 'subject_type', 'year_level', 'archived']
    list_filter = ['archived', 'subject_type', 'course', 'year_level']
    search_fields = ['code', 'title']
    ordering = ['code']
    filter_horizontal = ['prerequisites']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']

    fieldsets = (
        ('Subject Information', {
            'fields': ('code', 'title', 'description', 'units', 'subject_type')
        }),
        ('Curriculum', {
            'fields': ('course', 'year_level', 'semester', 'prerequisites')
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
