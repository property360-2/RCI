"""
Notification Signals

This module defines signal handlers that automatically create notifications
when certain events occur in the system.

Author: Richwell College IT Team
Version: 1.0
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import NotificationService


@receiver(post_save, sender='grades.GradeRecord')
def notify_grade_posted(sender, instance, created, **kwargs):
    """
    Send notification when a grade is posted.

    Args:
        sender: Model class (GradeRecord)
        instance: GradeRecord instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created and not instance.is_inc() and not instance.is_dropped():
        # Only notify for actual grades (not INC or DRP)
        try:
            NotificationService.send_grade_notification(instance)
        except Exception as e:
            # Log error but don't break the grade posting
            print(f"Error sending grade notification: {str(e)}")


@receiver(post_save, sender='enrollments.Enrollment')
def notify_enrollment_confirmed(sender, instance, created, **kwargs):
    """
    Send notification when enrollment is confirmed.

    Args:
        sender: Model class (Enrollment)
        instance: Enrollment instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    # Check if enrollment status changed to CONFIRMED
    if not created:
        # Check if status just changed to CONFIRMED
        from enrollments.models import Enrollment
        if instance.status == Enrollment.Status.CONFIRMED:
            try:
                # Check if notification already sent
                from .models import Notification
                existing = Notification.objects.filter(
                    recipient=instance.student.user,
                    notification_type=Notification.Type.ENROLLMENT_CONFIRMED,
                    related_object_type='enrollment',
                    related_object_id=instance.id
                ).exists()

                if not existing:
                    NotificationService.send_enrollment_notification(instance)
            except Exception as e:
                # Log error but don't break the enrollment process
                print(f"Error sending enrollment notification: {str(e)}")
