from django.contrib import admin
from .models import Section, AssignedSubject


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Admin interface for Section model."""
    list_display = ['code', 'course', 'term', 'year_level', 'capacity', 'slots_remaining', 'adviser', 'archived']
    list_filter = ['archived', 'course', 'term', 'year_level']
    search_fields = ['code', 'course__code', 'adviser__username']
    ordering = ['course', 'year_level', 'code']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']

    fieldsets = (
        ('Section Information', {
            'fields': ('code', 'course', 'term', 'year_level')
        }),
        ('Capacity', {
            'fields': ('capacity', 'slots_remaining')
        }),
        ('Personnel', {
            'fields': ('adviser',)
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


@admin.register(AssignedSubject)
class AssignedSubjectAdmin(admin.ModelAdmin):
    """Admin interface for AssignedSubject model."""
    list_display = ['subject', 'section', 'professor', 'archived']
    list_filter = ['archived', 'section__term', 'section__course']
    search_fields = ['subject__code', 'section__code', 'professor__username']
    ordering = ['section', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']

    fieldsets = (
        ('Assignment Information', {
            'fields': ('section', 'subject', 'professor')
        }),
        ('Schedule', {
            'fields': ('schedule',)
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
