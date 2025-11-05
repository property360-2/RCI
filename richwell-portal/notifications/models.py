"""
Notification Models

This module defines the Notification model for managing in-app and email notifications.

**Notification Types:**
- INC_REMINDER: INC deadline reminder notifications
- GRADE_POSTED: Grade posting notifications
- ENROLLMENT_CONFIRMED: Enrollment confirmation notifications
- SECTION_ASSIGNED: Professor section assignment notifications
- GENERAL: General system notifications

Author: Richwell College IT Team
Version: 1.0
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import ArchiveMixin, TimeStampMixin


class Notification(ArchiveMixin, TimeStampMixin):
    """
    Stores in-app and email notifications for users.

    Notifications are sent to users for various events like INC deadlines,
    grade postings, enrollment confirmations, etc.

    **Business Rules:**
    - Notifications can be read/unread
    - Notifications can be sent via email
    - INC reminders sent at 30, 14, 7 days before deadline
    - Grade notifications sent when professor posts grades
    - Email sending tracked separately from in-app notification

    **Fields:**
        recipient (FK): User receiving the notification
        notification_type (str): Type of notification
        title (str): Notification title
        message (text): Notification message body
        link (str, optional): URL to related resource
        is_read (bool): Whether notification has been read
        read_at (DateTime, optional): When notification was read
        sent_via_email (bool): Whether email was sent
        email_sent_at (DateTime, optional): When email was sent
        related_object_type (str, optional): Type of related object
        related_object_id (int, optional): ID of related object

    **Methods:**
        mark_as_read(): Mark notification as read
        send_email(): Send notification via email

    **Example Usage:**
        ```python
        # Create INC reminder notification
        notification = Notification.objects.create(
            recipient=student.user,
            notification_type=Notification.Type.INC_REMINDER,
            title="INC Deadline Reminder",
            message=f"Your INC in {subject} is due in 7 days",
            link="/my-grades/"
        )

        # Send email
        notification.send_email()
        ```

    **Access Control:**
    - Users can only see their own notifications
    - Admin/Registrar can see all notifications
    """

    class Type(models.TextChoices):
        INC_REMINDER = "INC_REMINDER", "INC Deadline Reminder"
        GRADE_POSTED = "GRADE_POSTED", "Grade Posted"
        ENROLLMENT_CONFIRMED = "ENROLLMENT_CONFIRMED", "Enrollment Confirmed"
        SECTION_ASSIGNED = "SECTION_ASSIGNED", "Section Assigned"
        GENERAL = "GENERAL", "General Notification"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="User receiving this notification"
    )

    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices,
        default=Type.GENERAL,
        help_text="Type of notification"
    )

    title = models.CharField(
        max_length=200,
        help_text="Notification title"
    )

    message = models.TextField(
        help_text="Notification message body"
    )

    link = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL to related resource (optional)"
    )

    is_read = models.BooleanField(
        default=False,
        help_text="Whether notification has been read"
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When notification was read"
    )

    sent_via_email = models.BooleanField(
        default=False,
        help_text="Whether this notification was sent via email"
    )

    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When email was sent"
    )

    # Generic relation to any object
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of related object (e.g., 'inc_record', 'grade_record')"
    )

    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of related object"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'archived']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['sent_via_email', 'email_sent_at']),
        ]

    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"{self.recipient.get_full_name()} - {self.title} ({status})"

    def mark_as_read(self):
        """
        Mark notification as read.

        Returns:
            bool: True if marked successfully

        Example:
            ```python
            notification.mark_as_read()
            ```
        """
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
        return True

    def send_email(self):
        """
        Send notification via email.

        Returns:
            bool: True if email sent successfully

        Example:
            ```python
            notification.send_email()
            ```
        """
        from notifications.services import EmailService

        if self.sent_via_email:
            return False  # Already sent

        # Send email
        email_service = EmailService()
        success = email_service.send_notification_email(self)

        if success:
            self.sent_via_email = True
            self.email_sent_at = timezone.now()
            self.save(update_fields=['sent_via_email', 'email_sent_at'])

        return success

    @classmethod
    def create_inc_reminder(cls, inc_record, days_remaining):
        """
        Create INC deadline reminder notification.

        Args:
            inc_record: INCRecord object
            days_remaining: Number of days until deadline

        Returns:
            Notification: Created notification

        Example:
            ```python
            notification = Notification.create_inc_reminder(inc_record, 7)
            notification.send_email()
            ```
        """
        student = inc_record.enrollment.student
        subject = inc_record.enrollment.subject

        title = f"INC Deadline Reminder - {subject.code}"
        message = (
            f"Your incomplete grade in {subject.code} ({subject.name}) "
            f"is due in {days_remaining} days.\n\n"
            f"Deadline: {inc_record.deadline}\n\n"
            f"Please complete your requirements as soon as possible."
        )

        return cls.objects.create(
            recipient=student.user,
            notification_type=cls.Type.INC_REMINDER,
            title=title,
            message=message,
            link="/my-grades/",
            related_object_type="inc_record",
            related_object_id=inc_record.id
        )

    @classmethod
    def create_grade_posted(cls, grade_record):
        """
        Create grade posted notification.

        Args:
            grade_record: GradeRecord object

        Returns:
            Notification: Created notification

        Example:
            ```python
            notification = Notification.create_grade_posted(grade_record)
            notification.send_email()
            ```
        """
        student = grade_record.enrollment.student
        subject = grade_record.enrollment.subject

        title = f"Grade Posted - {subject.code}"
        message = (
            f"Your grade for {subject.code} ({subject.name}) has been posted.\n\n"
            f"Grade: {grade_record.grade}\n"
            f"Professor: {grade_record.encoded_by.get_full_name() if grade_record.encoded_by else 'N/A'}\n\n"
            f"View your grades to see details."
        )

        if grade_record.remarks:
            message += f"\n\nRemarks: {grade_record.remarks}"

        return cls.objects.create(
            recipient=student.user,
            notification_type=cls.Type.GRADE_POSTED,
            title=title,
            message=message,
            link="/my-grades/",
            related_object_type="grade_record",
            related_object_id=grade_record.id
        )

    @classmethod
    def create_enrollment_confirmed(cls, enrollment):
        """
        Create enrollment confirmation notification.

        Args:
            enrollment: Enrollment object

        Returns:
            Notification: Created notification

        Example:
            ```python
            notification = Notification.create_enrollment_confirmed(enrollment)
            notification.send_email()
            ```
        """
        student = enrollment.student
        subject = enrollment.subject

        title = f"Enrollment Confirmed - {subject.code}"
        message = (
            f"Your enrollment in {subject.code} ({subject.name}) "
            f"has been confirmed.\n\n"
            f"Section: {enrollment.section.code if enrollment.section else 'TBA'}\n"
            f"Term: {enrollment.term.name}\n"
            f"Units: {enrollment.units}\n\n"
            f"Good luck with your studies!"
        )

        return cls.objects.create(
            recipient=student.user,
            notification_type=cls.Type.ENROLLMENT_CONFIRMED,
            title=title,
            message=message,
            link="/my-enrollments/",
            related_object_type="enrollment",
            related_object_id=enrollment.id
        )

    @classmethod
    def get_unread_for_user(cls, user):
        """
        Get all unread notifications for a user.

        Args:
            user: User object

        Returns:
            QuerySet: Unread notifications

        Example:
            ```python
            unread = Notification.get_unread_for_user(request.user)
            ```
        """
        return cls.objects.filter(
            recipient=user,
            is_read=False,
            archived=False
        )

    @classmethod
    def get_unread_count(cls, user):
        """
        Get count of unread notifications for a user.

        Args:
            user: User object

        Returns:
            int: Count of unread notifications

        Example:
            ```python
            count = Notification.get_unread_count(request.user)
            ```
        """
        return cls.get_unread_for_user(user).count()
