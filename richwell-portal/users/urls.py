# users/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    # Admin Management URLs
    path('admin/courses/', views.courses_management_view, name='courses_list'),
    path('admin/subjects/', views.subjects_management_view, name='subjects_list'),
    path('admin/sections/', views.sections_management_view, name='sections_list'),
    path('admin/students/', views.students_management_view, name='students_list'),

    # Legacy URLs (for backward compatibility)
    path('courses/', views.courses_management_view, name='courses_management'),
    path('subjects/', views.subjects_management_view, name='subjects_management'),
    path('sections/', views.sections_management_view, name='sections_management'),
    path('students/', views.students_management_view, name='students_management'),

    # Other URLs
    path('enrollment/create/', views.placeholder_view, name='enrollment_create'),
    path('my-sections/', views.my_sections_view, name='my_sections'),
    path('grade-encoding/', views.grade_encoding_view, name='grade_encoding'),
    path('my-grades/', views.my_grades_view, name='my_grades'),
    path('my-enrollments/', views.my_enrollments_view, name='my_enrollments'),
    path('analytics/', views.placeholder_view, name='analytics'),
]