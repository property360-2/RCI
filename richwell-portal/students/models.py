from django.db import models
from django.conf import settings
from core.models import ArchiveMixin, TimeStampMixin


class Student(ArchiveMixin, TimeStampMixin):
    """
    Student profile with enrollment information.
    Has one-to-one relationship with User model.
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
        related_name="student_profile"
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Student ID number"
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="students"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    year_level = models.PositiveIntegerField(
        default=1,
        help_text="Current year level (1-4)"
    )
    # JSON field for storing document references (future: Cloudinary/S3 URLs)
    documents = models.JSONField(
        default=dict,
        blank=True,
        help_text="Document metadata (birth cert, form 137, etc.)"
    )

    class Meta:
        ordering = ["student_id"]

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"
