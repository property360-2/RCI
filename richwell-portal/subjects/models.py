from django.db import models
from core.models import ArchiveMixin, TimeStampMixin


class Subject(ArchiveMixin, TimeStampMixin):
    """
    Represents an academic subject within a course/curriculum.
    """

    class SubjectType(models.TextChoices):
        MAJOR = "MAJOR", "Major"
        MINOR = "MINOR", "Minor"
        GE = "GE", "General Education"
        ELECTIVE = "ELECTIVE", "Elective"

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Subject code (e.g., CS101, MATH101)"
    )
    title = models.CharField(
        max_length=200,
        help_text="Subject title"
    )
    description = models.TextField(
        blank=True,
        help_text="Subject description"
    )
    units = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        help_text="Number of units (credit hours)"
    )
    subject_type = models.CharField(
        max_length=20,
        choices=SubjectType.choices,
        default=SubjectType.MAJOR,
        help_text="Type of subject"
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="subjects",
        help_text="Associated degree program"
    )
    year_level = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Recommended year level (1-4)"
    )
    semester = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Recommended semester (1ST, 2ND, SUMMER)"
    )
    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="required_for",
        help_text="Prerequisite subjects"
    )

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["course", "archived"]),
            models.Index(fields=["subject_type"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.title} ({self.units} units)"
