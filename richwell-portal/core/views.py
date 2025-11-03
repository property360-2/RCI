from django.http import JsonResponse
from django.db import connection
from django.conf import settings


def health_check(request):
    """
    Health check endpoint to verify the application is running.
    Returns 200 OK with database connectivity status.
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return JsonResponse({
        "status": "ok",
        "database": db_status,
        "debug": settings.DEBUG
    })
