from django.db import models
from core.models import TimeStampMixin


class Term(TimeStampMixin):
    """
    Represents an academic term (e.g., 2024-2025 1st Semester).
    Only one term can be active at a time.
    """

    class Semester(models.TextChoices):
        FIRST = "1ST", "1st Semester"
        SECOND = "2ND", "2nd Semester"
        SUMMER = "SUMMER", "Summer"

    school_year = models.CharField(
        max_length=20,
        help_text="Academic year (e.g., 2024-2025)"
    )
    semester = models.CharField(
        max_length=10,
        choices=Semester.choices,
        help_text="Semester type"
    )
    active = models.BooleanField(
        default=False,
        help_text="Only one term can be active at a time"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date of the term"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date of the term"
    )

    class Meta:
        ordering = ["-school_year", "-semester"]
        unique_together = ["school_year", "semester"]
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["-school_year"]),
        ]

    def __str__(self):
        return f"{self.school_year} {self.get_semester_display()}"

    def save(self, *args, **kwargs):
        """Ensure only one term is active at a time."""
        if self.active:
            Term.objects.filter(active=True).update(active=False)
        super().save(*args, **kwargs)
