"""
Academic Term Model

This module defines the Term model, which represents academic periods (semesters)
in the Richwell College Portal. Terms are used to organize courses, sections,
enrollments, and grades by academic period.

**Term Structure:**
- Each term represents one academic semester (e.g., "Fall 2024", "Spring 2025")
- Terms have start and end dates for enrollment and academic periods
- Only one term can be "active" for enrollment at a time
- Terms cannot be deleted (archive-first approach)

**Related Models:**
- Section: Each section belongs to a specific term
- Enrollment: Each enrollment is for a specific term
- GradeRecord: Each grade is associated with a term

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import TimeStampMixin, ArchiveMixin


class Term(ArchiveMixin, TimeStampMixin):
    """
    Represents an academic term/semester in the college system.

    A term is a discrete academic period (usually 4-5 months) during which
    courses are offered, students enroll, and grades are recorded.

    **Business Rules:**
    - Only ONE term can have is_active=True for enrollment at a time
    - Terms must not overlap in their date ranges
    - Term name must be unique (e.g., "Fall 2024")
    - enrollment_start must be before enrollment_end
    - term_start must be before term_end
    - Archived terms cannot be set as active

    **Fields:**
        name (str): Human-readable term name (e.g., "Fall 2024")
        slug (str): URL-friendly identifier (e.g., "fall-2024")
        term_start (date): First day of classes
        term_end (date): Last day of classes
        enrollment_start (date): When students can start enrolling
        enrollment_end (date): Last day to enroll in courses
        is_active (bool): True if this is the current enrollment term

    **Methods:**
        activate(): Make this the active enrollment term
        deactivate(): Remove active status from this term
        is_enrollment_open(): Check if enrollment is currently open
        is_in_session(): Check if classes are currently running

    **Example Usage:**
        ```python
        # Create a new term
        term = Term.objects.create(
            name="Fall 2024",
            slug="fall-2024",
            term_start=date(2024, 9, 1),
            term_end=date(2024, 12, 15),
            enrollment_start=date(2024, 7, 1),
            enrollment_end=date(2024, 9, 10)
        )

        # Activate for enrollment
        term.activate()

        # Check if enrollment is open
        if term.is_enrollment_open():
            # Allow students to enroll
            pass
        ```

    **Access Control:**
    - DEAN: Full read/write access, can create and activate terms
    - REGISTRAR: Full read/write access, can manage enrollments
    - ADMISSION: Read access, uses for enrollment processing
    - PROFESSOR: Read access only
    - STUDENT: Read access to active/upcoming terms only
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Term name (e.g., 'Fall 2024', 'Spring 2025')"
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier (auto-generated from name)"
    )

    term_start = models.DateField(
        help_text="First day of classes"
    )

    term_end = models.DateField(
        help_text="Last day of classes"
    )

    enrollment_start = models.DateField(
        help_text="When enrollment opens for this term"
    )

    enrollment_end = models.DateField(
        help_text="Last day students can enroll"
    )

    is_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True if this is the current enrollment term"
    )

    class Meta:
        ordering = ['-term_start']  # Newest first
        verbose_name = "Academic Term"
        verbose_name_plural = "Academic Terms"
        indexes = [
            models.Index(fields=['term_start', 'term_end']),
            models.Index(fields=['enrollment_start', 'enrollment_end']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validate term data before saving.

        Ensures:
        - Date ranges are logical (start before end)
        - Archived terms cannot be activated
        - Only one active term at a time

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        # Validate term date range
        if self.term_start and self.term_end:
            if self.term_start >= self.term_end:
                errors['term_end'] = 'Term end date must be after term start date.'

        # Validate enrollment date range
        if self.enrollment_start and self.enrollment_end:
            if self.enrollment_start >= self.enrollment_end:
                errors['enrollment_end'] = 'Enrollment end date must be after enrollment start date.'

        # Validate enrollment dates are before term dates
        if self.enrollment_end and self.term_end:
            if self.enrollment_end > self.term_end:
                errors['enrollment_end'] = 'Enrollment cannot end after the term ends.'

        # Cannot activate archived term
        if self.is_active and self.archived:
            errors['is_active'] = 'Cannot activate an archived term.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Save the term, enforcing business rules.

        If this term is being set as active, automatically deactivate
        all other terms to ensure only one active term exists.
        """
        # Run validation
        self.clean()

        # If setting this term as active, deactivate all others
        if self.is_active:
            Term.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)

        super().save(*args, **kwargs)

    def activate(self):
        """
        Make this term the active enrollment term.

        This method deactivates all other terms and sets this term as active.
        Only one term can be active at a time for enrollment.

        Raises:
            ValidationError: If term is archived

        Example:
            ```python
            fall_2024.activate()
            # Now fall_2024.is_active == True
            # All other terms have is_active == False
            ```
        """
        if self.archived:
            raise ValidationError("Cannot activate an archived term.")

        Term.objects.filter(is_active=True).update(is_active=False)
        self.is_active = True
        self.save(update_fields=['is_active'])

    def deactivate(self):
        """
        Remove active status from this term.

        Example:
            ```python
            fall_2024.deactivate()
            # Now fall_2024.is_active == False
            ```
        """
        self.is_active = False
        self.save(update_fields=['is_active'])

    def is_enrollment_open(self):
        """
        Check if enrollment is currently open for this term.

        Returns:
            bool: True if today is within the enrollment period and term is active

        Example:
            ```python
            if term.is_enrollment_open():
                # Allow student to enroll in courses
            ```
        """
        today = timezone.now().date()
        return (
            self.is_active and
            not self.archived and
            self.enrollment_start <= today <= self.enrollment_end
        )

    def is_in_session(self):
        """
        Check if classes are currently running for this term.

        Returns:
            bool: True if today is within the term dates

        Example:
            ```python
            if term.is_in_session():
                # Term is currently active, show current courses
            ```
        """
        today = timezone.now().date()
        return (
            not self.archived and
            self.term_start <= today <= self.term_end
        )

    def get_status(self):
        """
        Get human-readable status of this term.

        Returns:
            str: One of: "Upcoming", "Enrollment Open", "In Session", "Completed", "Archived"

        Example:
            ```python
            status = term.get_status()
            # "Enrollment Open" or "In Session", etc.
            ```
        """
        if self.archived:
            return "Archived"

        today = timezone.now().date()

        if today < self.enrollment_start:
            return "Upcoming"
        elif self.is_enrollment_open():
            return "Enrollment Open"
        elif self.is_in_session():
            return "In Session"
        elif today > self.term_end:
            return "Completed"
        else:
            return "Unknown"

    def get_duration(self):
        """
        Calculate the duration of the term in days.

        Returns:
            int: Number of days in the term
        """
        return (self.term_end - self.term_start).days

    def get_enrollment_stats(self):
        """
        Get enrollment statistics for this term.

        Returns:
            dict: Stats including total enrollments, students, sections

        Example:
            ```python
            stats = term.get_enrollment_stats()
            # {'total_enrollments': 450, 'total_students': 180, 'total_sections': 45}
            ```

        **Note:** Returns placeholder values until Enrollment model is implemented.
        """
        # TODO: Implement after Enrollment model is created
        return {
            'total_enrollments': 0,
            'total_students': 0,
            'total_sections': 0,
        }

    @classmethod
    def get_active_term(cls):
        """
        Get the currently active term for enrollment.

        Returns:
            Term or None: The active term, or None if no term is active

        Example:
            ```python
            active_term = Term.get_active_term()
            if active_term:
                # Show enrollment interface
            ```
        """
        return cls.objects.filter(is_active=True, archived=False).first()

    @classmethod
    def get_current_terms(cls):
        """
        Get all terms that are currently in session (classes running).

        Returns:
            QuerySet: Terms currently in their academic period

        Example:
            ```python
            current_terms = Term.get_current_terms()
            # [<Term: Fall 2024>]
            ```
        """
        today = timezone.now().date()
        return cls.objects.filter(
            archived=False,
            term_start__lte=today,
            term_end__gte=today
        )
