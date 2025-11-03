from django.db import models
from django.conf import settings
from core.models import ArchiveMixin, TimeStampMixin


class Section(ArchiveMixin, TimeStampMixin):
    """
    Represents a class section for a specific course and term.
    Manages student capacity and enrollment slots.
    """

    code = models.CharField(
        max_length=20,
        help_text="Section code (e.g., BSIT-1A, BSIT-2B)"
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="sections",
        help_text="Associated course/program"
    )
    term = models.ForeignKey(
        "terms.Term",
        on_delete=models.CASCADE,
        related_name="sections",
        help_text="Academic term"
    )
    year_level = models.PositiveIntegerField(
        help_text="Year level (1-4)"
    )
    capacity = models.PositiveIntegerField(
        default=40,
        help_text="Maximum number of students"
    )
    slots_remaining = models.PositiveIntegerField(
        default=40,
        help_text="Available enrollment slots"
    )
    adviser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advised_sections",
        limit_choices_to={"role": "PROFESSOR"},
        help_text="Section adviser (Professor)"
    )

    class Meta:
        ordering = ["course", "year_level", "code"]
        unique_together = ["code", "term"]
        indexes = [
            models.Index(fields=["course", "term", "archived"]),
            models.Index(fields=["term", "year_level"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.term}"

    def has_available_slots(self):
        """Check if section has available enrollment slots."""
        return self.slots_remaining > 0


class AssignedSubject(ArchiveMixin, TimeStampMixin):
    """
    Links a subject to a section with an assigned professor.
    Represents a specific class offering.
    """

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="assigned_subjects",
        help_text="Section this subject is assigned to"
    )
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.CASCADE,
        related_name="assignments",
        help_text="Subject being taught"
    )
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_assignments",
        limit_choices_to={"role": "PROFESSOR"},
        help_text="Professor teaching this subject"
    )
    schedule = models.JSONField(
        default=dict,
        blank=True,
        help_text="Class schedule (days, time, room)"
    )

    class Meta:
        ordering = ["section", "subject"]
        unique_together = ["section", "subject"]
        indexes = [
            models.Index(fields=["section", "archived"]),
            models.Index(fields=["professor", "archived"]),
        ]

    def __str__(self):
        return f"{self.subject.code} - {self.section.code}"
