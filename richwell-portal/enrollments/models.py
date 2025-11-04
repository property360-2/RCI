"""
Enrollment Model

This module defines the Enrollment model, which represents student enrollments
in subjects for specific terms in the Richwell College Portal.

**Enrollment Structure:**
- Links a student to a subject for a specific academic term
- Each enrollment may be associated with a section (nullable for irregular students)
- Enforces 30-unit cap per term
- Validates prerequisites before enrollment
- Tracks enrollment status (Pending, Confirmed, Cancelled)

**Related Models:**
- Student: The student enrolling
- Subject: The subject being enrolled in
- Section: The class section (nullable)
- Term: The academic term
- GradeRecord: Final grade for this enrollment

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from core.models import ArchiveMixin, TimeStampMixin


class Enrollment(ArchiveMixin, TimeStampMixin):
    """
    Represents a student's enrollment in a subject for a specific term.

    An Enrollment links a student to a subject within an academic term.
    It enforces business rules like the 30-unit cap and prerequisite
    validation before allowing enrollment.

    **Business Rules:**
    - Student cannot exceed 30 units per term
    - Student must meet all prerequisite requirements
    - Each student can only enroll once per subject per term
    - Section is optional (for irregular students)
    - Archived enrollments don't count toward unit cap
    - Only ACTIVE or IRREGULAR students can enroll

    **Fields:**
        student (FK): The student enrolling
        subject (FK): The subject being enrolled in
        section (FK): The class section (nullable for irregular students)
        term (FK): The academic term
        units (int): Credit units (copied from subject for audit)
        status (str): Enrollment status (Pending, Confirmed, Cancelled)

    **Methods:**
        validate_unit_cap(): Check if enrollment exceeds 30-unit cap
        validate_prerequisites(): Check if student meets prerequisites
        confirm(): Confirm pending enrollment
        cancel(): Cancel enrollment and free up section slot

    **Example Usage:**
        ```python
        # Create an enrollment
        enrollment = Enrollment.objects.create(
            student=student,
            subject=comp101,
            section=bsit_1a,
            term=fall_2024,
            status=Enrollment.EnrollmentStatus.PENDING
        )

        # Validate and confirm
        if enrollment.validate_unit_cap() and enrollment.validate_prerequisites():
            enrollment.confirm()
        ```

    **Access Control:**
    - DEAN: Full read access
    - REGISTRAR: Full read/write access
    - ADMISSION: Create enrollments, read access
    - PROFESSOR: Read access to enrollments in their sections
    - STUDENT: Read access to own enrollments
    """

    class EnrollmentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="The student enrolling in the subject"
    )

    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.PROTECT,
        related_name="enrollments",
        help_text="The subject being enrolled in"
    )

    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="enrollments",
        help_text="Class section (nullable for irregular students)"
    )

    term = models.ForeignKey(
        "terms.Term",
        on_delete=models.PROTECT,
        related_name="enrollments",
        help_text="The academic term for this enrollment"
    )

    units = models.PositiveIntegerField(
        help_text="Credit units (copied from subject for audit purposes)"
    )

    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.PENDING,
        db_index=True,
        help_text="Current enrollment status"
    )

    class Meta:
        unique_together = ["student", "subject", "term"]
        ordering = ["-term", "student", "subject"]
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        indexes = [
            models.Index(fields=['student', 'term', 'status']),
            models.Index(fields=['section', 'archived']),
            models.Index(fields=['term', 'status']),
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} ({self.term})"

    def clean(self):
        """
        Validate enrollment data before saving.

        Ensures:
        - Student can enroll (not graduated, dropped, or on LOA)
        - 30-unit cap is not exceeded
        - Prerequisites are met
        - Section belongs to same course as subject
        - No duplicate enrollments

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        # Check if student can enroll
        if self.student:
            can_enroll, reason = self.student.can_enroll()
            if not can_enroll:
                errors['student'] = reason

        # Validate unit cap
        if self.student and self.term:
            can_add, reason = self.validate_unit_cap()
            if not can_add:
                errors['units'] = reason

        # Validate prerequisites
        if self.student and self.subject:
            has_prereqs, missing = self.validate_prerequisites()
            if not has_prereqs:
                missing_codes = [s.code for s in missing]
                errors['subject'] = f"Missing prerequisites: {', '.join(missing_codes)}"

        # Validate section matches subject's course
        if self.section and self.subject:
            if self.section.course != self.subject.course:
                errors['section'] = "Section must belong to the same course as the subject"

        # Validate section has available slots
        if self.section and not self.pk:  # Only check on creation
            can_accept, reason = self.section.can_accept_enrollment()
            if not can_accept:
                errors['section'] = reason

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Save enrollment after validation.
        Auto-populate units from subject if not set.
        """
        if not self.units:
            self.units = self.subject.units

        # Only validate if creating new enrollment or changing key fields
        if not self.pk or any(field in kwargs.get('update_fields', [])
                             for field in ['student', 'subject', 'term', 'section']):
            self.clean()

        is_new = not self.pk
        super().save(*args, **kwargs)

        # Update section slots if enrolling in a section
        if is_new and self.section and self.status == self.EnrollmentStatus.CONFIRMED:
            self.section.enroll_student()

    def validate_unit_cap(self):
        """
        Check if this enrollment would exceed the 30-unit cap.

        Returns:
            tuple: (bool, str) - (is_valid, reason)

        Example:
            ```python
            can_add, reason = enrollment.validate_unit_cap()
            if not can_add:
                print(reason)
            ```

        **Business Rule:** Students cannot exceed 30 units per term
        """
        if not self.student or not self.term:
            return (True, "")

        # Calculate current units (excluding this enrollment if updating)
        current_enrollments = Enrollment.objects.filter(
            student=self.student,
            term=self.term,
            status=self.EnrollmentStatus.CONFIRMED,
            archived=False
        )

        if self.pk:
            current_enrollments = current_enrollments.exclude(pk=self.pk)

        result = current_enrollments.aggregate(total=Sum('units'))
        current_units = result['total'] or 0
        new_total = current_units + self.units

        if new_total > 30:
            return (False, f"Would exceed 30-unit cap (current: {current_units}, new total: {new_total})")

        return (True, "")

    def validate_prerequisites(self):
        """
        Check if student has met all prerequisite requirements.

        Returns:
            tuple: (bool, list) - (has_prerequisites, missing_subjects)

        Example:
            ```python
            has_prereqs, missing = enrollment.validate_prerequisites()
            if not has_prereqs:
                for subj in missing:
                    print(f"Missing: {subj.code}")
            ```

        **Business Logic:**
        - Student must have passing grade (>= 3.0) in all prerequisites
        - INC (Incomplete) grades don't count as completion
        """
        if not self.subject or not self.student:
            return (True, [])

        prerequisites = self.subject.get_prerequisites()
        if not prerequisites.exists():
            return (True, [])

        missing_prereqs = []
        for prereq in prerequisites:
            if not self.student.has_passed_subject(prereq):
                missing_prereqs.append(prereq)

        return (len(missing_prereqs) == 0, missing_prereqs)

    def confirm(self):
        """
        Confirm a pending enrollment.

        Returns:
            bool: True if confirmation successful

        Raises:
            ValueError: If enrollment is not pending

        Example:
            ```python
            enrollment.confirm()
            # Status changed to CONFIRMED
            ```
        """
        if self.status != self.EnrollmentStatus.PENDING:
            raise ValueError("Only pending enrollments can be confirmed")

        self.status = self.EnrollmentStatus.CONFIRMED
        self.save(update_fields=['status'])

        # Update section slots if applicable
        if self.section:
            self.section.enroll_student()

        return True

    def cancel(self):
        """
        Cancel an enrollment and free up section slot.

        Returns:
            bool: True if cancellation successful

        Raises:
            ValueError: If enrollment is already cancelled

        Example:
            ```python
            enrollment.cancel()
            # Status changed to CANCELLED, section slot freed
            ```
        """
        if self.status == self.EnrollmentStatus.CANCELLED:
            raise ValueError("Enrollment is already cancelled")

        old_status = self.status
        self.status = self.EnrollmentStatus.CANCELLED
        self.save(update_fields=['status'])

        # Free up section slot if was confirmed
        if old_status == self.EnrollmentStatus.CONFIRMED and self.section:
            self.section.drop_student()

        return True

    def is_confirmed(self):
        """
        Check if enrollment is confirmed.

        Returns:
            bool: True if status is CONFIRMED

        Example:
            ```python
            if enrollment.is_confirmed():
                # Include in student's schedule
            ```
        """
        return self.status == self.EnrollmentStatus.CONFIRMED

    def is_pending(self):
        """
        Check if enrollment is pending.

        Returns:
            bool: True if status is PENDING

        Example:
            ```python
            if enrollment.is_pending():
                # Show pending badge
            ```
        """
        return self.status == self.EnrollmentStatus.PENDING

    def has_grade(self):
        """
        Check if this enrollment has a grade record.

        Returns:
            bool: True if grade exists

        Example:
            ```python
            if enrollment.has_grade():
                # Display grade
            ```
        """
        return hasattr(self, 'grade') and self.grade is not None

    def get_grade(self):
        """
        Get the grade record for this enrollment.

        Returns:
            GradeRecord: Grade record, or None if not graded

        Example:
            ```python
            grade = enrollment.get_grade()
            if grade:
                print(grade.grade)
            ```
        """
        try:
            return self.grade
        except:
            return None

    def get_professor(self):
        """
        Get the professor teaching this subject in this section.

        Returns:
            User: Professor user, or None if no assignment

        Example:
            ```python
            prof = enrollment.get_professor()
            # Professor Smith
            ```
        """
        if not self.section:
            return None

        try:
            assignment = self.section.assigned_subjects.get(
                subject=self.subject,
                archived=False
            )
            return assignment.professor
        except:
            return None

    @classmethod
    def get_by_student_and_term(cls, student, term):
        """
        Get all enrollments for a student in a specific term.

        Args:
            student: Student object
            term: Term object

        Returns:
            QuerySet: Enrollment objects

        Example:
            ```python
            enrollments = Enrollment.get_by_student_and_term(student, fall_2024)
            # All enrollments for student in Fall 2024
            ```
        """
        return cls.objects.filter(
            student=student,
            term=term,
            archived=False
        ).select_related('subject', 'section', 'term')

    @classmethod
    def get_confirmed_by_section(cls, section):
        """
        Get all confirmed enrollments for a section.

        Args:
            section: Section object

        Returns:
            QuerySet: Confirmed enrollment objects

        Example:
            ```python
            enrollments = Enrollment.get_confirmed_by_section(bsit_1a)
            # All confirmed enrollments in BSIT-1A
            ```
        """
        return cls.objects.filter(
            section=section,
            status=cls.EnrollmentStatus.CONFIRMED,
            archived=False
        ).select_related('student', 'subject')
