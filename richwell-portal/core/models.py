from django.db import models
from django.conf import settings
from django.utils import timezone


class TimeStampMixin(models.Model):
    """
    Abstract model to add created_at and updated_at timestamps to any model.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ArchiveMixin(models.Model):
    """
    Abstract model to enable soft-delete functionality (archive instead of delete).
    All models using this mixin will have archive/restore capabilities.
    """
    archived = models.BooleanField(default=False, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_archived"
    )

    class Meta:
        abstract = True

    def archive(self, user):
        """Mark record as archived (soft delete)."""
        self.archived = True
        self.archived_at = timezone.now()
        self.archived_by = user
        self.save()

    def restore(self):
        """Restore archived record."""
        self.archived = False
        self.archived_at = None
        self.archived_by = None
        self.save()
