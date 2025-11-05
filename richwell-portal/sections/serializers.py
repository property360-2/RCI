"""
Section Serializers

This module provides serializers for the Section and AssignedSubject models.
"""

from rest_framework import serializers
from .models import Section, AssignedSubject


class AssignedSubjectSerializer(serializers.ModelSerializer):
    """Serializer for AssignedSubject model."""

    professor_name = serializers.CharField(source='professor.get_full_name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_units = serializers.IntegerField(source='subject.units', read_only=True)

    class Meta:
        model = AssignedSubject
        fields = [
            'id',
            'section',
            'subject',
            'subject_code',
            'subject_name',
            'subject_units',
            'professor',
            'professor_name',
            'schedule',
            'room',
            'archived',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Section model.

    Provides full CRUD operations for sections via REST API.
    """

    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    term_name = serializers.CharField(source='term.__str__', read_only=True)

    class Meta:
        model = Section
        fields = [
            'id',
            'code',
            'course',
            'course_code',
            'course_name',
            'term',
            'term_name',
            'capacity',
            'slots_remaining',
            'archived',
            'archived_at',
            'archived_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'archived_at', 'archived_by']


class SectionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for section list views.
    """

    course_code = serializers.CharField(source='course.code', read_only=True)
    term_name = serializers.CharField(source='term.__str__', read_only=True)
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id',
            'code',
            'course_code',
            'term_name',
            'capacity',
            'slots_remaining',
            'enrollment_count',
            'archived'
        ]

    def get_enrollment_count(self, obj):
        """Get count of enrolled students."""
        return obj.capacity - obj.slots_remaining


class SectionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for section detail views with assigned subjects.
    """

    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    term_name = serializers.CharField(source='term.__str__', read_only=True)
    assigned_subjects = AssignedSubjectSerializer(many=True, read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    total_units = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id',
            'code',
            'course',
            'course_code',
            'course_name',
            'term',
            'term_name',
            'capacity',
            'slots_remaining',
            'enrollment_count',
            'total_units',
            'assigned_subjects',
            'archived',
            'created_at',
            'updated_at',
        ]

    def get_enrollment_count(self, obj):
        """Get count of enrolled students."""
        return obj.get_enrollment_count()

    def get_total_units(self, obj):
        """Get total units for this section."""
        return obj.get_total_units()
