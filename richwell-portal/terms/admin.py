from django.contrib import admin
from .models import Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['school_year', 'semester', 'active', 'created_at']
    list_filter = ['semester', 'active', 'created_at']
    search_fields = ['school_year']
    readonly_fields = ['created_at', 'updated_at']
