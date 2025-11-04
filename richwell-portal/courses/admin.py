from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'total_units', 'years_to_complete', 'archived', 'created_at']
    list_filter = ['archived', 'years_to_complete', 'created_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']
