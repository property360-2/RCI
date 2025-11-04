"""
Subject Serializers

This module provides serializers for the Subject model to enable REST API functionality.
"""

from rest_framework import serializers
from .models import Subject
from courses.serializers import CourseListSerializer


class SubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Subject model.

    Provides full CRUD operations for subjects via REST API.
    """

    course_name = serializers.CharField(source='course.name', read_only=True)
    prerequisite_names = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id',
            'code',
            'name',
            'description',
            'units',
            'course',
            'course_name',
            'prerequisites',
            'prerequisite_names',
            'archived',
            'archived_at',
            'archived_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'archived_at', 'archived_by']

    def get_prerequisite_names(self, obj):
        """Get names of prerequisite subjects."""
        return [f"{prereq.code} - {prereq.name}" for prereq in obj.prerequisites.all()]


class SubjectListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for subject list views.
    """

    course_code = serializers.CharField(source='course.code', read_only=True)
    prerequisites_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'units', 'course_code', 'prerequisites_count', 'archived']

    def get_prerequisites_count(self, obj):
        """Get count of prerequisites."""
        return obj.prerequisites.count()


class SubjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for subject detail views.
    """

    course = CourseListSerializer(read_only=True)
    prerequisites = SubjectListSerializer(many=True, read_only=True)
    sections_count = serializers.SerializerMethodField()
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id',
            'code',
            'name',
            'description',
            'units',
            'course',
            'prerequisites',
            'sections_count',
            'enrollments_count',
            'archived',
            'created_at',
            'updated_at',
        ]

    def get_sections_count(self, obj):
        """Get count of sections for this subject."""
        return obj.sections.filter(archived=False).count()

    def get_enrollments_count(self, obj):
        """Get count of total enrollments across all sections."""
        return sum(section.enrollments.count() for section in obj.sections.filter(archived=False))


class SubjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating subjects.
    """

    class Meta:
        model = Subject
        fields = ['code', 'name', 'description', 'units', 'course', 'prerequisites']

    def validate_units(self, value):
        """Validate units are within acceptable range."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Units must be between 1 and 5.")
        return value

    def validate_prerequisites(self, value):
        """Validate prerequisites don't create circular dependencies."""
        # TODO: Implement circular dependency check
        return value
