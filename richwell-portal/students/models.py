"""
Student Model

This module defines the Student model, which represents student profiles and
academic records in the Richwell College Portal.

**Student Structure:**
- Each student has a one-to-one relationship with a User account
- Students belong to a specific course (degree program)
- Students have an academic status (Active, Irregular, LOA, Graduated, Dropped)
- Students track their year level and document submissions

**Related Models:**
- User: One-to-one relationship for authentication
- Course: The degree program the student is enrolled in
- Section: The class section the student belongs to
- Enrollment: Student enrollments in subjects
- GradeRecord: Student grades

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, Avg, Q
from core.models import ArchiveMixin, TimeStampMixin


class Student(ArchiveMixin, TimeStampMixin):
    """
    Represents a student profile with enrollment and academic information.

    A Student profile extends the User model with academic-specific fields
    such as student ID, course enrollment, academic status, and documents.

    **Business Rules:**
    - Student ID must be unique across all students
    - Only users with STUDENT role can have student profiles
    - Status changes must follow valid transitions
    - Year level must be between 1 and 5
    - Archived students cannot enroll in new subjects

    **Fields:**
        user (OneToOne): Link to User account
        student_id (str): Unique student ID number
        course (FK): The degree program the student is enrolled in
        status (str): Academic status (Active, Irregular, LOA, Graduated, Dropped)
        year_level (int): Current year level (1-5)
        documents (JSON): Document metadata and references

    **Methods:**
        get_current_enrollments(): Get enrollments for current term
        get_total_units(): Calculate total units enrolled
        can_enroll(): Check if student can enroll in new subjects
        get_gpa(): Calculate grade point average
        get_grades(): Get all grade records
        is_regular(): Check if student has regular status

    **Example Usage:**
        ```python
        # Create a student profile
        student = Student.objects.create(
            user=user_account,
            student_id="2024-001",
            course=bsit_course,
            status=Student.Status.ACTIVE,
            year_level=1
        )

        # Check enrollment eligibility
        if student.can_enroll():
            # Allow enrollment
            pass

        # Get current GPA
        gpa = student.get_gpa()
        ```

    **Access Control:**
    - DEAN: Full read access to all students
    - REGISTRAR: Full read/write access
    - ADMISSION: Create students, read access
    - PROFESSOR: Read access to students in their sections
    - STUDENT: Read access to own profile only
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        IRREGULAR = "IRREGULAR", "Irregular"
        LOA = "LOA", "Leave of Absence"
        GRADUATED = "GRADUATED", "Graduated"
        DROPPED = "DROPPED", "Dropped"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        help_text="Link to user account"
    )

    student_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique student ID number (e.g., '2024-001')"
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="students",
        help_text="The degree program the student is enrolled in"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        help_text="Current academic status"
    )

    year_level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Current year level (1-5)"
    )

    documents = models.JSONField(
        default=dict,
        blank=True,
        help_text="Document metadata (birth certificate, form 137, etc.)"
    )

    class Meta:
        ordering = ["student_id"]
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [
            models.Index(fields=['student_id', 'archived']),
            models.Index(fields=['course', 'year_level']),
            models.Index(fields=['status', 'archived']),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

    def clean(self):
        """
        Validate student data before saving.

        Ensures:
        - User has STUDENT role
        - Year level is valid for course duration
        - Status transitions are valid

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        if self.user and self.user.role != 'STUDENT':
            errors['user'] = 'User must have STUDENT role.'

        if self.year_level < 1 or self.year_level > 5:
            errors['year_level'] = 'Year level must be between 1 and 5.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Save student profile after validation."""
        self.clean()
        super().save(*args, **kwargs)

    def is_active(self):
        """
        Check if student has active status.

        Returns:
            bool: True if status is ACTIVE

        Example:
            ```python
            if student.is_active():
                # Allow enrollment
            ```
        """
        return self.status == self.Status.ACTIVE

    def is_regular(self):
        """
        Check if student has regular (non-irregular) status.

        Returns:
            bool: True if status is ACTIVE (not irregular)

        Example:
            ```python
            if student.is_regular():
                # Follow regular curriculum
            ```
        """
        return self.status == self.Status.ACTIVE

    def can_enroll(self):
        """
        Check if student can enroll in new subjects.

        Returns:
            tuple: (bool, str) - (can_enroll, reason)

        Example:
            ```python
            can_enroll, reason = student.can_enroll()
            if not can_enroll:
                print(reason)
            ```

        **Business Logic:**
        - Student must not be archived
        - Student must have ACTIVE or IRREGULAR status
        - Student cannot be on LOA, GRADUATED, or DROPPED
        """
        if self.archived:
            return (False, "Student profile is archived")

        if self.status in [self.Status.GRADUATED, self.Status.DROPPED]:
            return (False, f"Student status is {self.get_status_display()}")

        if self.status == self.Status.LOA:
            return (False, "Student is on Leave of Absence")

        return (True, "")

    def get_current_enrollments(self, term=None):
        """
        Get student's enrollments for current or specified term.

        Args:
            term (Term, optional): Specific term to filter by

        Returns:
            QuerySet: Enrollment objects

        Example:
            ```python
            enrollments = student.get_current_enrollments()
            # All enrollments for current term
            ```
        """
        from terms.models import Term
        if not term:
            term = Term.get_current_term()

        if not term:
            return self.enrollments.none()

        return self.enrollments.filter(
            term=term,
            archived=False
        )

    def get_total_units(self, term=None):
        """
        Calculate total credit units student is enrolled in.

        Args:
            term (Term, optional): Specific term to calculate for

        Returns:
            int: Total credit units

        Example:
            ```python
            units = student.get_total_units()
            # 24 units
            ```

        **Business Rule:** Maximum is 30 units per term
        """
        enrollments = self.get_current_enrollments(term)
        result = enrollments.filter(
            status='CONFIRMED'
        ).aggregate(total=Sum('units'))
        return result['total'] or 0

    def can_add_units(self, additional_units, term=None):
        """
        Check if student can add more units without exceeding cap.

        Args:
            additional_units (int): Units to add
            term (Term, optional): Term to check for

        Returns:
            tuple: (bool, str) - (can_add, reason)

        Example:
            ```python
            can_add, reason = student.can_add_units(3)
            if not can_add:
                print(reason)  # "Would exceed 30-unit cap"
            ```

        **Business Rule:** Students cannot exceed 30 units per term
        """
        current_units = self.get_total_units(term)
        new_total = current_units + additional_units

        if new_total > 30:
            return (False, f"Would exceed 30-unit cap (current: {current_units}, new: {new_total})")

        return (True, "")

    def get_grades(self, term=None):
        """
        Get all grade records for this student.

        Args:
            term (Term, optional): Filter by specific term

        Returns:
            QuerySet: GradeRecord objects

        Example:
            ```python
            grades = student.get_grades()
            # All grade records for student
            ```
        """
        from grades.models import GradeRecord
        enrollments = self.enrollments.filter(archived=False)

        if term:
            enrollments = enrollments.filter(term=term)

        return GradeRecord.objects.filter(
            enrollment__in=enrollments,
            archived=False
        )

    def get_gpa(self, term=None):
        """
        Calculate student's grade point average.

        Args:
            term (Term, optional): Calculate for specific term only

        Returns:
            float: GPA on 1.0-5.0 scale, or None if no grades

        Example:
            ```python
            gpa = student.get_gpa()
            # 2.3
            ```

        **Grading Scale:**
        - 1.0 = Excellent
        - 1.5 - 3.0 = Passing
        - 5.0 = Failed
        - INC/DRP excluded from calculation
        """
        grades = self.get_grades(term).exclude(grade__in=['INC', 'DRP'])
        if not grades.exists():
            return None

        grade_values = {
            '1.0': 1.0, '1.5': 1.5, '2.0': 2.0,
            '2.5': 2.5, '3.0': 3.0, '5.0': 5.0
        }

        total = 0
        count = 0
        for grade in grades:
            if grade.grade in grade_values:
                total += grade_values[grade.grade]
                count += 1

        return total / count if count > 0 else None

    def get_grade_for_subject(self, subject):
        """
        Get student's grade for a specific subject.

        Args:
            subject: Subject object

        Returns:
            GradeRecord: Grade record, or None if not found

        Example:
            ```python
            grade = student.get_grade_for_subject(comp101)
            if grade and grade.grade >= '3.0':
                # Student passed
            ```
        """
        from grades.models import GradeRecord
        try:
            enrollment = self.enrollments.get(
                subject=subject,
                archived=False
            )
            return GradeRecord.objects.get(
                enrollment=enrollment,
                archived=False
            )
        except:
            return None

    def has_passed_subject(self, subject):
        """
        Check if student has passed a specific subject.

        Args:
            subject: Subject object

        Returns:
            bool: True if student has passing grade

        Example:
            ```python
            if student.has_passed_subject(prerequisite):
                # Allow enrollment
            ```

        **Business Logic:** Passing grade is >= 3.0
        """
        grade_record = self.get_grade_for_subject(subject)
        if not grade_record:
            return False

        passing_grades = ['1.0', '1.5', '2.0', '2.5', '3.0']
        return grade_record.grade in passing_grades

    def get_inc_records(self):
        """
        Get all incomplete (INC) grade records.

        Returns:
            QuerySet: INCRecord objects

        Example:
            ```python
            incs = student.get_inc_records()
            # All incomplete grades
            ```
        """
        from grades.models import INCRecord
        enrollments = self.enrollments.filter(archived=False)
        return INCRecord.objects.filter(
            enrollment__in=enrollments,
            archived=False,
            resolved_at__isnull=True
        )

    def get_transcript(self):
        """
        Generate complete academic transcript.

        Returns:
            dict: Transcript data with all grades organized by term

        Example:
            ```python
            transcript = student.get_transcript()
            # {
            #   'student_id': '2024-001',
            #   'course': 'BSIT',
            #   'gpa': 2.3,
            #   'terms': [...]
            # }
            ```
        """
        grades = self.get_grades().select_related('enrollment__subject', 'enrollment__term')

        transcript = {
            'student_id': self.student_id,
            'name': self.user.get_full_name() or self.user.username,
            'course': self.course.code,
            'year_level': self.year_level,
            'status': self.get_status_display(),
            'gpa': self.get_gpa(),
            'terms': {}
        }

        for grade in grades:
            term_key = str(grade.enrollment.term)
            if term_key not in transcript['terms']:
                transcript['terms'][term_key] = []

            transcript['terms'][term_key].append({
                'subject_code': grade.enrollment.subject.code,
                'subject_name': grade.enrollment.subject.name,
                'units': grade.enrollment.units,
                'grade': grade.grade
            })

        return transcript

    @classmethod
    def get_by_course_and_year(cls, course, year_level):
        """
        Get all students for a specific course and year level.

        Args:
            course: Course object
            year_level: Year level (1-5)

        Returns:
            QuerySet: Students matching criteria

        Example:
            ```python
            first_years = Student.get_by_course_and_year(bsit_course, 1)
            # All 1st year BSIT students
            ```
        """
        return cls.objects.filter(
            course=course,
            year_level=year_level,
            archived=False
        ).order_by('student_id')
