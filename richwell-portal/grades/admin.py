from django.contrib import admin
from .models import GradeRecord, INCRecord


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    """Admin interface for GradeRecord model."""
    list_display = ['enrollment', 'grade', 'encoded_by', 'encoded_at', 'archived']
    list_filter = ['archived', 'grade', 'encoded_at']
    search_fields = ['enrollment__student__student_id', 'enrollment__subject__code']
    ordering = ['-encoded_at']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by', 'encoded_at']

    fieldsets = (
        ('Grade Information', {
            'fields': ('enrollment', 'grade', 'remarks')
        }),
        ('Encoding', {
            'fields': ('encoded_by', 'encoded_at')
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


@admin.register(INCRecord)
class INCRecordAdmin(admin.ModelAdmin):
    """Admin interface for INCRecord model."""
    list_display = ['enrollment', 'deadline', 'resolved_at', 'expired', 'confirmed_by']
    list_filter = ['expired', 'deadline', 'resolved_at']
    search_fields = ['enrollment__student__student_id', 'enrollment__subject__code']
    ordering = ['deadline']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('INC Information', {
            'fields': ('enrollment', 'deadline', 'expired')
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolution_note', 'confirmed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
