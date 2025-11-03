from django.db import models
from django.conf import settings
from core.models import ArchiveMixin, TimeStampMixin


class Section(ArchiveMixin, TimeStampMixin):
    """
    Represents a class section for a specific course and term.
    Has capacity limits and tracks available slots.
    """
    code = models.CharField(
        max_length=20,
        help_text="Section code (e.g., BSIT-1A, BSEd-2B)"
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="sections"
    )
    term = models.ForeignKey(
        "terms.Term",
        on_delete=models.CASCADE,
        related_name="sections"
    )
    capacity = models.PositiveIntegerField(
        default=40,
        help_text="Maximum number of students"
    )
    slots_remaining = models.PositiveIntegerField(
        default=40,
        help_text="Available enrollment slots"
    )

    class Meta:
        unique_together = ["code", "term"]
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} ({self.term})"


class AssignedSubject(ArchiveMixin, TimeStampMixin):
    """
    Links a subject to a section and assigns a professor to teach it.
    """
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="assigned_subjects"
    )
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "PROFESSOR"},
        related_name="teaching_assignments"
    )
    schedule = models.CharField(
        max_length=200,
        blank=True,
        help_text="Class schedule (e.g., MWF 9:00-10:00 AM)"
    )
    room = models.CharField(
        max_length=50,
        blank=True,
        help_text="Room assignment"
    )

    class Meta:
        unique_together = ["section", "subject"]
        ordering = ["section", "subject"]

    def __str__(self):
        return f"{self.subject.code} - {self.section.code} ({self.professor.username})"
