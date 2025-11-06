"""
Custom permission classes for Role-Based Access Control (RBAC).

These permissions replace inline permission checks in viewsets
and provide a more maintainable and testable permission system.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to Admin users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsDean(permissions.BasePermission):
    """Allow access only to Dean users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'DEAN'
        )


class IsRegistrar(permissions.BasePermission):
    """Allow access only to Registrar users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'REGISTRAR'
        )


class IsAdmission(permissions.BasePermission):
    """Allow access only to Admission users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMISSION'
        )


class IsProfessor(permissions.BasePermission):
    """Allow access only to Professor users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'PROFESSOR'
        )


class IsStudent(permissions.BasePermission):
    """Allow access only to Student users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'STUDENT'
        )


class IsAdminOrDeanOrRegistrar(permissions.BasePermission):
    """Allow access to Admin, Dean, or Registrar users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['ADMIN', 'DEAN', 'REGISTRAR']
        )


class IsAdminOrRegistrar(permissions.BasePermission):
    """Allow access to Admin or Registrar users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['ADMIN', 'REGISTRAR']
        )


class IsRegistrarOrAdmission(permissions.BasePermission):
    """Allow access to Registrar or Admission users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['REGISTRAR', 'ADMISSION']
        )


class CanManageStudents(permissions.BasePermission):
    """
    Allow Admin, Registrar, or Admission to manage students.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Read-only for everyone authenticated
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write access for specific roles
        return request.user.role in ['ADMIN', 'REGISTRAR', 'ADMISSION']


class CanManageCourses(permissions.BasePermission):
    """
    Allow Admin, Dean, or Registrar to create/update/delete courses.
    All authenticated users can view courses.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Read-only for everyone authenticated
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write access for specific roles
        return request.user.role in ['ADMIN', 'DEAN', 'REGISTRAR']


class CanManageGrades(permissions.BasePermission):
    """
    Allow Professors to manage their own grades,
    Admin/Registrar can manage all grades.
    Students can only view their own grades.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Admin and Registrar have full access
        if request.user.role in ['ADMIN', 'REGISTRAR']:
            return True

        # Professors can manage grades
        if request.user.role == 'PROFESSOR':
            return True

        # Students can only read
        if request.user.role == 'STUDENT' and request.method in permissions.SAFE_METHODS:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for grades."""
        # Admin and Registrar can access all grades
        if request.user.role in ['ADMIN', 'REGISTRAR']:
            return True

        # Students can only view their own grades
        if request.user.role == 'STUDENT':
            if request.method in permissions.SAFE_METHODS:
                return obj.enrollment.student.user == request.user
            return False

        # Professors can only manage grades for subjects they teach
        if request.user.role == 'PROFESSOR':
            from sections.models import AssignedSubject
            return AssignedSubject.objects.filter(
                subject=obj.enrollment.subject,
                professor=request.user
            ).exists()

        return False


class CanManageEnrollments(permissions.BasePermission):
    """
    Allow Registrar and Admission to manage enrollments.
    Students can view their own enrollments.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Read-only for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write access for specific roles
        return request.user.role in ['ADMIN', 'REGISTRAR', 'ADMISSION']

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for enrollments."""
        # Admin, Registrar, Admission have full access
        if request.user.role in ['ADMIN', 'REGISTRAR', 'ADMISSION']:
            return True

        # Students can only view their own enrollments
        if request.user.role == 'STUDENT':
            if request.method in permissions.SAFE_METHODS:
                return obj.student.user == request.user
            return False

        # Professors can view enrollments for their sections
        if request.user.role == 'PROFESSOR':
            if request.method in permissions.SAFE_METHODS:
                from sections.models import AssignedSubject
                return AssignedSubject.objects.filter(
                    section=obj.section,
                    professor=request.user
                ).exists()
            return False

        return False


class CanManageSections(permissions.BasePermission):
    """
    Allow Admin, Dean, or Registrar to manage sections.
    Professors can view sections they're assigned to.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Read-only for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write access for specific roles
        return request.user.role in ['ADMIN', 'DEAN', 'REGISTRAR']


class CanArchiveRestore(permissions.BasePermission):
    """
    Allow only Admin, Dean, or Registrar to archive/restore records.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['ADMIN', 'DEAN', 'REGISTRAR']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow users to access their own data, or Admin to access all.
    """

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == 'ADMIN':
            return True

        # Check if object has 'user' attribute and matches request user
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Check if object is the user itself
        if obj == request.user:
            return True

        return False


class ReadOnly(permissions.BasePermission):
    """
    Allow read-only access to authenticated users.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.method in permissions.SAFE_METHODS


class CanManageNotifications(permissions.BasePermission):
    """
    Users can manage their own notifications.
    Admin can manage all notifications.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can access all notifications
        if request.user.role == 'ADMIN':
            return True

        # Users can only access their own notifications
        return obj.recipient == request.user


# Composite permissions for common use cases

class CoursePermission(permissions.BasePermission):
    """
    Combined permission for Course viewset.
    - Everyone can view non-archived courses
    - Admin/Dean/Registrar can view all courses including archived
    - Admin/Dean/Registrar can create/update/delete/archive/restore
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role in ['ADMIN', 'DEAN', 'REGISTRAR']


class StudentPermission(permissions.BasePermission):
    """
    Combined permission for Student viewset.
    - Admin/Registrar/Admission can manage students
    - Professors can view students in their sections
    - Students can view their own data
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role in ['ADMIN', 'REGISTRAR', 'ADMISSION']

    def has_object_permission(self, request, view, obj):
        # Admin, Registrar, Admission have full access
        if request.user.role in ['ADMIN', 'REGISTRAR', 'ADMISSION']:
            return True

        # Students can view their own data
        if request.user.role == 'STUDENT':
            if request.method in permissions.SAFE_METHODS:
                return obj.user == request.user
            return False

        # Professors can view students in their sections
        if request.user.role == 'PROFESSOR':
            if request.method in permissions.SAFE_METHODS:
                from sections.models import AssignedSubject
                from enrollments.models import Enrollment
                professor_sections = AssignedSubject.objects.filter(
                    professor=request.user
                ).values_list('section', flat=True)
                return Enrollment.objects.filter(
                    student=obj,
                    section__in=professor_sections
                ).exists()
            return False

        return False
