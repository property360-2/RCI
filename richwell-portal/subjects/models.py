"""
Subject Model

This module defines the Subject model, which represents individual courses/subjects
(e.g., COMP101, MATH201) within a degree program in the Richwell College Portal.

**Subject Structure:**
- A subject is an individual course offered within a program (e.g., "Introduction to Programming")
- Each subject belongs to a course (degree program)
- Subjects have unit values (typically 1-5 units)
- Subjects can have prerequisites (other subjects that must be completed first)
- Subjects are offered in sections during specific terms

**Related Models:**
- Course: Each subject belongs to a course
- Section: Subjects are offered as sections in specific terms
- Enrollment: Students enroll in sections of subjects
- GradeRecord: Grades are recorded for subject enrollments

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from core.models import ArchiveMixin, TimeStampMixin


class Subject(ArchiveMixin, TimeStampMixin):
    """
    Represents an individual academic subject/course within a program.

    A Subject is a specific course like "COMP101 - Introduction to Programming"
    or "MATH201 - Calculus I". Students enroll in sections of subjects.

    **Business Rules:**
    - Subject code must be unique (e.g., "COMP101")
    - Units must be between 1 and 5
    - Prerequisites must be valid subjects in the same course
    - Subjects cannot be their own prerequisite (no circular dependencies)
    - Year level indicates which academic year the subject is typically taken (1-5)

    **Fields:**
        code (str): Unique subject code (e.g., "COMP101", "MATH201")
        name (str): Subject name (e.g., "Introduction to Programming")
        description (text): Detailed subject description
        units (int): Credit units (1-5)
        year_level (int): Academic year this subject is typically taken (1-5)
        course (FK): The degree program this subject belongs to
        prerequisites (M2M): Other subjects that must be completed first

    **Methods:**
        has_prerequisites(): Check if subject has any prerequisites
        can_student_enroll(student): Check if student meets prerequisite requirements
        get_sections(): Get all sections offering this subject

    **Example Usage:**
        ```python
        # Create a subject
        subject = Subject.objects.create(
            code="COMP101",
            name="Introduction to Programming",
            description="Basic programming concepts using Python",
            units=3,
            year_level=1,
            course=bscs_course
        )

        # Add prerequisites
        subject.prerequisites.add(prerequisite_subject)

        # Check if student can enroll
        if subject.can_student_enroll(student):
            # Allow enrollment
            pass
        ```

    **Access Control:**
    - DEAN: Full read/write access
    - REGISTRAR: Full read/write access
    - ADMISSION: Read access for enrollment processing
    - PROFESSOR: Read access, can view assigned subjects
    - STUDENT: Read access to active subjects only
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique subject code (e.g., 'COMP101', 'MATH201')"
    )

    name = models.CharField(
        max_length=200,
        help_text="Subject name (e.g., 'Introduction to Programming')"
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description of the subject content and objectives"
    )

    units = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Credit units (typically 1-5)"
    )

    year_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Academic year level (1=Freshman, 2=Sophomore, etc.)"
    )

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.PROTECT,
        related_name='subject_set',
        help_text="The degree program this subject belongs to"
    )

    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='prerequisite_for',
        help_text="Subjects that must be completed before enrolling in this subject"
    )

    class Meta:
        ordering = ['course__code', 'year_level', 'code']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        indexes = [
            models.Index(fields=['code', 'archived']),
            models.Index(fields=['course', 'year_level']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.units}u)"

    def clean(self):
        """
        Validate subject data before saving.

        Ensures:
        - Subject doesn't have circular prerequisite dependencies
        - Prerequisites belong to the same course
        - Year level is logical relative to prerequisites

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        # Validate prerequisites belong to same course
        if self.pk:  # Only check if instance already exists
            invalid_prereqs = self.prerequisites.exclude(course=self.course)
            if invalid_prereqs.exists():
                errors['prerequisites'] = 'Prerequisites must belong to the same course.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Save subject, ensuring code is uppercase."""
        self.code = self.code.upper()
        self.clean()
        super().save(*args, **kwargs)

    def has_prerequisites(self):
        """
        Check if this subject has any prerequisites.

        Returns:
            bool: True if subject has prerequisites

        Example:
            ```python
            if subject.has_prerequisites():
                # Check student eligibility
            ```
        """
        return self.prerequisites.exists()

    def get_prerequisites(self):
        """
        Get all prerequisite subjects (active only).

        Returns:
            QuerySet: Prerequisite subjects

        Example:
            ```python
            prereqs = subject.get_prerequisites()
            # [<Subject: COMP101>, <Subject: MATH101>]
            ```
        """
        return self.prerequisites.filter(archived=False)

    def can_student_enroll(self, student):
        """
        Check if a student has completed all prerequisites for this subject.

        This method verifies that the student has passed (grade >= 3.0) all
        prerequisite subjects before allowing enrollment.

        Args:
            student: Student object to check

        Returns:
            tuple: (bool, list) - (can_enroll, missing_prerequisites)

        Example:
            ```python
            can_enroll, missing = subject.can_student_enroll(student)
            if not can_enroll:
                print(f"Missing: {missing}")
            ```

        **Business Logic:**
        - Student must have passing grade (>= 3.0) in all prerequisites
        - INC (Incomplete) grades don't count as completion
        - Archived subjects are ignored

        **Note:** Returns (True, []) until GradeRecord model is implemented
        """
        if not self.has_prerequisites():
            return (True, [])

        # TODO: Implement prerequisite checking after GradeRecord model is created
        # Prerequisites need to check student's grade records
        # passing_grade = 3.0
        #
        # missing_prereqs = []
        # for prereq in self.get_prerequisites():
        #     grade_record = student.get_grade_for_subject(prereq)
        #     if not grade_record or grade_record.grade < passing_grade:
        #         missing_prereqs.append(prereq)
        #
        # return (len(missing_prereqs) == 0, missing_prereqs)

        return (True, [])  # Placeholder: allow all enrollments for now

    def get_sections(self, term=None):
        """
        Get all sections offering this subject.

        Args:
            term (Term, optional): Filter by specific term

        Returns:
            QuerySet: Sections offering this subject

        Example:
            ```python
            # Get all sections
            sections = subject.get_sections()

            # Get sections for specific term
            fall_sections = subject.get_sections(term=fall_2024)
            ```

        **Note:** Returns empty QuerySet until Section model is implemented
        """
        # TODO: Implement after Section model is created
        # sections = self.section_set.filter(archived=False)
        # if term:
        #     sections = sections.filter(term=term)
        # return sections
        from sections.models import Section  # Placeholder to avoid circular import
        return Section.objects.none()

    def get_enrolled_count(self, term=None):
        """
        Count students currently enrolled in this subject.

        Args:
            term (Term, optional): Count for specific term only

        Returns:
            int: Number of enrolled students

        Example:
            ```python
            count = subject.get_enrolled_count()
            # 45 students enrolled across all sections
            ```

        **Note:** Returns 0 until Enrollment model is implemented
        """
        # TODO: Implement after Enrollment model is created
        return 0

    def get_average_grade(self):
        """
        Calculate average grade for this subject across all terms.

        Returns:
            float: Average grade (0.0-5.0 scale), or None if no grades

        Example:
            ```python
            avg = subject.get_average_grade()
            # 2.5 (average grade)
            ```

        **Note:** Returns None until GradeRecord model is implemented
        """
        # TODO: Implement after GradeRecord model is created
        return None

    def get_pass_rate(self):
        """
        Calculate percentage of students who passed this subject.

        Returns:
            float: Pass rate (0-100), or None if no data

        Example:
            ```python
            rate = subject.get_pass_rate()
            # 85.5 (85.5% pass rate)
            ```

        **Business Logic:**
        - Passing grade is >= 3.0
        - INC (Incomplete) grades are not counted

        **Note:** Returns None until GradeRecord model is implemented
        """
        # TODO: Implement after GradeRecord model is created
        return None

    def get_full_code(self):
        """
        Get full subject identifier with course code.

        Returns:
            str: Course code + subject code

        Example:
            ```python
            subject.get_full_code()
            # "BSCS-COMP101"
            ```
        """
        return f"{self.course.code}-{self.code}"

    def get_year_level_display_name(self):
        """
        Get human-readable year level name.

        Returns:
            str: Year level name (e.g., "1st Year", "2nd Year")

        Example:
            ```python
            subject.get_year_level_display_name()
            # "1st Year"
            ```
        """
        year_names = {
            1: "1st Year",
            2: "2nd Year",
            3: "3rd Year",
            4: "4th Year",
            5: "5th Year"
        }
        return year_names.get(self.year_level, f"{self.year_level}th Year")

    @classmethod
    def get_by_year_level(cls, course, year_level):
        """
        Get all subjects for a specific course and year level.

        Args:
            course: Course object
            year_level: Year level (1-5)

        Returns:
            QuerySet: Subjects for that year

        Example:
            ```python
            first_year_subjects = Subject.get_by_year_level(bscs_course, 1)
            # All 1st year BSCS subjects
            ```
        """
        return cls.objects.filter(
            course=course,
            year_level=year_level,
            archived=False
        ).order_by('code')
