"""
Core Models and Mixins

This module provides reusable model mixins used across the Richwell College Portal.
These mixins implement the "archive-first" methodology and standardized timestamps
for all domain models.

**Design Philosophy:**
- Archive-first: Soft deletes for data preservation and audit trail
- Timestamp all changes: Created and updated timestamps on all records
- Consistent behavior: All models inherit the same archival and temporal patterns

**Mixins Available:**
- TimeStampMixin: Automatic created_at and updated_at timestamps
- ArchiveMixin: Soft delete functionality with archive/restore methods

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

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


class TimeStampMixin(models.Model):
    """
    Abstract base model that adds automatic timestamp fields to any model.

    This mixin provides:
    - created_at: Automatically set when record is first created
    - updated_at: Automatically updated whenever record is saved

    **Usage:**
        ```python
        class MyModel(TimeStampMixin):
            name = models.CharField(max_length=100)
            # created_at and updated_at are automatically added
        ```

    **Fields:**
        created_at (DateTimeField): Timestamp of record creation
        updated_at (DateTimeField): Timestamp of last modification

    **Notes:**
    - These fields are indexed for efficient querying
    - Timestamps use timezone-aware datetime (Django's TIME_ZONE setting)
    - updated_at is updated automatically on every save()
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when this record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="Timestamp when this record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']  # Default ordering: newest first

    def get_age(self):
        """
        Calculate how long ago this record was created.

        Returns:
            timedelta: Time elapsed since creation
        """
        return timezone.now() - self.created_at


class ArchiveMixin(models.Model):
    """
    Abstract base model that implements soft delete (archiving) functionality.

    This mixin provides the "archive-first" approach where records are never
    truly deleted from the database. Instead, they are marked as archived,
    preserving data integrity and enabling complete audit trails.

    **Features:**
    - Soft delete: Records marked as archived instead of deleted
    - Audit trail: Tracks who archived the record and when
    - Restore capability: Archived records can be restored
    - Query helpers: Manager methods to filter archived/active records

    **Usage:**
        ```python
        class Student(ArchiveMixin, TimeStampMixin):
            name = models.CharField(max_length=100)

        # Archive a student
        student.archive(archived_by=request.user)

        # Restore a student
        student.restore()

        # Query only active students
        active_students = Student.objects.filter(archived=False)
        ```

    **Fields:**
        archived (BooleanField): True if record is archived (soft deleted)
        archived_at (DateTimeField): When the record was archived
        archived_by (ForeignKey): User who archived the record

    **Methods:**
        archive(archived_by): Mark record as archived
        restore(): Restore archived record to active status

    **Important:**
    - Archived records are still in the database, just marked as inactive
    - Always filter by `archived=False` in queries unless you need archived data
    - Only specific roles (DEAN, REGISTRAR) can access archived data
    """

    archived = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True if this record has been archived (soft deleted)"
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Timestamp when this record was archived"
    )

    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_archived',
        help_text="User who archived this record"
    )

    class Meta:
        abstract = True

    def archive(self, archived_by=None):
        """
        Mark this record as archived (soft delete).

        This method sets the archived flag to True and records the timestamp
        and user who performed the archival. The record remains in the database
        but should be filtered out of normal queries.

        Args:
            archived_by (User, optional): The user performing the archival.
                                         Should be provided for audit trail.

        Returns:
            None

        Raises:
            ValueError: If record is already archived

        Example:
            ```python
            student.archive(archived_by=request.user)
            ```

        **Post-Archival Behavior:**
        - Record is marked as archived=True
        - archived_at timestamp is set to current time
        - archived_by is set to the user (if provided)
        - Related records may need to be handled (e.g., cascade archive)

        **Access Control:**
        Only these roles can archive records:
        - DEAN: Can archive all academic records
        - REGISTRAR: Can archive students, enrollments, grades
        - ADMIN: Can archive any record
        """
        if self.archived:
            raise ValueError(f"This {self.__class__.__name__} is already archived.")

        self.archived = True
        self.archived_at = timezone.now()
        self.archived_by = archived_by
        self.save(update_fields=['archived', 'archived_at', 'archived_by'])

    def restore(self):
        """
        Restore an archived record back to active status.

        This method reverses the archival process, making the record active
        again. The archived_at and archived_by fields are retained for
        audit purposes.

        Returns:
            None

        Raises:
            ValueError: If record is not archived

        Example:
            ```python
            student.restore()
            ```

        **Post-Restoration Behavior:**
        - archived flag is set to False
        - Record becomes visible in normal queries
        - archived_at and archived_by are NOT cleared (preserved for audit)

        **Access Control:**
        Only these roles can restore records:
        - DEAN: Can restore all academic records
        - REGISTRAR: Can restore students, enrollments, grades
        - ADMIN: Can restore any record
        """
        if not self.archived:
            raise ValueError(f"This {self.__class__.__name__} is not archived.")

        self.archived = False
        self.save(update_fields=['archived'])

    def is_archived(self):
        """
        Check if this record is currently archived.

        Returns:
            bool: True if archived, False if active
        """
        return self.archived

    def get_archive_info(self):
        """
        Get human-readable archive information.

        Returns:
            dict: Archive status information including who archived it and when

        Example:
            ```python
            info = student.get_archive_info()
            # {
            #     'is_archived': True,
            #     'archived_at': datetime(...),
            #     'archived_by': 'admin',
            #     'archived_duration': '5 days ago'
            # }
            ```
        """
        if not self.archived:
            return {'is_archived': False}

        return {
            'is_archived': True,
            'archived_at': self.archived_at,
            'archived_by': self.archived_by.username if self.archived_by else 'Unknown',
            'archived_duration': timezone.now() - self.archived_at if self.archived_at else None
        }
