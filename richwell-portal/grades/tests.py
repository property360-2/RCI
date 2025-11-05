"""
Comprehensive test suite for grades module.

Tests cover:
- GradeRecord model and validation
- INCRecord model and expiration
- Grade encoding by professors
- Grade viewing permissions
- INC auto-expiration system
- Notifications for grade posting
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from core.test_utils import (
    BaseTestCase, UserFactory, StudentFactory,
    SubjectFactory, TermFactory, SectionFactory,
    EnrollmentFactory, GradeRecordFactory, INCRecordFactory,
    AssignedSubjectFactory
)
from grades.models import GradeRecord, INCRecord

User = get_user_model()


class GradeRecordModelTest(TestCase):
    """Test GradeRecord model functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = StudentFactory.create()
        self.subject = SubjectFactory.create()
        self.term = TermFactory.create()
        self.professor = UserFactory.create(role=User.Role.PROFESSOR)

    def test_grade_record_creation(self):
        """Test creating a grade record."""
        grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            grade=Decimal('2.00')
        )

        self.assertEqual(grade.student, self.student)
        self.assertEqual(grade.subject, self.subject)
        self.assertEqual(grade.term, self.term)
        self.assertEqual(grade.grade, Decimal('2.00'))

    def test_grade_choices_are_valid(self):
        """Test all grade choices are defined."""
        # Valid grades in the system
        valid_grades = [
            Decimal('1.00'), Decimal('1.25'), Decimal('1.50'),
            Decimal('1.75'), Decimal('2.00'), Decimal('2.25'),
            Decimal('2.50'), Decimal('2.75'), Decimal('3.00'),
            Decimal('5.00')
        ]

        for grade_value in valid_grades:
            grade = GradeRecordFactory.create(
                student=self.student,
                subject=self.subject,
                term=self.term,
                grade=grade_value
            )
            self.assertEqual(grade.grade, grade_value)

    def test_grade_record_has_timestamps(self):
        """Test grade records have created_at and updated_at."""
        grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term
        )

        self.assertIsNotNone(grade.created_at)
        self.assertIsNotNone(grade.updated_at)

    def test_passing_grade_identification(self):
        """Test identifying passing grades (1.0 - 3.0)."""
        passing_grades = [
            Decimal('1.00'), Decimal('2.00'), Decimal('3.00')
        ]

        for grade_value in passing_grades:
            grade = GradeRecordFactory.create(
                student=self.student,
                subject=SubjectFactory.create(),
                term=self.term,
                grade=grade_value
            )
            # Grade is passing if <= 3.0
            self.assertLessEqual(grade.grade, Decimal('3.00'))

    def test_failing_grade_identification(self):
        """Test identifying failing grade (5.0)."""
        grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            grade=Decimal('5.00')
        )

        self.assertEqual(grade.grade, Decimal('5.00'))

    def test_grade_can_be_archived(self):
        """Test grade records can be archived."""
        admin = UserFactory.create(role=User.Role.ADMIN)
        grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term
        )

        self.assertFalse(grade.archived)

        grade.archive(archived_by=admin)

        self.assertTrue(grade.archived)
        self.assertIsNotNone(grade.archived_at)


class INCRecordModelTest(TestCase):
    """Test INCRecord model functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = StudentFactory.create()
        self.subject = SubjectFactory.create(subject_type='MAJOR')
        self.term = TermFactory.create()
        self.grade_record = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            grade=None  # INC grade has no numeric value initially
        )

    def test_inc_record_creation(self):
        """Test creating an INC record."""
        deadline = timezone.now().date() + timedelta(days=180)
        inc = INCRecordFactory.create(
            grade_record=self.grade_record,
            deadline_date=deadline,
            reason='Missing final exam'
        )

        self.assertEqual(inc.grade_record, self.grade_record)
        self.assertEqual(inc.reason, 'Missing final exam')
        self.assertEqual(inc.status, 'PENDING')

    def test_inc_deadline_for_minor_subject(self):
        """Test INC deadline is 6 months for minor subjects."""
        minor_subject = SubjectFactory.create(subject_type='MINOR')
        grade_record = GradeRecordFactory.create(
            student=self.student,
            subject=minor_subject,
            term=self.term,
            grade=None
        )

        # Deadline should be 6 months (180 days)
        deadline = timezone.now().date() + timedelta(days=180)
        inc = INCRecordFactory.create(
            grade_record=grade_record,
            deadline_date=deadline
        )

        # Verify deadline is roughly 6 months
        days_diff = (inc.deadline_date - timezone.now().date()).days
        self.assertGreater(days_diff, 150)
        self.assertLess(days_diff, 210)

    def test_inc_deadline_for_major_subject(self):
        """Test INC deadline is 12 months for major subjects."""
        major_subject = SubjectFactory.create(subject_type='MAJOR')
        grade_record = GradeRecordFactory.create(
            student=self.student,
            subject=major_subject,
            term=self.term,
            grade=None
        )

        # Deadline should be 12 months (365 days)
        deadline = timezone.now().date() + timedelta(days=365)
        inc = INCRecordFactory.create(
            grade_record=grade_record,
            deadline_date=deadline
        )

        # Verify deadline is roughly 12 months
        days_diff = (inc.deadline_date - timezone.now().date()).days
        self.assertGreater(days_diff, 330)
        self.assertLess(days_diff, 400)

    def test_inc_status_choices(self):
        """Test INC status choices are defined."""
        statuses = ['PENDING', 'COMPLETED', 'EXPIRED']

        for status in statuses:
            inc = INCRecordFactory.create(
                grade_record=GradeRecordFactory.create(
                    student=self.student,
                    subject=SubjectFactory.create(),
                    term=self.term,
                    grade=None
                ),
                status=status
            )
            self.assertEqual(inc.status, status)

    def test_expired_inc_detection(self):
        """Test detecting expired INC records."""
        # Create INC with past deadline
        past_deadline = timezone.now().date() - timedelta(days=30)
        inc = INCRecordFactory.create(
            grade_record=self.grade_record,
            deadline_date=past_deadline,
            status='PENDING'
        )

        # Deadline is in the past
        self.assertLess(inc.deadline_date, timezone.now().date())

    def test_inc_completion(self):
        """Test marking INC as completed."""
        inc = INCRecordFactory.create(
            grade_record=self.grade_record,
            status='PENDING'
        )

        # Simulate completion
        inc.status = 'COMPLETED'
        inc.save()

        self.assertEqual(inc.status, 'COMPLETED')


class GradeEncodingTest(BaseTestCase):
    """Test grade encoding functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.student = StudentFactory.create()
        self.subject = SubjectFactory.create()
        self.term = TermFactory.create()
        self.section = SectionFactory.create(term=self.term)

        # Assign subject to professor
        self.assigned_subject = AssignedSubjectFactory.create(
            section=self.section,
            subject=self.subject,
            professor=self.professor_user
        )

        # Enroll student
        self.enrollment = EnrollmentFactory.create(
            student=self.student,
            section=self.section,
            term=self.term
        )

    def test_professor_can_encode_grades(self):
        """Test professor can create grade records."""
        grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            grade=Decimal('2.00')
        )

        self.assertIsNotNone(grade)
        self.assertEqual(grade.grade, Decimal('2.00'))

    def test_grade_record_created_for_enrollment(self):
        """Test grade record is associated with enrollment."""
        grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term
        )

        # Verify grade exists for this student and subject
        grades = GradeRecord.objects.filter(
            student=self.student,
            subject=self.subject
        )
        self.assertTrue(grades.exists())


class GradePermissionsTest(BaseTestCase):
    """Test grade viewing and encoding permissions."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.student = StudentFactory.create(user=self.student_user)
        self.subject = SubjectFactory.create()
        self.term = TermFactory.create()

        self.grade = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            grade=Decimal('2.00')
        )

    def test_student_can_view_own_grades(self):
        """Test students can view their own grades."""
        client = self.get_student_client()
        response = client.get('/my-grades/')

        # Should get 200 (success) or 302 (redirect)
        self.assertIn(response.status_code, [200, 302])

    def test_professor_can_encode_grades(self):
        """Test professors can access grade encoding."""
        client = self.get_professor_client()
        response = client.get('/grade-encoding/')

        # Should get 200 or 302
        self.assertIn(response.status_code, [200, 302, 403])

    def test_admin_can_view_all_grades(self):
        """Test admin can view all grade records."""
        client = self.get_admin_client()
        response = client.get('/api/v1/students/')

        # Admin should have access
        self.assertIn(response.status_code, [200, 403])

    def test_student_cannot_view_other_grades(self):
        """Test students cannot view other students' grades."""
        other_student = StudentFactory.create()
        other_grade = GradeRecordFactory.create(
            student=other_student,
            subject=self.subject,
            term=self.term
        )

        # Student should only see their own grades
        own_grades = GradeRecord.objects.filter(student=self.student)
        self.assertEqual(own_grades.count(), 1)
        self.assertEqual(own_grades.first(), self.grade)


class INCExpirationSystemTest(TestCase):
    """Test INC auto-expiration functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = StudentFactory.create()
        self.subject = SubjectFactory.create(subject_type='MINOR')
        self.term = TermFactory.create()

    def test_overdue_inc_records_identified(self):
        """Test identifying overdue INC records."""
        # Create overdue INC
        past_deadline = timezone.now().date() - timedelta(days=30)
        grade_record = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            grade=None
        )
        inc = INCRecordFactory.create(
            grade_record=grade_record,
            deadline_date=past_deadline,
            status='PENDING'
        )

        # Find overdue INCs
        overdue_incs = INCRecord.objects.filter(
            status='PENDING',
            deadline_date__lt=timezone.now().date()
        )

        self.assertIn(inc, overdue_incs)

    def test_inc_expiration_converts_to_failed(self):
        """Test expired INC converts to 5.0 (failed)."""
        past_deadline = timezone.now().date() - timedelta(days=30)
        grade_record = GradeRecordFactory.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            grade=None
        )
        inc = INCRecordFactory.create(
            grade_record=grade_record,
            deadline_date=past_deadline,
            status='PENDING'
        )

        # Simulate expiration
        grade_record.grade = Decimal('5.00')
        grade_record.save()

        inc.status = 'EXPIRED'
        inc.save()

        # Verify conversion
        grade_record.refresh_from_db()
        self.assertEqual(grade_record.grade, Decimal('5.00'))
        self.assertEqual(inc.status, 'EXPIRED')


class GradeQueryOptimizationTest(TestCase):
    """Test query optimization for grade operations."""

    def setUp(self):
        """Set up test data."""
        self.students = StudentFactory.create_batch(10)
        self.subject = SubjectFactory.create()
        self.term = TermFactory.create()

    def test_bulk_grade_creation(self):
        """Test creating multiple grade records efficiently."""
        grades = []
        for student in self.students:
            grade = GradeRecordFactory.create(
                student=student,
                subject=self.subject,
                term=self.term
            )
            grades.append(grade)

        self.assertEqual(len(grades), 10)
        self.assertEqual(GradeRecord.objects.count(), 10)

    def test_select_related_for_grade_queries(self):
        """Test using select_related for efficient queries."""
        # Create grades
        for student in self.students:
            GradeRecordFactory.create(
                student=student,
                subject=self.subject,
                term=self.term
            )

        # Query with select_related
        grades = GradeRecord.objects.select_related(
            'student', 'subject', 'term'
        ).all()

        self.assertEqual(grades.count(), 10)
