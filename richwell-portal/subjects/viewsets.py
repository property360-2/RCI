"""
Subject ViewSets

This module provides REST API viewsets for Subject operations.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Subject
from .serializers import (
    SubjectSerializer,
    SubjectListSerializer,
    SubjectDetailSerializer,
    SubjectCreateUpdateSerializer
)


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subject CRUD operations via REST API.

    Provides standard CRUD operations plus custom actions:
    - sections: Get all sections for a subject
    - prerequisites: Get prerequisites for a subject
    - check_prerequisites: Check if student meets prerequisites
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['archived', 'course', 'units']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'units', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        """
        Get queryset based on user role and filters.
        """
        queryset = Subject.objects.select_related('course').prefetch_related('prerequisites')

        # Filter archived subjects unless user has permission
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
            return SubjectListSerializer
        elif self.action == 'retrieve':
            return SubjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SubjectCreateUpdateSerializer
        return SubjectSerializer

    def perform_destroy(self, instance):
        """
        Soft delete (archive) instead of hard delete.
        """
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to archive subjects.'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.archive(archived_by=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restore an archived subject.

        POST /api/subjects/{id}/restore/
        """
        if not self.request.user.role in ['DEAN', 'REGISTRAR', 'ADMIN']:
            return Response(
                {'error': 'You do not have permission to restore subjects.'},
                status=status.HTTP_403_FORBIDDEN
            )

        subject = self.get_object()

        if not subject.archived:
            return Response(
                {'error': 'This subject is not archived.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subject.restore()
        serializer = self.get_serializer(subject)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        """
        Get all sections for a specific subject.

        GET /api/subjects/{id}/sections/
        """
        subject = self.get_object()
        sections = subject.sections.filter(archived=False)

        # Import here to avoid circular import
        from sections.serializers import SectionListSerializer

        serializer = SectionListSerializer(sections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def prerequisites(self, request, pk=None):
        """
        Get all prerequisites for a specific subject.

        GET /api/subjects/{id}/prerequisites/
        """
        subject = self.get_object()
        prerequisites = subject.prerequisites.all()

        serializer = SubjectListSerializer(prerequisites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_prerequisites(self, request, pk=None):
        """
        Check if a student meets prerequisites for this subject.

        POST /api/subjects/{id}/check_prerequisites/
        Body: {"student_id": 123}
        """
        subject = self.get_object()
        student_id = request.data.get('student_id')

        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement prerequisite checking logic
        # This would check if student has passed all prerequisite subjects

        return Response({
            'meets_prerequisites': True,
            'missing_prerequisites': []
        })
