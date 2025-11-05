"""
API URL Configuration

This module configures all REST API endpoints using Django REST Framework routers.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import viewsets
from courses.viewsets import CourseViewSet
from subjects.viewsets import SubjectViewSet
from sections.viewsets import SectionViewSet, AssignedSubjectViewSet
from students.viewsets import StudentViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'assigned-subjects', AssignedSubjectViewSet, basename='assigned-subject')
router.register(r'students', StudentViewSet, basename='student')

# URL patterns
urlpatterns = [
    # JWT Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API router endpoints
    path('', include(router.urls)),
]
