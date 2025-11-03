# users/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Placeholder URLs (will implement later)
    path('courses/', views.placeholder_view, name='courses_list'),
    path('subjects/', views.placeholder_view, name='subjects_list'),
    path('sections/', views.placeholder_view, name='sections_list'),
    path('enrollment/create/', views.placeholder_view, name='enrollment_create'),
    path('students/', views.placeholder_view, name='students_list'),
    path('my-sections/', views.placeholder_view, name='my_sections'),
    path('grade-encoding/', views.placeholder_view, name='grade_encoding'),
    path('my-grades/', views.placeholder_view, name='my_grades'),
    path('my-enrollments/', views.placeholder_view, name='my_enrollments'),
    path('analytics/', views.placeholder_view, name='analytics'),
]