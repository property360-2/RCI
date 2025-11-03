from django.db import models
from django.conf import settings


class AuditTrail(models.Model):
    """
    Audit trail for tracking all CRUD operations across the system.
    Logs actor, action type, affected table and record, and value changes.
    """

    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        ARCHIVE = "ARCHIVE", "Archive"
        RESTORE = "RESTORE", "Restore"
        DELETE = "DELETE", "Delete"
        POLICY_EXPIRE = "POLICY_EXPIRE", "Policy Expire"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        help_text="Type of action performed"
    )
    table_name = models.CharField(
        max_length=100,
        help_text="Name of the affected database table"
    )
    record_id = models.IntegerField(
        help_text="ID of the affected record"
    )
    old_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous state of the record (for updates)"
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
        help_text="New state of the record"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the actor"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Browser/client user agent"
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["table_name", "record_id"]),
            models.Index(fields=["actor", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.actor.username} - {self.action} on {self.table_name}:{self.record_id} at {self.timestamp}"
