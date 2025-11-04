"""
Student Serializers

This module provides serializers for the Student model to enable REST API functionality.
"""

from rest_framework import serializers
from .models import Student
from users.models import User


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Student model.
    """

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'username',
            'email',
            'full_name',
            'student_id',
            'course',
            'course_name',
            'course_code',
            'year_level',
            'status',
            'enrollment_date',
            'documents',
            'archived',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'archived_at', 'archived_by']

    def get_full_name(self, obj):
        """Get student's full name from user."""
        return obj.user.get_full_name()


class StudentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for student list views.
    """

    full_name = serializers.SerializerMethodField()
    course_code = serializers.CharField(source='course.code', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'full_name', 'course_code', 'year_level', 'status']

    def get_full_name(self, obj):
        """Get student's full name."""
        return obj.user.get_full_name()


class StudentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for student detail views.
    """

    user_details = serializers.SerializerMethodField()
    course_details = serializers.SerializerMethodField()
    enrollments_count = serializers.SerializerMethodField()
    total_units = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'user_details',
            'student_id',
            'course_details',
            'year_level',
            'status',
            'enrollment_date',
            'enrollments_count',
            'total_units',
            'documents',
            'archived',
            'created_at',
            'updated_at',
        ]

    def get_user_details(self, obj):
        """Get user information."""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'full_name': obj.user.get_full_name(),
        }

    def get_course_details(self, obj):
        """Get course information."""
        return {
            'id': obj.course.id,
            'code': obj.course.code,
            'name': obj.course.name,
            'total_units': obj.course.total_units,
        }

    def get_enrollments_count(self, obj):
        """Get count of student's enrollments."""
        return obj.enrollments.filter(archived=False).count()

    def get_total_units(self, obj):
        """Get total units enrolled by student."""
        # TODO: Calculate from current term enrollments
        return 0


class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new students.
    """

    # User fields
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Student
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'student_id',
            'course',
            'year_level',
            'status',
            'enrollment_date',
            'documents',
        ]

    def create(self, validated_data):
        """Create user and student together."""
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'password': validated_data.pop('password'),
            'role': 'STUDENT',
        }

        # Create user
        user = User.objects.create_user(**user_data)

        # Create student
        student = Student.objects.create(user=user, **validated_data)

        return student
