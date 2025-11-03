from django.contrib import admin
from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'course', 'units', 'subject_type', 'archived']
    list_filter = ['subject_type', 'archived', 'course']
    search_fields = ['code', 'title']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']
    filter_horizontal = ['prerequisites']
