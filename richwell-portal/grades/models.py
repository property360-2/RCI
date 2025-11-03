from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from core.models import ArchiveMixin, TimeStampMixin


class GradeRecord(ArchiveMixin, TimeStampMixin):
    """
    Stores final encoded grades for each enrollment.
    One grade record per enrollment.
    """

    class Grade(models.TextChoices):
        ONE_ZERO = "1.0", "1.0 (Excellent)"
        ONE_FIVE = "1.5", "1.5"
        TWO_ZERO = "2.0", "2.0"
        TWO_FIVE = "2.5", "2.5"
        THREE_ZERO = "3.0", "3.0 (Passing)"
        FIVE_ZERO = "5.0", "5.0 (Failed)"
        INC = "INC", "Incomplete"
        DRP = "DRP", "Dropped"

    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade",
        help_text="Associated enrollment"
    )
    grade = models.CharField(
        max_length=10,
        choices=Grade.choices,
        help_text="Encoded grade"
    )
    encoded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="encoded_grades",
        help_text="Professor who encoded the grade"
    )
    encoded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the grade was encoded"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Additional remarks or notes"
    )

    class Meta:
        ordering = ["-encoded_at"]
        indexes = [
            models.Index(fields=["enrollment", "archived"]),
            models.Index(fields=["grade"]),
            models.Index(fields=["-encoded_at"]),
        ]

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.enrollment.subject.code}: {self.grade}"

    def is_passing(self):
        """Check if grade is passing."""
        return self.grade in [
            self.Grade.ONE_ZERO,
            self.Grade.ONE_FIVE,
            self.Grade.TWO_ZERO,
            self.Grade.TWO_FIVE,
            self.Grade.THREE_ZERO,
        ]


class INCRecord(TimeStampMixin):
    """
    Tracks incomplete (INC) grades and their resolution.
    Enforces 6-month (minor) or 12-month (major) deadlines.
    """

    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="inc_record",
        help_text="Associated enrollment with INC grade"
    )
    deadline = models.DateField(
        help_text="Deadline to resolve the INC"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the INC was resolved"
    )
    resolution_note = models.TextField(
        blank=True,
        help_text="Notes about INC resolution"
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_incs",
        help_text="Registrar who confirmed resolution"
    )
    expired = models.BooleanField(
        default=False,
        help_text="Whether the INC has expired"
    )

    class Meta:
        ordering = ["deadline"]
        indexes = [
            models.Index(fields=["deadline", "resolved_at"]),
            models.Index(fields=["expired"]),
        ]

    def __str__(self):
        status = "Resolved" if self.resolved_at else "Pending"
        return f"{self.enrollment.student.student_id} - {self.enrollment.subject.code}: {status}"

    def is_expired(self):
        """Check if INC deadline has passed."""
        return timezone.now().date() > self.deadline and not self.resolved_at

    def save(self, *args, **kwargs):
        """Auto-set deadline based on subject type if not provided."""
        if not self.deadline:
            subject = self.enrollment.subject
            # Major subjects: 12 months, Minor subjects: 6 months
            months = 12 if subject.subject_type == "MAJOR" else 6
            self.deadline = timezone.now().date() + timedelta(days=months * 30)
        super().save(*args, **kwargs)
