"""
Section Model

This module defines the Section model, which represents class sections for specific
courses and terms in the Richwell College Portal.

**Section Structure:**
- A section is a class group (e.g., "BSIT-1A", "BSEd-2B") for a specific term
- Each section belongs to a course (degree program) and a term (school year/semester)
- Sections have capacity limits and track available enrollment slots
- Sections have multiple subjects assigned with professors

**Related Models:**
- Course: Each section belongs to a course
- Term: Sections exist within a specific term
- AssignedSubject: Links subjects and professors to sections
- Enrollment: Students enroll in sections
- Student: Multiple students belong to a section

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models import ArchiveMixin, TimeStampMixin


class Section(ArchiveMixin, TimeStampMixin):
    """
    Represents a class section for a specific course and term.

    A Section is a class group like "BSIT-1A" or "BSEd-2B" that groups students
    together for a specific academic term. Sections have capacity limits and
    track enrollment availability.

    **Business Rules:**
    - Section code must be unique within a term
    - Capacity must be at least 10 students
    - Slots remaining cannot exceed capacity
    - Sections cannot accept enrollments when full
    - Each section must have subjects assigned to it

    **Fields:**
        code (str): Section code (e.g., "BSIT-1A", "BSEd-2B")
        course (FK): The degree program this section belongs to
        term (FK): The academic term for this section
        capacity (int): Maximum number of students (default 40)
        slots_remaining (int): Available enrollment slots

    **Methods:**
        is_full(): Check if section has reached capacity
        can_accept_enrollment(): Check if section can accept new enrollments
        enroll_student(): Enroll a student and update available slots
        drop_student(): Remove a student and free up a slot
        get_enrolled_students(): Get all students in this section
        get_assigned_subjects(): Get all subjects assigned to this section

    **Example Usage:**
        ```python
        # Create a section
        section = Section.objects.create(
            code="BSIT-1A",
            course=bsit_course,
            term=fall_2024,
            capacity=40
        )

        # Check if section is full
        if not section.is_full():
            section.enroll_student(student)

        # Get all students in section
        students = section.get_enrolled_students()
        ```

    **Access Control:**
    - DEAN: Full read access
    - REGISTRAR: Full read/write access
    - ADMISSION: Create sections, read access
    - PROFESSOR: Read access to assigned sections
    - STUDENT: Read access to own section only
    """

    code = models.CharField(
        max_length=20,
        db_index=True,
        help_text="Section code (e.g., 'BSIT-1A', 'BSEd-2B')"
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="sections",
        help_text="The degree program this section belongs to"
    )

    term = models.ForeignKey(
        "terms.Term",
        on_delete=models.PROTECT,
        related_name="sections",
        help_text="The academic term for this section"
    )

    capacity = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(10)],
        help_text="Maximum number of students (minimum 10)"
    )

    slots_remaining = models.PositiveIntegerField(
        default=40,
        help_text="Available enrollment slots"
    )

    class Meta:
        unique_together = ["code", "term"]
        ordering = ["code"]
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        indexes = [
            models.Index(fields=['code', 'term', 'archived']),
            models.Index(fields=['course', 'term']),
        ]

    def __str__(self):
        return f"{self.code} ({self.term})"

    def clean(self):
        """
        Validate section data before saving.

        Ensures:
        - Slots remaining doesn't exceed capacity
        - Capacity is at least 10
        - Code follows naming convention

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        if self.slots_remaining > self.capacity:
            errors['slots_remaining'] = 'Slots remaining cannot exceed capacity.'

        if self.capacity < 10:
            errors['capacity'] = 'Capacity must be at least 10 students.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Save section, ensuring code is uppercase.
        Set slots_remaining to capacity if not specified.
        """
        self.code = self.code.upper()

        # Initialize slots_remaining to capacity if creating new section
        if not self.pk and self.slots_remaining == 40:  # Default value
            self.slots_remaining = self.capacity

        self.clean()
        super().save(*args, **kwargs)

    def is_full(self):
        """
        Check if section has reached maximum capacity.

        Returns:
            bool: True if section is at capacity

        Example:
            ```python
            if section.is_full():
                # Reject enrollment
            ```
        """
        return self.slots_remaining <= 0

    def can_accept_enrollment(self):
        """
        Check if section can accept new enrollments.

        Returns:
            tuple: (bool, str) - (can_accept, reason)

        Example:
            ```python
            can_accept, reason = section.can_accept_enrollment()
            if not can_accept:
                print(reason)
            ```

        **Business Logic:**
        - Section must not be archived
        - Section must have available slots
        - Term must be current or future (not past)
        """
        if self.archived:
            return (False, "Section is archived")

        if self.is_full():
            return (False, "Section is at full capacity")

        if not self.term.is_current() and not self.term.is_future():
            return (False, "Cannot enroll in past terms")

        return (True, "")

    def enroll_student(self):
        """
        Decrement available slots when a student enrolls.

        Returns:
            bool: True if enrollment successful

        Raises:
            ValueError: If section is full

        Example:
            ```python
            if section.enroll_student():
                # Create enrollment record
            ```

        **Note:** This only updates the slot count. Enrollment record
        must be created separately in the enrollments app.
        """
        if self.is_full():
            raise ValueError("Cannot enroll: section is at full capacity")

        self.slots_remaining -= 1
        self.save(update_fields=['slots_remaining'])
        return True

    def drop_student(self):
        """
        Increment available slots when a student drops.

        Example:
            ```python
            section.drop_student()
            # Slot is now available
            ```

        **Note:** This only updates the slot count. Enrollment record
        must be updated separately.
        """
        if self.slots_remaining < self.capacity:
            self.slots_remaining += 1
            self.save(update_fields=['slots_remaining'])

    def get_enrolled_students(self):
        """
        Get all students enrolled in this section.

        Returns:
            QuerySet: Students in this section

        Example:
            ```python
            students = section.get_enrolled_students()
            # [<Student: 2024-001>, <Student: 2024-002>, ...]
            ```
        """
        from students.models import Student
        enrollment_student_ids = self.enrollments.filter(
            archived=False,
            status='CONFIRMED'
        ).values_list('student_id', flat=True)
        return Student.objects.filter(id__in=enrollment_student_ids)

    def get_enrollment_count(self):
        """
        Get count of enrolled students.

        Returns:
            int: Number of enrolled students

        Example:
            ```python
            count = section.get_enrollment_count()
            # 35 students enrolled
            ```
        """
        return self.enrollments.filter(
            archived=False,
            status='CONFIRMED'
        ).count()

    def get_assigned_subjects(self):
        """
        Get all subjects assigned to this section.

        Returns:
            QuerySet: AssignedSubject objects

        Example:
            ```python
            subjects = section.get_assigned_subjects()
            # [<AssignedSubject: COMP101 - BSIT-1A>, ...]
            ```
        """
        return self.assigned_subjects.filter(archived=False)

    def get_total_units(self):
        """
        Calculate total units for all subjects in this section.

        Returns:
            int: Total credit units

        Example:
            ```python
            units = section.get_total_units()
            # 24 units
            ```
        """
        from django.db.models import Sum
        result = self.assigned_subjects.filter(
            archived=False
        ).aggregate(total=Sum('subject__units'))
        return result['total'] or 0

    @classmethod
    def get_by_course_and_term(cls, course, term):
        """
        Get all sections for a specific course and term.

        Args:
            course: Course object
            term: Term object

        Returns:
            QuerySet: Sections for that course and term

        Example:
            ```python
            sections = Section.get_by_course_and_term(bsit_course, fall_2024)
            # All BSIT sections for Fall 2024
            ```
        """
        return cls.objects.filter(
            course=course,
            term=term,
            archived=False
        ).order_by('code')


class AssignedSubject(ArchiveMixin, TimeStampMixin):
    """
    Links a subject to a section and assigns a professor to teach it.

    An AssignedSubject represents the assignment of a subject (e.g., COMP101)
    to a specific section (e.g., BSIT-1A) with a professor instructor.
    It includes scheduling and room information.

    **Business Rules:**
    - Each subject can only be assigned once per section
    - Only users with PROFESSOR role can be assigned
    - Schedule should follow standard format (e.g., "MWF 9:00-10:00 AM")
    - Room assignments should not conflict (same room, same time)

    **Fields:**
        section (FK): The section this assignment belongs to
        subject (FK): The subject being taught
        professor (FK): The professor teaching this subject
        schedule (str): Class schedule (e.g., "MWF 9:00-10:00 AM")
        room (str): Room assignment (e.g., "Room 301", "Lab A")

    **Methods:**
        get_enrolled_students(): Get students enrolled in this subject-section
        get_grades(): Get all grades for this assignment
        has_schedule_conflict(): Check for scheduling conflicts

    **Example Usage:**
        ```python
        # Assign a subject to a section
        assignment = AssignedSubject.objects.create(
            section=bsit_1a,
            subject=comp101,
            professor=prof_smith,
            schedule="MWF 9:00-10:00 AM",
            room="Room 301"
        )

        # Get all students in this subject
        students = assignment.get_enrolled_students()
        ```

    **Access Control:**
    - DEAN: Full read access
    - REGISTRAR: Full read/write access
    - PROFESSOR: Read/write for own assignments
    - STUDENT: Read access to own assignments
    """

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="assigned_subjects",
        help_text="The section this subject is assigned to"
    )

    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.PROTECT,
        related_name="assignments",
        help_text="The subject being taught"
    )

    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={"role": "PROFESSOR"},
        related_name="teaching_assignments",
        help_text="The professor teaching this subject"
    )

    schedule = models.CharField(
        max_length=200,
        blank=True,
        help_text="Class schedule (e.g., 'MWF 9:00-10:00 AM', 'TTh 1:00-2:30 PM')"
    )

    room = models.CharField(
        max_length=50,
        blank=True,
        help_text="Room assignment (e.g., 'Room 301', 'Lab A')"
    )

    class Meta:
        unique_together = ["section", "subject"]
        ordering = ["section", "subject"]
        verbose_name = "Assigned Subject"
        verbose_name_plural = "Assigned Subjects"
        indexes = [
            models.Index(fields=['section', 'archived']),
            models.Index(fields=['professor', 'archived']),
            models.Index(fields=['subject', 'section']),
        ]

    def __str__(self):
        return f"{self.subject.code} - {self.section.code} ({self.professor.username})"

    def clean(self):
        """
        Validate assigned subject data before saving.

        Ensures:
        - Professor has PROFESSOR role
        - Subject belongs to same course as section
        - No duplicate assignments

        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        if self.professor and self.professor.role != 'PROFESSOR':
            errors['professor'] = 'Assigned user must have PROFESSOR role.'

        if self.section and self.subject:
            if self.subject.course != self.section.course:
                errors['subject'] = 'Subject must belong to the same course as the section.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Save assignment after validation."""
        self.clean()
        super().save(*args, **kwargs)

    def get_enrolled_students(self):
        """
        Get all students enrolled in this specific subject-section combination.

        Returns:
            QuerySet: Students enrolled in this assignment

        Example:
            ```python
            students = assignment.get_enrolled_students()
            # All students taking COMP101 in BSIT-1A
            ```
        """
        from students.models import Student
        enrollment_student_ids = self.section.enrollments.filter(
            subject=self.subject,
            archived=False,
            status='CONFIRMED'
        ).values_list('student_id', flat=True)
        return Student.objects.filter(id__in=enrollment_student_ids)

    def get_enrollment_count(self):
        """
        Get count of students enrolled in this subject-section.

        Returns:
            int: Number of enrolled students

        Example:
            ```python
            count = assignment.get_enrollment_count()
            # 35 students
            ```
        """
        return self.section.enrollments.filter(
            subject=self.subject,
            archived=False,
            status='CONFIRMED'
        ).count()

    def get_grades(self):
        """
        Get all grade records for this assignment.

        Returns:
            QuerySet: GradeRecord objects

        Example:
            ```python
            grades = assignment.get_grades()
            # All grades for COMP101 in BSIT-1A
            ```
        """
        from grades.models import GradeRecord
        enrollments = self.section.enrollments.filter(
            subject=self.subject,
            archived=False
        )
        return GradeRecord.objects.filter(
            enrollment__in=enrollments,
            archived=False
        )

    def get_average_grade(self):
        """
        Calculate average grade for this assignment.

        Returns:
            float: Average grade, or None if no grades

        Example:
            ```python
            avg = assignment.get_average_grade()
            # 2.5
            ```
        """
        grades = self.get_grades().exclude(grade__in=['INC', 'DRP'])
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

    def has_schedule_conflict(self):
        """
        Check if this assignment has a schedule conflict with other assignments.

        Returns:
            bool: True if conflict exists

        Example:
            ```python
            if assignment.has_schedule_conflict():
                # Warn user about conflict
            ```

        **Note:** Basic implementation. Can be enhanced to parse schedule
        and check for actual time overlaps.
        """
        if not self.schedule or not self.room:
            return False

        conflicts = AssignedSubject.objects.filter(
            section__term=self.section.term,
            schedule=self.schedule,
            room=self.room,
            archived=False
        ).exclude(pk=self.pk)

        return conflicts.exists()
