from django.db import models
from django.conf import settings


class AuditTrail(models.Model):
    """
    Logs all significant actions (create, update, archive, restore) across the system.
    Stores old and new values in JSON format for complete audit trail.
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
        related_name="audit_logs"
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )
    table_name = models.CharField(
        max_length=100,
        help_text="Model/table name (e.g., 'students.Student')"
    )
    record_id = models.IntegerField(
        help_text="Primary key of the affected record"
    )
    old_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous state (for UPDATE/ARCHIVE)"
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
        help_text="New state (for CREATE/UPDATE/RESTORE)"
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["table_name", "record_id"]),
            models.Index(fields=["actor", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.actor.username} - {self.action} on {self.table_name}#{self.record_id}"
