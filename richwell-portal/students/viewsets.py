"""
Student ViewSets

This module provides REST API viewsets for Student operations.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Student
from .serializers import (
    StudentSerializer,
    StudentListSerializer,
    StudentDetailSerializer
)


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student CRUD operations via REST API.

    Provides:
    - list: Get all students
    - retrieve: Get a specific student
    - create: Create a new student
    - update: Update a student
    - partial_update: Partially update a student
    - destroy: Archive a student (soft delete)
    - restore: Restore an archived student

    Permissions:
    - DEAN: Full read access
    - REGISTRAR: Full read/write access
    - ADMISSION: Create students, read access
    - PROFESSOR: Read access to students in their sections
    - STUDENT: Read access to own profile only
    - ADMIN: Full access
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['archived', 'student_id', 'course', 'status', 'year_level']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['student_id', 'created_at', 'year_level']
    ordering = ['student_id']

    def get_queryset(self):
        """
        Get queryset based on user role.

        - STUDENT: Only own profile
        - PROFESSOR: Students in their sections
        - DEAN, REGISTRAR, ADMISSION, ADMIN: All students
        """
        queryset = Student.objects.select_related('user', 'course').all()

        # Role-based filtering
        if self.request.user.role == 'STUDENT':
            # Students can only see their own profile
            queryset = queryset.filter(user=self.request.user)
        elif self.request.user.role == 'PROFESSOR':
            # Professors can see students in their sections
            # TODO: Implement section-based filtering
            pass
        elif not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMISSION', 'ADMIN']:
            # Filter archived students for other roles
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
            return StudentListSerializer
        elif self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer

    def perform_create(self, serializer):
        """Create a new student."""
        # Only REGISTRAR, ADMISSION, and ADMIN can create students
        if not self.request.user.role in ['REGISTRAR', 'ADMISSION', 'ADMIN']:
            raise serializers.ValidationError(
                'You do not have permission to create students.'
            )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Soft delete (archive) instead of hard delete.
        """
        if not self.request.user.role in ['REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to archive students.'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.archive(archived_by=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restore an archived student.

        POST /api/students/{id}/restore/
        """
        if not self.request.user.role in ['REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to restore students.'},
                status=status.HTTP_403_FORBIDDEN
            )

        student = self.get_object()

        if not student.archived:
            return Response(
                {'error': 'This student is not archived.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        student.restore()
        serializer = self.get_serializer(student)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """
        Get all enrollments for this student.

        GET /api/students/{id}/enrollments/
        """
        student = self.get_object()
        enrollments = student.get_current_enrollments()

        # Import here to avoid circular import
        from enrollments.serializers import EnrollmentSerializer

        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """
        Get all grades for this student.

        GET /api/students/{id}/grades/
        """
        student = self.get_object()
        grades = student.get_grades()

        # Import here to avoid circular import
        from grades.serializers import GradeRecordSerializer

        serializer = GradeRecordSerializer(grades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        """
        Get complete transcript for this student.

        GET /api/students/{id}/transcript/
        """
        student = self.get_object()
        transcript = student.get_transcript()
        return Response(transcript)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall student statistics.

        GET /api/students/statistics/
        """
        total_students = Student.objects.filter(archived=False).count()
        archived_students = Student.objects.filter(archived=True).count()
        active_students = Student.objects.filter(
            archived=False,
            status=Student.Status.ACTIVE
        ).count()

        return Response({
            'total_students': total_students,
            'archived_students': archived_students,
            'active_students': active_students,
        })
