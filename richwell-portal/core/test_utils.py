"""
Test utilities and factories for RCI testing suite.

This module provides common utilities, fixtures, and factory functions
for creating test data across all test modules.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string

User = get_user_model()


class BaseTestCase(TestCase):
    """
    Base test case with common setup for all tests.
    Provides user fixtures for each role and authenticated clients.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        # Create users for each role
        cls.admin_user = UserFactory.create(
            username='admin_test',
            email='admin@test.com',
            role=User.Role.ADMIN,
            first_name='Admin',
            last_name='User'
        )

        cls.dean_user = UserFactory.create(
            username='dean_test',
            email='dean@test.com',
            role=User.Role.DEAN,
            first_name='Dean',
            last_name='User'
        )

        cls.registrar_user = UserFactory.create(
            username='registrar_test',
            email='registrar@test.com',
            role=User.Role.REGISTRAR,
            first_name='Registrar',
            last_name='User'
        )

        cls.admission_user = UserFactory.create(
            username='admission_test',
            email='admission@test.com',
            role=User.Role.ADMISSION,
            first_name='Admission',
            last_name='User'
        )

        cls.professor_user = UserFactory.create(
            username='professor_test',
            email='professor@test.com',
            role=User.Role.PROFESSOR,
            first_name='Professor',
            last_name='User'
        )

        cls.student_user = UserFactory.create(
            username='student_test',
            email='student@test.com',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='User'
        )

    def setUp(self):
        """Set up test client for each test method."""
        self.client = Client()
        self.api_client = APIClient()

    def authenticate_user(self, user):
        """Authenticate a user for web views."""
        self.client.force_login(user)

    def get_api_client(self, user):
        """Get authenticated API client for a user."""
        refresh = RefreshToken.for_user(user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client

    def get_admin_client(self):
        """Get authenticated admin API client."""
        return self.get_api_client(self.admin_user)

    def get_dean_client(self):
        """Get authenticated dean API client."""
        return self.get_api_client(self.dean_user)

    def get_registrar_client(self):
        """Get authenticated registrar API client."""
        return self.get_api_client(self.registrar_user)

    def get_professor_client(self):
        """Get authenticated professor API client."""
        return self.get_api_client(self.professor_user)

    def get_student_client(self):
        """Get authenticated student API client."""
        return self.get_api_client(self.student_user)


class UserFactory:
    """Factory for creating User instances."""

    @staticmethod
    def create(username=None, email=None, password='testpass123',
               role=User.Role.STUDENT, **kwargs):
        """Create a user with the given parameters."""
        if username is None:
            username = f'user_{random_string()}'
        if email is None:
            email = f'{username}@test.com'

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **kwargs
        )
        return user

    @staticmethod
    def create_batch(count=5, role=User.Role.STUDENT, **kwargs):
        """Create multiple users."""
        users = []
        for i in range(count):
            username = f'user_{role.lower()}_{i}_{random_string(4)}'
            user = UserFactory.create(username=username, role=role, **kwargs)
            users.append(user)
        return users


class StudentFactory:
    """Factory for creating Student instances."""

    @staticmethod
    def create(user=None, student_id=None, course=None, **kwargs):
        """Create a student with the given parameters."""
        from students.models import Student

        if user is None:
            user = UserFactory.create(role=User.Role.STUDENT)

        if student_id is None:
            student_id = f'{random.randint(2020, 2024)}-{random.randint(1000, 9999)}'

        if course is None:
            course = CourseFactory.create()

        defaults = {
            'user': user,
            'student_id': student_id,
            'course': course,
            'status': 'ACTIVE',
            'year_level': 1,
            'documents': {}
        }
        defaults.update(kwargs)

        student = Student.objects.create(**defaults)
        return student

    @staticmethod
    def create_batch(count=5, **kwargs):
        """Create multiple students."""
        students = []
        for _ in range(count):
            student = StudentFactory.create(**kwargs)
            students.append(student)
        return students


class CourseFactory:
    """Factory for creating Course instances."""

    @staticmethod
    def create(name=None, code=None, **kwargs):
        """Create a course with the given parameters."""
        from courses.models import Course

        if name is None:
            name = f'Test Course {random_string()}'
        if code is None:
            code = f'TC{random_string(6).upper()}'

        defaults = {
            'name': name,
            'code': code,
            'description': f'Description for {name}',
            'total_units': 120,
            'years_to_complete': 4
        }
        defaults.update(kwargs)

        course = Course.objects.create(**defaults)
        return course

    @staticmethod
    def create_batch(count=3, **kwargs):
        """Create multiple courses."""
        courses = []
        for _ in range(count):
            course = CourseFactory.create(**kwargs)
            courses.append(course)
        return courses


class SubjectFactory:
    """Factory for creating Subject instances."""

    @staticmethod
    def create(name=None, code=None, course=None, **kwargs):
        """Create a subject with the given parameters."""
        from subjects.models import Subject

        if name is None:
            name = f'Test Subject {random_string()}'
        if code is None:
            code = f'TS{random.randint(100, 999)}'
        if course is None:
            course = CourseFactory.create()

        defaults = {
            'name': name,
            'code': code,
            'course': course,
            'units': 3,
            'year_level': 1
        }
        defaults.update(kwargs)

        subject = Subject.objects.create(**defaults)
        return subject

    @staticmethod
    def create_batch(count=5, course=None, **kwargs):
        """Create multiple subjects."""
        subjects = []
        for _ in range(count):
            subject = SubjectFactory.create(course=course, **kwargs)
            subjects.append(subject)
        return subjects


class TermFactory:
    """Factory for creating Term instances."""

    @staticmethod
    def create(name=None, slug=None, **kwargs):
        """Create a term with the given parameters."""
        from terms.models import Term
        from django.utils.text import slugify

        if name is None:
            year = random.randint(2025, 2026)
            semester = random.choice(['1st Semester', '2nd Semester', 'Summer'])
            name = f'AY {year}-{year+1} {semester} {random_string(4)}'

        if slug is None:
            slug = slugify(name)

        # Create dates that are in the future to allow enrollments in tests
        # Using 2026 dates to ensure they're in the future relative to test environment
        defaults = {
            'name': name,
            'slug': slug,
            'term_start': datetime(2026, 1, 15).date(),
            'term_end': datetime(2026, 6, 15).date(),
            'enrollment_start': datetime(2026, 1, 1).date(),
            'enrollment_end': datetime(2026, 3, 31).date(),
            'is_active': True
        }
        defaults.update(kwargs)

        term = Term.objects.create(**defaults)
        return term


class SectionFactory:
    """Factory for creating Section instances."""

    @staticmethod
    def create(code=None, course=None, term=None, **kwargs):
        """Create a section with the given parameters."""
        from sections.models import Section

        if code is None:
            code = f'SEC-{random_string()}'
        if course is None:
            course = CourseFactory.create()
        if term is None:
            term = TermFactory.create()

        defaults = {
            'code': code,
            'course': course,
            'term': term,
            'capacity': 30
        }
        defaults.update(kwargs)

        section = Section.objects.create(**defaults)
        return section


class AssignedSubjectFactory:
    """Factory for creating AssignedSubject instances."""

    @staticmethod
    def create(section=None, subject=None, professor=None, **kwargs):
        """Create an assigned subject with the given parameters."""
        from sections.models import AssignedSubject

        if section is None:
            section = SectionFactory.create()
        if subject is None:
            # Subject must belong to the same course as the section
            subject = SubjectFactory.create(course=section.course)
        if professor is None:
            professor = UserFactory.create(role=User.Role.PROFESSOR)

        defaults = {
            'section': section,
            'subject': subject,
            'professor': professor,
            'schedule': 'MWF 10:00-11:00',
            'room': f'Room {random.randint(100, 500)}'
        }
        defaults.update(kwargs)

        assigned = AssignedSubject.objects.create(**defaults)
        return assigned


class EnrollmentFactory:
    """Factory for creating Enrollment instances."""

    @staticmethod
    def create(student=None, subject=None, section=None, term=None, **kwargs):
        """Create an enrollment with the given parameters."""
        from enrollments.models import Enrollment

        if student is None:
            student = StudentFactory.create()

        # Determine course to use - prefer from subject if provided, otherwise create new
        course = None
        if subject is not None:
            course = subject.course
        elif section is not None:
            course = section.course

        # Create subject if not provided, ensuring it matches the course
        if subject is None:
            if course is not None:
                subject = SubjectFactory.create(course=course)
            else:
                subject = SubjectFactory.create()
                course = subject.course

        # Create section if not provided, ensuring it matches the course
        if section is None:
            if term is not None:
                section = SectionFactory.create(course=course, term=term)
            else:
                section = SectionFactory.create(course=course)

        if term is None:
            term = section.term

        defaults = {
            'student': student,
            'subject': subject,
            'section': section,
            'term': term,
            'units': subject.units if hasattr(subject, 'units') else 3,
            'status': 'CONFIRMED'
        }
        defaults.update(kwargs)

        enrollment = Enrollment.objects.create(**defaults)
        return enrollment


class GradeRecordFactory:
    """Factory for creating GradeRecord instances."""

    @staticmethod
    def create(enrollment=None, student=None, subject=None, section=None, term=None,
               grade=None, encoded_by=None, **kwargs):
        """Create a grade record with the given parameters."""
        from grades.models import GradeRecord

        # If enrollment not provided, create one from individual parameters
        if enrollment is None:
            enrollment_params = {}
            if student is not None:
                enrollment_params['student'] = student
            if subject is not None:
                enrollment_params['subject'] = subject
            if section is not None:
                enrollment_params['section'] = section
            if term is not None:
                enrollment_params['term'] = term
            enrollment = EnrollmentFactory.create(**enrollment_params)

        if grade is None:
            grade = random.choice(['1.0', '1.5', '2.0', '2.5', '3.0'])
        if encoded_by is None:
            encoded_by = UserFactory.create(role=User.Role.PROFESSOR)

        defaults = {
            'enrollment': enrollment,
            'grade': grade,
            'encoded_by': encoded_by
        }
        defaults.update(kwargs)

        grade_record = GradeRecord.objects.create(**defaults)
        return grade_record


class INCRecordFactory:
    """Factory for creating INCRecord instances."""

    @staticmethod
    def create(enrollment=None, grade_record=None, deadline=None, deadline_date=None, **kwargs):
        """Create an INC record with the given parameters."""
        from grades.models import INCRecord, GradeRecord

        # Support both 'enrollment' and 'grade_record' parameter names
        if enrollment is None and grade_record is not None:
            # If grade_record is provided, extract enrollment from it
            enrollment = grade_record.enrollment

        if enrollment is None:
            enrollment = EnrollmentFactory.create()

        # Support both 'deadline' and 'deadline_date' parameter names
        if deadline is None:
            if deadline_date is not None:
                deadline = deadline_date
            else:
                # Default to 6 months from now
                deadline = (datetime.now() + timedelta(days=180)).date()

        # Filter out legacy field names that don't exist in the model
        valid_fields = {'enrollment', 'deadline', 'resolved_at', 'resolution_note', 'confirmed_by'}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}

        # Map legacy field names to current ones
        if 'reason' in kwargs:
            filtered_kwargs['resolution_note'] = kwargs['reason']
        if 'status' in kwargs:
            # 'status' was removed - if it was 'RESOLVED', set resolved_at
            if kwargs['status'] == 'RESOLVED' and 'resolved_at' not in filtered_kwargs:
                from django.utils import timezone
                filtered_kwargs['resolved_at'] = timezone.now()

        # Ensure the enrollment has an INC grade (required by validation)
        if not hasattr(enrollment, 'grade') or enrollment.grade.grade != 'INC':
            # Create or update grade record to INC
            if hasattr(enrollment, 'grade'):
                enrollment.grade.grade = 'INC'
                enrollment.grade.save()
            else:
                GradeRecord.objects.create(
                    enrollment=enrollment,
                    grade='INC',
                    encoded_by=UserFactory.create(role=User.Role.PROFESSOR)
                )

        # Check if INCRecord already exists for this enrollment (OneToOne relationship)
        # This check must happen AFTER ensuring the grade is INC, in case creating/updating
        # the GradeRecord to INC automatically creates an INCRecord
        try:
            existing_inc = INCRecord.objects.get(enrollment=enrollment)
            # If an INCRecord already exists, update and return it instead
            existing_inc.deadline = deadline
            for key, value in filtered_kwargs.items():
                setattr(existing_inc, key, value)
            existing_inc.save()
            return existing_inc
        except INCRecord.DoesNotExist:
            pass

        defaults = {
            'enrollment': enrollment,
            'deadline': deadline
        }
        defaults.update(filtered_kwargs)

        inc_record = INCRecord.objects.create(**defaults)
        return inc_record


class NotificationFactory:
    """Factory for creating Notification instances."""

    @staticmethod
    def create(recipient=None, notification_type='GENERAL', **kwargs):
        """Create a notification with the given parameters."""
        from notifications.models import Notification

        if recipient is None:
            recipient = UserFactory.create()

        defaults = {
            'recipient': recipient,
            'notification_type': notification_type,
            'title': f'Test Notification {random_string()}',
            'message': 'This is a test notification message',
            'is_read': False
        }
        defaults.update(kwargs)

        notification = Notification.objects.create(**defaults)
        return notification


def random_string(length=8):
    """Generate a random string of given length."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def create_test_data_set():
    """
    Create a complete test data set with related objects.
    Returns a dictionary with all created objects.
    """
    # Create users
    admin = UserFactory.create(username='admin', role=User.Role.ADMIN)
    dean = UserFactory.create(username='dean', role=User.Role.DEAN)
    registrar = UserFactory.create(username='registrar', role=User.Role.REGISTRAR)
    professor = UserFactory.create(username='professor', role=User.Role.PROFESSOR)

    # Create course and subjects
    course = CourseFactory.create(name='Computer Science', code='CS')
    subjects = SubjectFactory.create_batch(5, course=course)

    # Create term and section
    term = TermFactory.create(name='AY 2024-2025 1st Semester', is_active=True)
    section = SectionFactory.create(code='CS-1A', course=course, term=term)

    # Assign subjects to section
    assigned_subjects = []
    for subject in subjects:
        assigned = AssignedSubjectFactory.create(
            section=section,
            subject=subject,
            professor=professor
        )
        assigned_subjects.append(assigned)

    # Create students and enroll them
    students = StudentFactory.create_batch(10)
    enrollments = []
    for student in students:
        for subject in subjects[:3]:
            enrollment = EnrollmentFactory.create(
                student=student,
                subject=subject,
                section=section,
                term=term
            )
            enrollments.append(enrollment)

    # Create some grades
    grades = []
    for enrollment in enrollments[:15]:
        grade = GradeRecordFactory.create(
            enrollment=enrollment,
            encoded_by=professor
        )
        grades.append(grade)

    # Create some INC records
    inc_records = []
    for student in students[5:7]:
        for subject in subjects[3:5]:
            enrollment = EnrollmentFactory.create(
                student=student,
                subject=subject,
                section=section,
                term=term
            )
            inc = INCRecordFactory.create(enrollment=enrollment)
            inc_records.append(inc)

    return {
        'admin': admin,
        'dean': dean,
        'registrar': registrar,
        'professor': professor,
        'course': course,
        'subjects': subjects,
        'term': term,
        'section': section,
        'assigned_subjects': assigned_subjects,
        'students': students,
        'enrollments': enrollments,
        'grades': grades,
        'inc_records': inc_records
    }
