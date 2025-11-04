"""
Course ViewSets

This module provides REST API viewsets for Course operations.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Course
from .serializers import CourseSerializer, CourseListSerializer, CourseDetailSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course CRUD operations via REST API.

    Provides:
    - list: Get all courses
    - retrieve: Get a specific course
    - create: Create a new course
    - update: Update a course
    - partial_update: Partially update a course
    - destroy: Archive a course (soft delete)
    - restore: Restore an archived course

    Permissions:
    - DEAN, REGISTRAR, ADMISSION: Read access
    - DEAN, REGISTRAR: Write access
    - ADMIN: Full access
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['archived', 'code']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        """
        Get queryset based on user role.

        - Regular users: Only active courses
        - DEAN, REGISTRAR, ADMIN: All courses (including archived)
        """
        queryset = Course.objects.all()

        # Filter archived courses unless user has permission
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            queryset = queryset.filter(archived=False)

        # Allow filtering by archived status via query param
        archived = self.request.query_params.get('archived', None)
        if archived is not None:
            queryset = queryset.filter(archived=archived.lower() == 'true')

        return queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return CourseListSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        """Create a new course."""
        serializer.save()

    def perform_destroy(self, instance):
        """
        Soft delete (archive) instead of hard delete.
        """
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to archive courses.'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.archive(archived_by=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restore an archived course.

        POST /api/courses/{id}/restore/
        """
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to restore courses.'},
                status=status.HTTP_403_FORBIDDEN
            )

        course = self.get_object()

        if not course.archived:
            return Response(
                {'error': 'This course is not archived.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course.restore()
        serializer = self.get_serializer(course)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """
        Get all subjects for a specific course.

        GET /api/courses/{id}/subjects/
        """
        course = self.get_object()
        subjects = course.subjects.filter(archived=False)

        # Import here to avoid circular import
        from subjects.serializers import SubjectListSerializer

        serializer = SubjectListSerializer(subjects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students enrolled in a specific course.

        GET /api/courses/{id}/students/
        """
        course = self.get_object()
        students = course.students.filter(archived=False)

        # Import here to avoid circular import
        from students.serializers import StudentListSerializer

        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall course statistics.

        GET /api/courses/statistics/
        """
        total_courses = Course.objects.filter(archived=False).count()
        archived_courses = Course.objects.filter(archived=True).count()

        return Response({
            'total_courses': total_courses,
            'archived_courses': archived_courses,
            'active_courses': total_courses,
        })
