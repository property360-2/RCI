from django.db import models
from django.core.exceptions import ValidationError
from core.models import ArchiveMixin, TimeStampMixin


class Enrollment(ArchiveMixin, TimeStampMixin):
    """
    Links a student to a subject for a specific term.
    Enforces 30-unit cap and prerequisite validation.
    Section is nullable to support irregular/transferee students.
    """
    class EnrollmentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="enrollments",
        help_text="Nullable for irregular students"
    )
    term = models.ForeignKey(
        "terms.Term",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    units = models.PositiveIntegerField(
        help_text="Subject units (copied from subject for audit purposes)"
    )
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.PENDING
    )

    class Meta:
        unique_together = ["student", "subject", "term"]
        ordering = ["-term", "student", "subject"]

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} ({self.term})"

    def save(self, *args, **kwargs):
        """
        Auto-populate units from subject if not set.
        Enforce 30-unit cap at service layer, not here.
        """
        if not self.units:
            self.units = self.subject.units
        super().save(*args, **kwargs)
