"""
Notification Services

This module provides services for sending notifications via email and
creating automated notifications for various events.

Author: Richwell College IT Team
Version: 1.0
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import Notification


class EmailService:
    """
    Service for sending email notifications.

    Handles email composition and sending for all notification types.
    """

    def __init__(self):
        """Initialize email service with settings."""
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@richwell.edu')
        self.use_html = getattr(settings, 'EMAIL_USE_HTML', True)

    def send_notification_email(self, notification):
        """
        Send email for a notification.

        Args:
            notification: Notification object

        Returns:
            bool: True if email sent successfully

        Example:
            ```python
            service = EmailService()
            service.send_notification_email(notification)
            ```
        """
        try:
            recipient_email = notification.recipient.email
            if not recipient_email:
                return False

            subject = notification.title
            message = notification.message

            # Create plain text version
            text_content = message

            # Create HTML version if enabled
            if self.use_html:
                html_content = self._create_html_email(notification)

                # Send multipart email
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=self.from_email,
                    to=[recipient_email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
            else:
                # Send plain text email
                send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=self.from_email,
                    recipient_list=[recipient_email],
                    fail_silently=False
                )

            return True

        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"Error sending email: {str(e)}")
            return False

    def _create_html_email(self, notification):
        """
        Create HTML email content.

        Args:
            notification: Notification object

        Returns:
            str: HTML email content
        """
        # Simple HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4A5568;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    background-color: #f7fafc;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #718096;
                    font-size: 12px;
                    margin-top: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4299e1;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Richwell College Portal</h2>
                </div>
                <div class="content">
                    <h3>{notification.title}</h3>
                    <p>{notification.message.replace(chr(10), '<br>')}</p>
                    {f'<a href="{settings.SITE_URL}{notification.link}" class="button">View Details</a>' if notification.link else ''}
                </div>
                <div class="footer">
                    <p>This is an automated message from Richwell College Portal.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def send_bulk_emails(self, notifications):
        """
        Send emails for multiple notifications.

        Args:
            notifications: List or QuerySet of Notification objects

        Returns:
            dict: Results with success and failure counts

        Example:
            ```python
            service = EmailService()
            results = service.send_bulk_emails(notifications)
            # {'sent': 10, 'failed': 2}
            ```
        """
        results = {'sent': 0, 'failed': 0}

        for notification in notifications:
            if notification.send_email():
                results['sent'] += 1
            else:
                results['failed'] += 1

        return results


class NotificationService:
    """
    Service for creating and managing notifications.

    Provides high-level methods for creating notifications for various events.
    """

    @staticmethod
    def send_inc_reminders(days_before=7):
        """
        Send INC deadline reminders for records nearing deadline.

        Args:
            days_before (int): Days before deadline to send reminder

        Returns:
            int: Number of reminders sent

        Example:
            ```python
            # Send reminders for INCs due in 7 days
            count = NotificationService.send_inc_reminders(days_before=7)
            ```
        """
        from grades.models import INCRecord
        from datetime import timedelta

        target_date = timezone.now().date() + timedelta(days=days_before)

        # Get INC records with deadline on target date
        inc_records = INCRecord.objects.filter(
            deadline=target_date,
            resolved_at__isnull=True,
            archived=False
        )

        count = 0
        for inc_record in inc_records:
            # Check if reminder already sent
            existing = Notification.objects.filter(
                recipient=inc_record.enrollment.student.user,
                notification_type=Notification.Type.INC_REMINDER,
                related_object_type='inc_record',
                related_object_id=inc_record.id,
                created_at__gte=timezone.now() - timedelta(days=1)  # Don't spam
            ).exists()

            if not existing:
                notification = Notification.create_inc_reminder(
                    inc_record,
                    days_before
                )
                notification.send_email()
                count += 1

        return count

    @staticmethod
    def send_grade_notification(grade_record):
        """
        Send notification when grade is posted.

        Args:
            grade_record: GradeRecord object

        Returns:
            Notification: Created notification or None

        Example:
            ```python
            notification = NotificationService.send_grade_notification(grade_record)
            ```
        """
        notification = Notification.create_grade_posted(grade_record)
        notification.send_email()
        return notification

    @staticmethod
    def send_enrollment_notification(enrollment):
        """
        Send notification when enrollment is confirmed.

        Args:
            enrollment: Enrollment object

        Returns:
            Notification: Created notification or None

        Example:
            ```python
            notification = NotificationService.send_enrollment_notification(enrollment)
            ```
        """
        notification = Notification.create_enrollment_confirmed(enrollment)
        notification.send_email()
        return notification

    @staticmethod
    def cleanup_old_notifications(days=90):
        """
        Archive old read notifications.

        Args:
            days (int): Archive notifications older than this many days

        Returns:
            int: Number of notifications archived

        Example:
            ```python
            archived = NotificationService.cleanup_old_notifications(days=90)
            ```
        """
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)

        notifications = Notification.objects.filter(
            is_read=True,
            read_at__lt=cutoff_date,
            archived=False
        )

        count = notifications.count()
        notifications.update(archived=True, archived_at=timezone.now())

        return count
