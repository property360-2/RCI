from django.db import models
from core.models import ArchiveMixin, TimeStampMixin


class Subject(ArchiveMixin, TimeStampMixin):
    """
    Represents an academic subject/course.
    Can have prerequisites (many-to-many relationship to other subjects).
    """
    class SubjectType(models.TextChoices):
        MINOR = "MINOR", "Minor Subject"
        MAJOR = "MAJOR", "Major Subject"
        GE = "GE", "General Education"

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="subjects"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Subject code (e.g., CS101, MATH101)"
    )
    title = models.CharField(max_length=200)
    units = models.PositiveIntegerField(default=3)
    subject_type = models.CharField(
        max_length=10,
        choices=SubjectType.choices,
        default=SubjectType.MINOR
    )
    description = models.TextField(blank=True)

    # Many-to-many relationship for prerequisites
    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="required_for"
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.title} ({self.units} units)"
