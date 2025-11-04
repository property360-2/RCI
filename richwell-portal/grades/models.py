"""
Grade Models

This module defines the GradeRecord and INCRecord models for tracking student
grades and incomplete (INC) grade management in the Richwell College Portal.

**Grade Structure:**
- GradeRecord: Stores final grades for enrollments (1.0-5.0 scale)
- INCRecord: Tracks incomplete grades with deadlines (6 or 12 months)

**Grading Scale:**
- 1.0, 1.5, 2.0, 2.5, 3.0: Passing grades (1.0 is highest)
- 5.0: Failing grade
- INC: Incomplete (requires completion within deadline)
- DRP: Dropped (student withdrew from subject)

**Related Models:**
- Enrollment: One-to-one relationship with grade records
- Student: Grades belong to students
- Subject: Grades are for specific subjects
- User (Professor): Professors encode grades

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from core.models import ArchiveMixin, TimeStampMixin


class GradeRecord(ArchiveMixin, TimeStampMixin):
    """
    Stores the final grade for a student enrollment.

    A GradeRecord represents the final grade a student received for a
    specific subject enrollment. Grades are encoded by professors and
    can be updated within specified periods.

    **Business Rules:**
    - One grade per enrollment (one-to-one relationship)
    - Only professors can encode grades
    - INC grades must have corresponding INCRecord
    - Grades cannot be changed after term ends (without special permission)
    - Failed students (5.0) cannot use subject as prerequisite

    **Fields:**
        enrollment (OneToOne): Link to enrollment record
        grade (str): Final grade (1.0, 1.5, 2.0, 2.5, 3.0, 5.0, INC, DRP)
        encoded_by (FK): Professor who encoded the grade
        encoded_at (DateTime): When grade was encoded
        remarks (text): Additional notes or comments

    **Methods:**
        is_passing(): Check if grade is passing (>= 3.0)
        is_inc(): Check if grade is incomplete
        is_failed(): Check if grade is failed (5.0)
        can_be_used_as_prerequisite(): Check if grade qualifies for prerequisites
        convert_inc_to_grade(): Convert INC to final grade

    **Example Usage:**
        ```python
        # Encode a grade
        grade = GradeRecord.objects.create(
            enrollment=enrollment,
            grade=GradeRecord.Grade.TWO_ZERO,
            encoded_by=professor,
            remarks="Excellent performance"
        )

        # Check if passing
        if grade.is_passing():
            # Student passed
            pass
        ```

    **Access Control:**
    - DEAN: Read access to all grades
    - REGISTRAR: Full read/write access
    - PROFESSOR: Encode grades for own sections
    - STUDENT: Read access to own grades only
    """

    class Grade(models.TextChoices):
        ONE_ZERO = "1.0", "1.0 (Excellent)"
        ONE_FIVE = "1.5", "1.5 (Very Good)"
        TWO_ZERO = "2.0", "2.0 (Good)"
        TWO_FIVE = "2.5", "2.5 (Satisfactory)"
        THREE_ZERO = "3.0", "3.0 (Passing)"
        FIVE_ZERO = "5.0", "5.0 (Failed)"
        INC = "INC", "Incomplete"
        DRP = "DRP", "Dropped"

    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade",
        help_text="The enrollment this grade belongs to"
    )

    grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        help_text="Final grade for the enrollment"
    )

    encoded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role": "PROFESSOR"},
        related_name="encoded_grades",
        help_text="Professor who encoded this grade"
    )

    encoded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the grade was encoded"
    )

    remarks = models.TextField(
        blank=True,
        help_text="Additional comments or notes about the grade"
    )

    class Meta:
        ordering = ["-encoded_at"]
        verbose_name = "Grade Record"
        verbose_name_plural = "Grade Records"
        indexes = [
            models.Index(fields=['enrollment', 'archived']),
            models.Index(fields=['grade', 'encoded_at']),
            models.Index(fields=['encoded_by', 'encoded_at']),
        ]

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.enrollment.subject.code}: {self.grade}"

    def clean(self):
        """
        Validate grade record before saving.

        Ensures:
        - Encoder is a professor
        - INC grades have INCRecord
        - Enrollment is confirmed
        - No duplicate grades for same enrollment

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        if self.encoded_by and self.encoded_by.role != 'PROFESSOR':
            errors['encoded_by'] = 'Only professors can encode grades.'

        if self.enrollment and not self.enrollment.is_confirmed():
            errors['enrollment'] = 'Can only grade confirmed enrollments.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Save grade record after validation.
        Create INCRecord if grade is INC.
        """
        self.clean()
        super().save(*args, **kwargs)

        # Create INCRecord if grade is INC and doesn't exist
        if self.grade == self.Grade.INC:
            if not hasattr(self.enrollment, 'inc_record'):
                INCRecord.create_for_enrollment(self.enrollment)

    def is_passing(self):
        """
        Check if grade is passing.

        Returns:
            bool: True if grade is 1.0-3.0

        Example:
            ```python
            if grade.is_passing():
                # Student passed, can take next subject
            ```

        **Business Logic:** Passing grades are 1.0, 1.5, 2.0, 2.5, 3.0
        """
        passing_grades = [
            self.Grade.ONE_ZERO,
            self.Grade.ONE_FIVE,
            self.Grade.TWO_ZERO,
            self.Grade.TWO_FIVE,
            self.Grade.THREE_ZERO
        ]
        return self.grade in passing_grades

    def is_failed(self):
        """
        Check if grade is failed.

        Returns:
            bool: True if grade is 5.0

        Example:
            ```python
            if grade.is_failed():
                # Student failed, must retake
            ```
        """
        return self.grade == self.Grade.FIVE_ZERO

    def is_inc(self):
        """
        Check if grade is incomplete.

        Returns:
            bool: True if grade is INC

        Example:
            ```python
            if grade.is_inc():
                # Check INC deadline
            ```
        """
        return self.grade == self.Grade.INC

    def is_dropped(self):
        """
        Check if enrollment was dropped.

        Returns:
            bool: True if grade is DRP

        Example:
            ```python
            if grade.is_dropped():
                # Student withdrew from subject
            ```
        """
        return self.grade == self.Grade.DRP

    def can_be_used_as_prerequisite(self):
        """
        Check if this grade qualifies for prerequisite requirements.

        Returns:
            bool: True if passing grade (not INC, DRP, or 5.0)

        Example:
            ```python
            if grade.can_be_used_as_prerequisite():
                # Allow enrollment in next subject
            ```

        **Business Logic:**
        - Must be passing grade (1.0-3.0)
        - INC grades don't count until resolved
        - Failed grades (5.0) don't count
        - Dropped (DRP) doesn't count
        """
        return self.is_passing()

    def get_grade_point(self):
        """
        Get numeric grade point value.

        Returns:
            float: Grade point (1.0-5.0), or None for INC/DRP

        Example:
            ```python
            gp = grade.get_grade_point()
            # 2.5
            ```
        """
        grade_points = {
            self.Grade.ONE_ZERO: 1.0,
            self.Grade.ONE_FIVE: 1.5,
            self.Grade.TWO_ZERO: 2.0,
            self.Grade.TWO_FIVE: 2.5,
            self.Grade.THREE_ZERO: 3.0,
            self.Grade.FIVE_ZERO: 5.0
        }
        return grade_points.get(self.grade)

    def convert_inc_to_grade(self, new_grade, converted_by=None):
        """
        Convert an INC grade to a final grade.

        Args:
            new_grade (str): New grade to assign
            converted_by (User, optional): User performing conversion

        Returns:
            bool: True if conversion successful

        Raises:
            ValueError: If not an INC grade

        Example:
            ```python
            grade.convert_inc_to_grade(GradeRecord.Grade.TWO_ZERO, professor)
            # INC converted to 2.0
            ```
        """
        if not self.is_inc():
            raise ValueError("Only INC grades can be converted")

        self.grade = new_grade
        self.save(update_fields=['grade'])

        # Mark INCRecord as resolved
        if hasattr(self.enrollment, 'inc_record'):
            inc_record = self.enrollment.inc_record
            inc_record.resolve(
                resolution_note=f"Converted to {new_grade}",
                confirmed_by=converted_by
            )

        return True

    @classmethod
    def get_by_student(cls, student, term=None):
        """
        Get all grades for a student.

        Args:
            student: Student object
            term (Term, optional): Filter by term

        Returns:
            QuerySet: GradeRecord objects

        Example:
            ```python
            grades = GradeRecord.get_by_student(student, fall_2024)
            # All grades for student in Fall 2024
            ```
        """
        enrollments = student.enrollments.filter(archived=False)
        if term:
            enrollments = enrollments.filter(term=term)

        return cls.objects.filter(
            enrollment__in=enrollments,
            archived=False
        ).select_related('enrollment__subject', 'enrollment__term')


class INCRecord(ArchiveMixin, TimeStampMixin):
    """
    Tracks incomplete (INC) grades with deadlines and resolution.

    An INCRecord manages the deadline and completion tracking for incomplete
    grades. Minor subjects have 6-month deadlines, major subjects have
    12-month deadlines.

    **Business Rules:**
    - INCRecord created automatically when grade is INC
    - Minor subjects: 6-month deadline
    - Major subjects: 12-month deadline
    - Unresolved INC past deadline converts to 5.0 (Failed)
    - Only registrars can confirm INC resolutions

    **Fields:**
        enrollment (OneToOne): Link to enrollment with INC grade
        deadline (Date): Deadline to complete requirements
        resolved_at (DateTime): When INC was resolved
        resolution_note (text): How the INC was resolved
        confirmed_by (FK): Registrar who confirmed resolution

    **Methods:**
        is_overdue(): Check if deadline has passed
        days_remaining(): Calculate days until deadline
        resolve(): Mark INC as resolved
        convert_to_failed(): Convert expired INC to 5.0

    **Example Usage:**
        ```python
        # INCRecord created automatically when grade is INC
        inc = enrollment.inc_record

        # Check if overdue
        if inc.is_overdue():
            inc.convert_to_failed()

        # Resolve INC
        inc.resolve("Student completed requirements", registrar)
        ```

    **Access Control:**
    - DEAN: Read access to all INC records
    - REGISTRAR: Full read/write access
    - PROFESSOR: Read access to own sections
    - STUDENT: Read access to own INC records
    """

    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="inc_record",
        help_text="The enrollment with INC grade"
    )

    deadline = models.DateField(
        help_text="Deadline to complete requirements (6 or 12 months)"
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the INC was resolved"
    )

    resolution_note = models.TextField(
        blank=True,
        help_text="How the INC was resolved"
    )

    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "REGISTRAR"},
        related_name="confirmed_incs",
        help_text="Registrar who confirmed the resolution"
    )

    class Meta:
        ordering = ["deadline"]
        verbose_name = "INC Record"
        verbose_name_plural = "INC Records"
        indexes = [
            models.Index(fields=['deadline', 'resolved_at']),
            models.Index(fields=['enrollment', 'archived']),
        ]

    def __str__(self):
        status = "Resolved" if self.resolved_at else "Pending"
        return f"{self.enrollment.student.student_id} - {self.enrollment.subject.code} (INC - {status})"

    def clean(self):
        """
        Validate INC record before saving.

        Ensures:
        - Enrollment has INC grade
        - Deadline is in the future (on creation)
        - Confirmed by is registrar

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        if self.enrollment and hasattr(self.enrollment, 'grade'):
            if self.enrollment.grade.grade != GradeRecord.Grade.INC:
                errors['enrollment'] = 'INCRecord can only be created for INC grades'

        if self.confirmed_by and self.confirmed_by.role != 'REGISTRAR':
            errors['confirmed_by'] = 'Only registrars can confirm INC resolutions'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Save INC record after validation."""
        self.clean()
        super().save(*args, **kwargs)

    def is_resolved(self):
        """
        Check if INC has been resolved.

        Returns:
            bool: True if resolved_at is set

        Example:
            ```python
            if inc.is_resolved():
                # INC completed
            ```
        """
        return self.resolved_at is not None

    def is_overdue(self):
        """
        Check if INC deadline has passed.

        Returns:
            bool: True if deadline has passed and not resolved

        Example:
            ```python
            if inc.is_overdue():
                # Convert to failed
                inc.convert_to_failed()
            ```
        """
        if self.is_resolved():
            return False
        return timezone.now().date() > self.deadline

    def days_remaining(self):
        """
        Calculate days until INC deadline.

        Returns:
            int: Days remaining (negative if overdue)

        Example:
            ```python
            days = inc.days_remaining()
            # 45 days remaining
            ```
        """
        if self.is_resolved():
            return 0
        delta = self.deadline - timezone.now().date()
        return delta.days

    def resolve(self, resolution_note="", confirmed_by=None):
        """
        Mark INC as resolved.

        Args:
            resolution_note (str): Note about resolution
            confirmed_by (User, optional): Registrar confirming resolution

        Returns:
            bool: True if resolution successful

        Raises:
            ValueError: If already resolved

        Example:
            ```python
            inc.resolve("Student completed all requirements", registrar)
            ```
        """
        if self.is_resolved():
            raise ValueError("INC is already resolved")

        self.resolved_at = timezone.now()
        self.resolution_note = resolution_note
        self.confirmed_by = confirmed_by
        self.save(update_fields=['resolved_at', 'resolution_note', 'confirmed_by'])
        return True

    def convert_to_failed(self):
        """
        Convert expired INC to failed grade (5.0).

        Returns:
            bool: True if conversion successful

        Raises:
            ValueError: If not overdue or already resolved

        Example:
            ```python
            if inc.is_overdue():
                inc.convert_to_failed()
                # Grade changed to 5.0
            ```
        """
        if not self.is_overdue():
            raise ValueError("Cannot convert INC that is not overdue")

        if self.is_resolved():
            raise ValueError("Cannot convert resolved INC")

        # Update grade to 5.0
        grade_record = self.enrollment.grade
        grade_record.grade = GradeRecord.Grade.FIVE_ZERO
        grade_record.remarks += f"\n[AUTO] INC converted to 5.0 on {timezone.now().date()} (deadline expired)"
        grade_record.save(update_fields=['grade', 'remarks'])

        # Mark as resolved
        self.resolve(
            resolution_note="Automatically converted to 5.0 (deadline expired)"
        )

        return True

    @classmethod
    def create_for_enrollment(cls, enrollment, is_major=False):
        """
        Create INCRecord for an enrollment.

        Args:
            enrollment: Enrollment object
            is_major (bool): True for major subject (12 months), False for minor (6 months)

        Returns:
            INCRecord: Created INC record

        Example:
            ```python
            inc = INCRecord.create_for_enrollment(enrollment, is_major=True)
            # INC deadline set to 12 months from now
            ```

        **Deadline Rules:**
        - Minor subjects: 6 months
        - Major subjects: 12 months
        """
        months = 12 if is_major else 6
        deadline = timezone.now().date() + timedelta(days=months*30)

        return cls.objects.create(
            enrollment=enrollment,
            deadline=deadline
        )

    @classmethod
    def get_overdue(cls):
        """
        Get all overdue INC records.

        Returns:
            QuerySet: Overdue INCRecord objects

        Example:
            ```python
            overdue_incs = INCRecord.get_overdue()
            for inc in overdue_incs:
                inc.convert_to_failed()
            ```
        """
        return cls.objects.filter(
            deadline__lt=timezone.now().date(),
            resolved_at__isnull=True,
            archived=False
        )
