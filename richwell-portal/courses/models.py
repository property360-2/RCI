from django.db import models
from core.models import ArchiveMixin, TimeStampMixin


class Course(ArchiveMixin, TimeStampMixin):
    """
    Represents a degree program (e.g., BSIT, BSEd, BSN).
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Course code (e.g., BSIT, BSEd)"
    )
    title = models.CharField(
        max_length=200,
        help_text="Full course title"
    )
    description = models.TextField(
        blank=True,
        help_text="Course description"
    )
    years = models.PositiveIntegerField(
        default=4,
        help_text="Number of years for the program"
    )

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["archived"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"
