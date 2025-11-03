from django.db import models
from core.models import ArchiveMixin, TimeStampMixin


class Course(ArchiveMixin, TimeStampMixin):
    """
    Represents a degree program (e.g., BSIT, BSEd, BSBA).
    Archived courses are hidden but can be restored.
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
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.title}"
