from django.db import models
from core.models import TimeStampMixin


class Term(TimeStampMixin):
    """
    Represents an academic term (school year + semester).
    Example: 2024-2025, First Semester
    """
    class Semester(models.TextChoices):
        FIRST = "FIRST", "First Semester"
        SECOND = "SECOND", "Second Semester"
        SUMMER = "SUMMER", "Summer"

    school_year = models.CharField(
        max_length=20,
        help_text="Format: YYYY-YYYY (e.g., 2024-2025)"
    )
    semester = models.CharField(
        max_length=10,
        choices=Semester.choices
    )
    active = models.BooleanField(
        default=False,
        help_text="Only one term can be active at a time"
    )

    class Meta:
        unique_together = ["school_year", "semester"]
        ordering = ["-school_year", "-semester"]

    def __str__(self):
        return f"{self.school_year} - {self.get_semester_display()}"

    def save(self, *args, **kwargs):
        """Ensure only one term is active at a time."""
        if self.active:
            Term.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)
