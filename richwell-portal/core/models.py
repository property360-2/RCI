from django.db import models
from django.conf import settings


class TimeStampMixin(models.Model):
    """
    Abstract model mixin for automatic timestamping.
    Adds created_at and updated_at fields to any model that inherits from it.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ArchiveMixin(models.Model):
    """
    Abstract model mixin for soft-delete functionality.
    Instead of deleting records, mark them as archived with timestamp and user info.
    """
    archived = models.BooleanField(default=False, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_archived"
    )

    class Meta:
        abstract = True
