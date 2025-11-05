"""
Section ViewSets

This module provides REST API viewsets for Section operations.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Section, AssignedSubject
from .serializers import (
    SectionSerializer,
    SectionListSerializer,
    SectionDetailSerializer,
    AssignedSubjectSerializer
)


class SectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Section CRUD operations via REST API.

    Provides:
    - list: Get all sections
    - retrieve: Get a specific section
    - create: Create a new section
    - update: Update a section
    - partial_update: Partially update a section
    - destroy: Archive a section (soft delete)
    - restore: Restore an archived section

    Permissions:
    - DEAN, REGISTRAR, ADMISSION: Read access
    - DEAN, REGISTRAR: Write access
    - ADMIN: Full access
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['archived', 'code', 'course', 'term']
    search_fields = ['code']
    ordering_fields = ['code', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        """
        Get queryset based on user role.

        - Regular users: Only active sections
        - DEAN, REGISTRAR, ADMIN: All sections (including archived)
        """
        queryset = Section.objects.select_related('course', 'term').all()

        # Filter archived sections unless user has permission
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
            return SectionListSerializer
        elif self.action == 'retrieve':
            return SectionDetailSerializer
        return SectionSerializer

    def perform_create(self, serializer):
        """Create a new section."""
        serializer.save()

    def perform_destroy(self, instance):
        """
        Soft delete (archive) instead of hard delete.
        """
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to archive sections.'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.archive(archived_by=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restore an archived section.

        POST /api/sections/{id}/restore/
        """
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to restore sections.'},
                status=status.HTTP_403_FORBIDDEN
            )

        section = self.get_object()

        if not section.archived:
            return Response(
                {'error': 'This section is not archived.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        section.restore()
        serializer = self.get_serializer(section)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students enrolled in this section.

        GET /api/sections/{id}/students/
        """
        section = self.get_object()
        students = section.get_enrolled_students()

        # Import here to avoid circular import
        from students.serializers import StudentListSerializer

        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def assigned_subjects(self, request, pk=None):
        """
        Get all subjects assigned to this section.

        GET /api/sections/{id}/assigned_subjects/
        """
        section = self.get_object()
        assigned_subjects = section.get_assigned_subjects()

        serializer = AssignedSubjectSerializer(assigned_subjects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall section statistics.

        GET /api/sections/statistics/
        """
        total_sections = Section.objects.filter(archived=False).count()
        archived_sections = Section.objects.filter(archived=True).count()

        return Response({
            'total_sections': total_sections,
            'archived_sections': archived_sections,
            'active_sections': total_sections,
        })


class AssignedSubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AssignedSubject CRUD operations.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AssignedSubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['archived', 'section', 'subject', 'professor']
    ordering_fields = ['section', 'created_at']
    ordering = ['section']

    def get_queryset(self):
        """Get queryset based on user role."""
        queryset = AssignedSubject.objects.select_related(
            'section', 'subject', 'professor'
        ).all()

        # Filter archived unless user has permission
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN', 'PROFESSOR']:
            queryset = queryset.filter(archived=False)

        return queryset

    def perform_destroy(self, instance):
        """Soft delete (archive) instead of hard delete."""
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to archive assigned subjects.'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.archive(archived_by=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
