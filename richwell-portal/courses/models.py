"""
Course Model

This module defines the Course model, which represents academic programs (e.g., BS Computer Science,
BS Business Administration) in the Richwell College Portal.

**Course Structure:**
- A course is a complete academic program (degree program)
- Each course has multiple subjects (COMP101, MATH201, etc.)
- Courses are organized by code and name
- Courses use archive-first approach (never truly deleted)

**Related Models:**
- Subject: Each subject belongs to a course (e.g., COMP101 belongs to BS Computer Science)
- Student: Each student is enrolled in one course

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.db import models
from django.core.validators import MinValueValidator
from core.models import TimeStampMixin, ArchiveMixin


class Course(ArchiveMixin, TimeStampMixin):
    """
    Represents an academic program/degree offered by the college.

    A Course is a complete degree program (e.g., "BS Computer Science",
    "BA Psychology"). It contains multiple subjects that students must
    complete to earn the degree.

    **Business Rules:**
    - Course code must be unique (e.g., "BSCS", "BSBA")
    - Course name must be unique
    - Total units represents the full curriculum units required for graduation
    - Archived courses cannot accept new enrollments but existing students continue
    - Course code should be uppercase and alphanumeric

    **Fields:**
        code (str): Unique course code (e.g., "BSCS", "BSBA")
        name (str): Full course name (e.g., "Bachelor of Science in Computer Science")
        description (text): Detailed description of the program
        total_units (int): Total units required to graduate
        years_to_complete (int): Expected years to complete the program

    **Methods:**
        get_subjects(): Get all subjects belonging to this course
        get_student_count(): Count students enrolled in this course
        get_completion_rate(): Calculate graduation rate

    **Example Usage:**
        ```python
        # Create a new course
        course = Course.objects.create(
            code="BSCS",
            name="Bachelor of Science in Computer Science",
            description="A 4-year program focusing on software development...",
            total_units=120,
            years_to_complete=4
        )

        # Get all subjects in this course
        subjects = course.get_subjects()
        ```

    **Access Control:**
    - DEAN: Full read/write access, can create/archive courses
    - REGISTRAR: Full read/write access
    - ADMISSION: Read access for enrollment processing
    - PROFESSOR: Read access only
    - STUDENT: Read access to active courses only
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique course code (e.g., 'BSCS', 'BSBA')"
    )

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Full course name (e.g., 'Bachelor of Science in Computer Science')"
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description of the academic program"
    )

    total_units = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total units required to graduate from this program"
    )

    years_to_complete = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        help_text="Expected number of years to complete the program"
    )

    class Meta:
        ordering = ['code']
        verbose_name = "Course (Degree Program)"
        verbose_name_plural = "Courses (Degree Programs)"
        indexes = [
            models.Index(fields=['code', 'archived']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        """Save course, ensuring code is uppercase."""
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def get_subjects(self):
        """
        Get all subjects belonging to this course.

        Returns:
            QuerySet: All subjects in this course (active only by default)

        Example:
            ```python
            course = Course.objects.get(code="BSCS")
            subjects = course.get_subjects()
            # [<Subject: COMP101>, <Subject: COMP102>, ...]
            ```
        """
        return self.subject_set.filter(archived=False).order_by('code')

    def get_all_subjects(self):
        """
        Get all subjects including archived ones.

        Returns:
            QuerySet: All subjects (including archived)

        **Access Control:** Only DEAN and REGISTRAR can access archived data
        """
        return self.subject_set.all().order_by('code')

    def get_student_count(self):
        """
        Count active students enrolled in this course.

        Returns:
            int: Number of active students in this program

        Example:
            ```python
            count = course.get_student_count()
            # 180
            ```

        **Note:** Returns 0 until Student model is implemented
        """
        # TODO: Implement after Student model is created
        # return self.student_set.filter(archived=False).count()
        return 0

    def get_completion_rate(self):
        """
        Calculate the graduation/completion rate for this course.

        Returns:
            float: Percentage of students who completed (0-100)

        Example:
            ```python
            rate = course.get_completion_rate()
            # 85.5 (85.5% graduation rate)
            ```

        **Note:** Returns 0.0 until Student model has graduation tracking
        """
        # TODO: Implement graduation tracking
        return 0.0

    def get_subject_count(self):
        """
        Count total subjects in this course.

        Returns:
            int: Number of subjects (active only)
        """
        return self.subject_set.filter(archived=False).count()

    def get_short_name(self):
        """
        Get abbreviated course name.

        Returns:
            str: Course code and first part of name

        Example:
            ```python
            course.get_short_name()
            # "BSCS - Bachelor of Science"
            ```
        """
        name_parts = self.name.split(' in ')
        return f"{self.code} - {name_parts[0]}" if len(name_parts) > 1 else f"{self.code} - {self.name[:30]}"
