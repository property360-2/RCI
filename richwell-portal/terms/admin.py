from django.contrib import admin
from .models import Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'term_start', 'term_end', 'created_at']
    list_filter = ['is_active', 'archived', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']
