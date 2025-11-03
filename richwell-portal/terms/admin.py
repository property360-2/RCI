from django.contrib import admin
from .models import Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """Admin interface for Term model."""
    list_display = ['school_year', 'semester', 'active', 'start_date', 'end_date', 'created_at']
    list_filter = ['active', 'semester', 'school_year']
    search_fields = ['school_year']
    ordering = ['-school_year', '-semester']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Term Information', {
            'fields': ('school_year', 'semester', 'active')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
