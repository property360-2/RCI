from django.db import models
from django.conf import settings
from core.models import ArchiveMixin, TimeStampMixin


class GradeRecord(ArchiveMixin, TimeStampMixin):
    """
    Stores the final grade for an enrollment.
    One-to-one relationship with Enrollment.
    """
    class Grade(models.TextChoices):
        ONE_ZERO = "1.0", "1.0"
        ONE_FIVE = "1.5", "1.5"
        TWO_ZERO = "2.0", "2.0"
        TWO_FIVE = "2.5", "2.5"
        THREE_ZERO = "3.0", "3.0"
        FIVE_ZERO = "5.0", "5.0 (Failed)"
        INC = "INC", "Incomplete"
        DRP = "DRP", "Dropped"

    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade"
    )
    grade = models.CharField(
        max_length=5,
        choices=Grade.choices
    )
    encoded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role": "PROFESSOR"},
        related_name="encoded_grades"
    )
    encoded_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-encoded_at"]

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.enrollment.subject.code}: {self.grade}"


class INCRecord(ArchiveMixin, TimeStampMixin):
    """
    Tracks incomplete (INC) grades with deadlines and resolution.
    Minor subjects: 6 months, Major subjects: 12 months.
    """
    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="inc_record"
    )
    deadline = models.DateField(
        help_text="Deadline to complete requirements (6 or 12 months)"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(
        blank=True,
        help_text="How the INC was resolved"
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "REGISTRAR"},
        related_name="confirmed_incs"
    )

    class Meta:
        ordering = ["deadline"]

    def __str__(self):
        status = "Resolved" if self.resolved_at else "Pending"
        return f"{self.enrollment.student.student_id} - {self.enrollment.subject.code} (INC - {status})"
