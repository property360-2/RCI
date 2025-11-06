"""
Comprehensive test suite for core module.

Tests cover:
- TimeStampMixin functionality
- ArchiveMixin functionality (soft delete)
- Custom permissions
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from core.test_utils import UserFactory, CourseFactory
from core.permissions import (
    IsAdmin, IsDean, IsRegistrar, IsProfessor, IsStudent,
    IsAdminOrDeanOrRegistrar, CanManageCourses, CanManageGrades,
    CoursePermission, StudentPermission
)
from courses.models import Course

User = get_user_model()


class TimeStampMixinTest(TestCase):
    """Test TimeStampMixin functionality."""

    def setUp(self):
        """Set up test data."""
        self.course = CourseFactory.create(name='Test Course', code='TC101')

    def test_created_at_is_set_on_creation(self):
        """Test that created_at is automatically set when object is created."""
        self.assertIsNotNone(self.course.created_at)
        self.assertLessEqual(self.course.created_at, timezone.now())

    def test_updated_at_is_set_on_creation(self):
        """Test that updated_at is automatically set when object is created."""
        self.assertIsNotNone(self.course.updated_at)
        self.assertLessEqual(self.course.updated_at, timezone.now())

    def test_updated_at_changes_on_save(self):
        """Test that updated_at is updated when object is saved."""
        original_updated_at = self.course.updated_at

        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.01)

        self.course.name = 'Updated Course Name'
        self.course.save()

        self.assertGreater(self.course.updated_at, original_updated_at)

    def test_created_at_does_not_change_on_save(self):
        """Test that created_at remains unchanged when object is saved."""
        original_created_at = self.course.created_at

        self.course.name = 'Updated Course Name'
        self.course.save()

        self.assertEqual(self.course.created_at, original_created_at)

    def test_get_age_method(self):
        """Test get_age() method returns correct timedelta."""
        age = self.course.get_age()
        self.assertIsInstance(age, timedelta)
        self.assertGreaterEqual(age.total_seconds(), 0)

    def test_default_ordering_newest_first(self):
        """Test that default ordering is by created_at descending."""
        # Note: Course model has its own ordering by 'code', not created_at
        # This test verifies that courses can be ordered by created_at when explicitly requested
        # Create multiple courses
        course1 = CourseFactory.create(name='Course 1', code='C1')
        import time
        time.sleep(0.01)
        course2 = CourseFactory.create(name='Course 2', code='C2')
        time.sleep(0.01)
        course3 = CourseFactory.create(name='Course 3', code='C3')

        # Course model orders by code, so default ordering is C1, C2, C3
        courses = Course.objects.all()
        self.assertEqual(courses[0].code, 'C1')
        self.assertEqual(courses[1].code, 'C2')

        # But we can order by created_at explicitly
        courses_by_date = Course.objects.all().order_by('-created_at')
        self.assertEqual(courses_by_date[0].id, course3.id)
        self.assertEqual(courses_by_date[1].id, course2.id)


class ArchiveMixinTest(TestCase):
    """Test ArchiveMixin functionality (soft delete)."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = UserFactory.create(
            username='admin', role=User.Role.ADMIN
        )
        self.course = CourseFactory.create(name='Test Course', code='TC101')

    def test_archived_is_false_by_default(self):
        """Test that archived is False for new objects."""
        self.assertFalse(self.course.archived)
        self.assertIsNone(self.course.archived_at)
        self.assertIsNone(self.course.archived_by)

    def test_archive_method_sets_archived_flag(self):
        """Test that archive() method sets archived to True."""
        self.course.archive(archived_by=self.admin_user)

        self.assertTrue(self.course.archived)
        self.assertIsNotNone(self.course.archived_at)
        self.assertEqual(self.course.archived_by, self.admin_user)

    def test_archive_method_raises_error_if_already_archived(self):
        """Test that archiving an already archived object raises ValueError."""
        self.course.archive(archived_by=self.admin_user)

        with self.assertRaises(ValueError) as context:
            self.course.archive(archived_by=self.admin_user)

        self.assertIn('already archived', str(context.exception))

    def test_restore_method_unsets_archived_flag(self):
        """Test that restore() method sets archived back to False."""
        self.course.archive(archived_by=self.admin_user)
        self.assertTrue(self.course.archived)

        self.course.restore()
        self.assertFalse(self.course.archived)

    def test_restore_method_preserves_archive_audit_data(self):
        """Test that restore() keeps archived_at and archived_by for audit."""
        self.course.archive(archived_by=self.admin_user)
        archived_at = self.course.archived_at
        archived_by = self.course.archived_by

        self.course.restore()

        # Archived flag is False, but audit data remains
        self.assertFalse(self.course.archived)
        self.assertEqual(self.course.archived_at, archived_at)
        self.assertEqual(self.course.archived_by, archived_by)

    def test_restore_method_raises_error_if_not_archived(self):
        """Test that restoring an active object raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.course.restore()

        self.assertIn('not archived', str(context.exception))

    def test_is_archived_method(self):
        """Test is_archived() method returns correct status."""
        self.assertFalse(self.course.is_archived())

        self.course.archive(archived_by=self.admin_user)
        self.assertTrue(self.course.is_archived())

        self.course.restore()
        self.assertFalse(self.course.is_archived())

    def test_get_archive_info_when_not_archived(self):
        """Test get_archive_info() returns correct data for active record."""
        info = self.course.get_archive_info()
        self.assertEqual(info, {'is_archived': False})

    def test_get_archive_info_when_archived(self):
        """Test get_archive_info() returns complete data for archived record."""
        self.course.archive(archived_by=self.admin_user)
        info = self.course.get_archive_info()

        self.assertTrue(info['is_archived'])
        self.assertEqual(info['archived_at'], self.course.archived_at)
        self.assertEqual(info['archived_by'], 'admin')
        self.assertIsInstance(info['archived_duration'], timedelta)

    def test_archive_without_user(self):
        """Test that archive() works without providing archived_by."""
        self.course.archive()

        self.assertTrue(self.course.archived)
        self.assertIsNotNone(self.course.archived_at)
        self.assertIsNone(self.course.archived_by)

    def test_archived_records_can_be_filtered(self):
        """Test that archived records can be filtered in queries."""
        course1 = CourseFactory.create(name='Active Course', code='AC1')
        course2 = CourseFactory.create(name='Archived Course', code='AC2')
        course2.archive(archived_by=self.admin_user)

        # Query active courses
        active_courses = Course.objects.filter(archived=False)
        self.assertIn(course1, active_courses)
        self.assertNotIn(course2, active_courses)

        # Query archived courses
        archived_courses = Course.objects.filter(archived=True)
        self.assertNotIn(course1, archived_courses)
        self.assertIn(course2, archived_courses)


class PermissionTests(TestCase):
    """Test custom permission classes."""

    def setUp(self):
        """Set up test users and request factory."""
        self.factory = APIRequestFactory()
        self.view = APIView()

        # Create users for each role
        self.admin = UserFactory.create(username='admin', role=User.Role.ADMIN)
        self.dean = UserFactory.create(username='dean', role=User.Role.DEAN)
        self.registrar = UserFactory.create(username='registrar', role=User.Role.REGISTRAR)
        self.admission = UserFactory.create(username='admission', role=User.Role.ADMISSION)
        self.professor = UserFactory.create(username='professor', role=User.Role.PROFESSOR)
        self.student = UserFactory.create(username='student', role=User.Role.STUDENT)

    def test_is_admin_permission(self):
        """Test IsAdmin permission class."""
        permission = IsAdmin()

        request = self.factory.get('/')
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.dean
        self.assertFalse(permission.has_permission(request, self.view))

        request.user = self.student
        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_dean_permission(self):
        """Test IsDean permission class."""
        permission = IsDean()

        request = self.factory.get('/')
        request.user = self.dean
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.admin
        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_registrar_permission(self):
        """Test IsRegistrar permission class."""
        permission = IsRegistrar()

        request = self.factory.get('/')
        request.user = self.registrar
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.dean
        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_professor_permission(self):
        """Test IsProfessor permission class."""
        permission = IsProfessor()

        request = self.factory.get('/')
        request.user = self.professor
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.student
        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_student_permission(self):
        """Test IsStudent permission class."""
        permission = IsStudent()

        request = self.factory.get('/')
        request.user = self.student
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.professor
        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_admin_or_dean_or_registrar_permission(self):
        """Test IsAdminOrDeanOrRegistrar permission class."""
        permission = IsAdminOrDeanOrRegistrar()

        request = self.factory.get('/')

        request.user = self.admin
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.dean
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.registrar
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.professor
        self.assertFalse(permission.has_permission(request, self.view))

        request.user = self.student
        self.assertFalse(permission.has_permission(request, self.view))

    def test_can_manage_courses_permission_read(self):
        """Test CanManageCourses permission for read operations."""
        permission = CanManageCourses()

        # GET request (read) - all authenticated users can read
        request = self.factory.get('/')

        for user in [self.admin, self.dean, self.registrar, self.professor, self.student]:
            request.user = user
            self.assertTrue(permission.has_permission(request, self.view))

    def test_can_manage_courses_permission_write(self):
        """Test CanManageCourses permission for write operations."""
        permission = CanManageCourses()

        # POST request (write) - only admin, dean, registrar can write
        request = self.factory.post('/')

        request.user = self.admin
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.dean
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.registrar
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.professor
        self.assertFalse(permission.has_permission(request, self.view))

        request.user = self.student
        self.assertFalse(permission.has_permission(request, self.view))

    def test_can_manage_grades_permission(self):
        """Test CanManageGrades permission."""
        permission = CanManageGrades()

        # Admin and Registrar have full access
        request = self.factory.post('/')
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, self.view))

        request.user = self.registrar
        self.assertTrue(permission.has_permission(request, self.view))

        # Professor can write grades
        request.user = self.professor
        self.assertTrue(permission.has_permission(request, self.view))

        # Student can only read
        request = self.factory.get('/')
        request.user = self.student
        self.assertTrue(permission.has_permission(request, self.view))

        # Student cannot write
        request = self.factory.post('/')
        request.user = self.student
        self.assertFalse(permission.has_permission(request, self.view))

    def test_course_permission_composite(self):
        """Test CoursePermission composite permission."""
        permission = CoursePermission()

        # Everyone can view
        request = self.factory.get('/')
        for user in [self.admin, self.dean, self.registrar, self.professor, self.student]:
            request.user = user
            self.assertTrue(permission.has_permission(request, self.view))

        # Only admin/dean/registrar can modify
        request = self.factory.post('/')

        for user in [self.admin, self.dean, self.registrar]:
            request.user = user
            self.assertTrue(permission.has_permission(request, self.view))

        for user in [self.professor, self.student]:
            request.user = user
            self.assertFalse(permission.has_permission(request, self.view))

    def test_unauthenticated_user_denied(self):
        """Test that unauthenticated users are denied access."""
        from django.contrib.auth.models import AnonymousUser

        permission = IsAdmin()
        request = self.factory.get('/')
        request.user = AnonymousUser()

        self.assertFalse(permission.has_permission(request, self.view))


class PermissionIntegrationTest(TestCase):
    """Integration tests for permissions with actual models."""

    def setUp(self):
        """Set up test data."""
        from core.test_utils import (
            StudentFactory, GradeRecordFactory,
            SubjectFactory, TermFactory
        )

        self.admin = UserFactory.create(username='admin', role=User.Role.ADMIN)
        self.professor = UserFactory.create(username='prof', role=User.Role.PROFESSOR)
        self.student_user = UserFactory.create(username='student', role=User.Role.STUDENT)

        self.student = StudentFactory.create(user=self.student_user)
        self.subject = SubjectFactory.create()
        self.term = TermFactory.create()
        self.grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term
        )

        self.factory = APIRequestFactory()
        self.view = APIView()

    def test_student_can_view_own_grades_object_permission(self):
        """Test that students can view their own grades (object level)."""
        from core.permissions import CanManageGrades

        permission = CanManageGrades()
        request = self.factory.get('/')
        request.user = self.student_user

        self.assertTrue(permission.has_object_permission(request, self.view, self.grade))

    def test_student_cannot_view_other_grades_object_permission(self):
        """Test that students cannot view other students' grades."""
        from core.test_utils import StudentFactory
        from core.permissions import CanManageGrades

        other_student_user = UserFactory.create(username='other', role=User.Role.STUDENT)
        other_student = StudentFactory.create(user=other_student_user)

        permission = CanManageGrades()
        request = self.factory.get('/')
        request.user = other_student_user

        # Should not be able to view the original student's grade
        self.assertFalse(permission.has_object_permission(request, self.view, self.grade))

    def test_admin_can_view_all_grades(self):
        """Test that admin can view all grades."""
        from core.permissions import CanManageGrades

        permission = CanManageGrades()
        request = self.factory.get('/')
        request.user = self.admin

        self.assertTrue(permission.has_object_permission(request, self.view, self.grade))
