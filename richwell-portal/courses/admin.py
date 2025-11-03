from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'archived', 'created_at']
    list_filter = ['archived', 'created_at']
    search_fields = ['code', 'title']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']
