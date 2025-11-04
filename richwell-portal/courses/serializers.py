"""
Course Serializers

This module provides serializers for the Course model to enable REST API functionality.
"""

from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model.

    Provides full CRUD operations for courses via REST API.
    """

    total_subjects = serializers.IntegerField(read_only=True)
    total_units = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'code',
            'name',
            'description',
            'total_units',
            'total_subjects',
            'archived',
            'archived_at',
            'archived_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'archived_at', 'archived_by']


class CourseListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for course list views.
    """

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'total_units', 'archived']


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for course detail views with related subjects.
    """

    subjects_count = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'code',
            'name',
            'description',
            'total_units',
            'subjects_count',
            'students_count',
            'archived',
            'created_at',
            'updated_at',
        ]

    def get_subjects_count(self, obj):
        """Get count of subjects in this course."""
        return obj.subjects.filter(archived=False).count()

    def get_students_count(self, obj):
        """Get count of students enrolled in this course."""
        return obj.students.filter(archived=False).count()
