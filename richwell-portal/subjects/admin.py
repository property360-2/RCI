from django.contrib import admin
from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "units", "year_level", "course", "archived")
    search_fields = ("code", "name")
    list_filter = ("course", "year_level", "archived")
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']
    filter_horizontal = ['prerequisites']
