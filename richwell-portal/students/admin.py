from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'course', 'status', 'year_level', 'archived']
    list_filter = ['status', 'year_level', 'archived', 'course']
    search_fields = ['student_id', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'archived_at', 'archived_by']
