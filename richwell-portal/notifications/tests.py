"""Tests for notifications app."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class NotificationModelTests(TestCase):
    """Test cases for Notification model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.Type.GENERAL,
            title='Test Notification',
            message='This is a test notification'
        )

        self.assertEqual(notification.recipient, self.user)
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.sent_via_email)

    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.Type.GENERAL,
            title='Test',
            message='Test'
        )

        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)

        notification.mark_as_read()

        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_get_unread_count(self):
        """Test getting unread notification count."""
        # Create 3 notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user,
                notification_type=Notification.Type.GENERAL,
                title=f'Test {i}',
                message='Test'
            )

        # All should be unread
        self.assertEqual(Notification.get_unread_count(self.user), 3)

        # Mark one as read
        notification = Notification.objects.first()
        notification.mark_as_read()

        # Should now be 2 unread
        self.assertEqual(Notification.get_unread_count(self.user), 2)
