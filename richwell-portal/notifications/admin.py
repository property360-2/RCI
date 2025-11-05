"""Admin configuration for notifications app."""

from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""

    list_display = [
        'recipient',
        'notification_type',
        'title',
        'is_read',
        'sent_via_email',
        'created_at'
    ]

    list_filter = [
        'notification_type',
        'is_read',
        'sent_via_email',
        'created_at',
        'archived'
    ]

    search_fields = [
        'recipient__username',
        'recipient__email',
        'recipient__first_name',
        'recipient__last_name',
        'title',
        'message'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'read_at',
        'email_sent_at'
    ]

    fieldsets = (
        ('Recipient', {
            'fields': ('recipient', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'message', 'link')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'sent_via_email', 'email_sent_at')
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'archived', 'archived_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'send_email_notifications']

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        updated = 0
        for notification in queryset:
            notification.mark_as_read()
            updated += 1
        self.message_user(request, f'{updated} notification(s) marked as read.')

    mark_as_read.short_description = 'Mark selected as read'

    def send_email_notifications(self, request, queryset):
        """Send email for selected notifications."""
        sent = 0
        for notification in queryset:
            if notification.send_email():
                sent += 1
        self.message_user(request, f'{sent} email(s) sent successfully.')

    send_email_notifications.short_description = 'Send email notifications'
