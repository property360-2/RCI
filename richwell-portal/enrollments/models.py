from django.db import models
from django.core.exceptions import ValidationError
from core.models import ArchiveMixin, TimeStampMixin


class Enrollment(ArchiveMixin, TimeStampMixin):
    """
    Represents a student's enrollment in a subject for a specific term.
    Enforces 30-unit cap and manages section slots.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        DROPPED = "DROPPED", "Dropped"
        COMPLETED = "COMPLETED", "Completed"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Enrolled student"
    )
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Subject enrolled in"
    )
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
        help_text="Assigned section (nullable for irregular students)"
    )
    term = models.ForeignKey(
        "terms.Term",
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Academic term"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Enrollment status"
    )
    units = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        help_text="Number of units for this enrollment"
    )
    enrolled_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="processed_enrollments",
        help_text="Staff who processed the enrollment"
    )

    class Meta:
        ordering = ["-term", "student", "subject"]
        unique_together = ["student", "subject", "term"]
        indexes = [
            models.Index(fields=["student", "term", "archived"]),
            models.Index(fields=["section", "archived"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} ({self.term})"

    def clean(self):
        """Validate 30-unit cap per term."""
        if not self.pk:  # Only for new enrollments
            total_units = Enrollment.objects.filter(
                student=self.student,
                term=self.term,
                archived=False,
                status__in=[self.Status.PENDING, self.Status.CONFIRMED]
            ).aggregate(
                total=models.Sum("units")
            )["total"] or 0

            if total_units + float(self.units) > 30:
                raise ValidationError(
                    f"Total units ({total_units + float(self.units)}) exceeds 30-unit cap."
                )

    def save(self, *args, **kwargs):
        """Set units from subject and validate before saving."""
        if not self.units:
            self.units = self.subject.units
        self.clean()
        super().save(*args, **kwargs)
