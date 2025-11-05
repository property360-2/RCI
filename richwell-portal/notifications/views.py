"""Views for notifications app."""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def notifications_list(request):
    """
    Display list of notifications for the logged-in user.

    Template: notifications/list.html
    """
    notifications = Notification.objects.filter(
        recipient=request.user,
        archived=False
    )

    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }

    return render(request, 'notifications/list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """
    Mark a notification as read (AJAX endpoint).

    Returns JSON response.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user,
            archived=False
        )
        notification.mark_as_read()

        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })

    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)


@login_required
def mark_all_as_read(request):
    """
    Mark all notifications as read for the logged-in user (AJAX endpoint).

    Returns JSON response.
    """
    notifications = Notification.get_unread_for_user(request.user)
    count = 0

    for notification in notifications:
        notification.mark_as_read()
        count += 1

    return JsonResponse({
        'success': True,
        'message': f'{count} notification(s) marked as read',
        'count': count
    })


@login_required
def unread_count(request):
    """
    Get count of unread notifications (AJAX endpoint).

    Returns JSON response with unread count.
    """
    count = Notification.get_unread_count(request.user)

    return JsonResponse({
        'count': count
    })
