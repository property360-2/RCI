from django.db import models
from django.conf import settings
from core.models import ArchiveMixin, TimeStampMixin


class Student(ArchiveMixin, TimeStampMixin):
    """
    Represents a student profile linked to a User account.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        GRADUATED = "GRADUATED", "Graduated"
        DROPPED = "DROPPED", "Dropped"
        LOA = "LOA", "Leave of Absence"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        help_text="Linked user account"
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique student ID number"
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="students",
        help_text="Enrolled degree program"
    )
    year_level = models.PositiveIntegerField(
        default=1,
        help_text="Current year level (1-4)"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text="Current enrollment status"
    )
    documents = models.JSONField(
        default=dict,
        blank=True,
        help_text="Student documents (JSON field for future CDN/S3 URLs)"
    )
    date_enrolled = models.DateField(
        null=True,
        blank=True,
        help_text="Date first enrolled"
    )
    date_graduated = models.DateField(
        null=True,
        blank=True,
        help_text="Date graduated (if applicable)"
    )
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Student contact number"
    )
    address = models.TextField(
        blank=True,
        help_text="Student address"
    )

    class Meta:
        ordering = ["student_id"]
        indexes = [
            models.Index(fields=["student_id"]),
            models.Index(fields=["course", "archived"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"
