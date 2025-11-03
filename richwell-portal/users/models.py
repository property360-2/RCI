from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings


class User(AbstractUser):
    class Role(models.TextChoices):
        DEAN = "DEAN", "Dean"
        REGISTRAR = "REGISTRAR", "Registrar"
        ADMISSION = "ADMISSION", "Admission"
        PROFESSOR = "PROFESSOR", "Professor"
        STUDENT = "STUDENT", "Student"
        ADMIN = "ADMIN", "System Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )

    # Archive fields (soft delete)
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="archived_user_records"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def archive(self, user):
        """Mark user as archived (instead of deleting)."""
        self.archived = True
        self.archived_at = timezone.now()
        self.archived_by = user
        self.is_active = False
        self.save()

    def restore(self):
        """Restore archived user."""
        self.archived = False
        self.archived_at = None
        self.archived_by = None
        self.is_active = True
        self.save()

    def __str__(self):
        return f"{self.username} ({self.role})"
