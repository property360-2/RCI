# Critical System Features Documentation

This document describes the critical system features implemented in the Richwell College Portal.

## Table of Contents
1. [INC Auto-Expiration System](#inc-auto-expiration-system)
2. [Notifications System](#notifications-system)
3. [Email Notifications](#email-notifications)
4. [API Rate Limiting](#api-rate-limiting)
5. [Transcript Generation](#transcript-generation)
6. [Setup and Configuration](#setup-and-configuration)

---

## INC Auto-Expiration System

### Overview
The INC (Incomplete) grade auto-expiration system automatically converts overdue incomplete grades to failed grades (5.0) when deadlines expire.

### Features
- **Automatic Conversion**: Overdue INC grades are automatically converted to 5.0 (Failed)
- **Deadline Tracking**:
  - Minor subjects: 6-month deadline
  - Major subjects: 12-month deadline
- **Audit Trail**: All conversions are logged with timestamps and remarks
- **Manual Override**: Professors/Registrars can resolve INC before expiration

### Management Command

Run the auto-expiration command:

```bash
# Run normally
python manage.py expire_inc_grades

# Preview changes without applying them
python manage.py expire_inc_grades --dry-run

# Show detailed output
python manage.py expire_inc_grades --verbose
```

### Cron Job Setup

Add to crontab to run daily at 2 AM:

```cron
0 2 * * * cd /path/to/richwell-portal && python manage.py expire_inc_grades >> /var/log/inc_expiration.log 2>&1
```

### Database Models

**INCRecord Model** (`grades/models.py`):
- `enrollment`: Link to enrollment with INC grade
- `deadline`: Date when INC expires
- `resolved_at`: When INC was resolved
- `resolution_note`: Resolution details
- `confirmed_by`: Registrar who confirmed

**Methods**:
- `is_overdue()`: Check if deadline passed
- `days_remaining()`: Calculate days until deadline
- `resolve()`: Mark INC as resolved
- `convert_to_failed()`: Convert to 5.0 grade
- `get_overdue()`: Get all overdue INC records (class method)

---

## Notifications System

### Overview
Comprehensive in-app and email notification system for important events.

### Notification Types

| Type | Description | Recipients | Auto-Send |
|------|-------------|------------|-----------|
| `INC_REMINDER` | INC deadline reminders | Students | Yes (30, 14, 7 days before) |
| `GRADE_POSTED` | Grade posting notifications | Students | Yes (on grade save) |
| `ENROLLMENT_CONFIRMED` | Enrollment confirmation | Students | Yes (on status change) |
| `SECTION_ASSIGNED` | Section assignment | Professors | Manual |
| `GENERAL` | General notifications | Any user | Manual |

### Database Models

**Notification Model** (`notifications/models.py`):
- `recipient`: User receiving notification
- `notification_type`: Type of notification
- `title`: Notification title
- `message`: Notification message
- `link`: URL to related resource
- `is_read`: Read status
- `read_at`: When notification was read
- `sent_via_email`: Email sent status
- `email_sent_at`: When email was sent
- `related_object_type`: Type of related object
- `related_object_id`: ID of related object

**Methods**:
- `mark_as_read()`: Mark as read
- `send_email()`: Send via email
- `create_inc_reminder()`: Create INC reminder (class method)
- `create_grade_posted()`: Create grade notification (class method)
- `create_enrollment_confirmed()`: Create enrollment notification (class method)
- `get_unread_for_user()`: Get unread notifications (class method)
- `get_unread_count()`: Get unread count (class method)

### Management Commands

**Send INC Reminders**:

```bash
# Send reminders for default days (30, 14, 7)
python manage.py send_inc_reminders

# Custom reminder days
python manage.py send_inc_reminders --days 30,14,7,3,1

# Preview without sending
python manage.py send_inc_reminders --dry-run
```

### Cron Job Setup

Add to crontab to run daily at 8 AM:

```cron
0 8 * * * cd /path/to/richwell-portal && python manage.py send_inc_reminders >> /var/log/inc_reminders.log 2>&1
```

### Web Endpoints

| URL | Method | Description |
|-----|--------|-------------|
| `/notifications/` | GET | List all notifications |
| `/notifications/<id>/mark-read/` | POST | Mark notification as read |
| `/notifications/mark-all-read/` | POST | Mark all as read |
| `/notifications/unread-count/` | GET | Get unread count (JSON) |

### Programmatic Usage

```python
from notifications.models import Notification
from notifications.services import NotificationService

# Create and send INC reminder
notification = Notification.create_inc_reminder(inc_record, days_remaining=7)
notification.send_email()

# Send grade posted notification
NotificationService.send_grade_notification(grade_record)

# Send enrollment confirmation
NotificationService.send_enrollment_notification(enrollment)

# Get unread notifications
unread = Notification.get_unread_for_user(user)
count = Notification.get_unread_count(user)
```

### Automatic Notifications (Signals)

The system automatically sends notifications for:
- **Grade Posted**: When professor saves a grade (not INC/DRP)
- **Enrollment Confirmed**: When enrollment status changes to CONFIRMED

Signals are defined in `notifications/signals.py`.

---

## Email Notifications

### Configuration

Email settings are configured via environment variables in `.env`:

```bash
# Development (console output)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Production (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@richwell.edu
```

### Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in `EMAIL_HOST_PASSWORD`

### SMTP Services

Supported email services:
- **Gmail**: smtp.gmail.com:587
- **Office 365**: smtp.office365.com:587
- **SendGrid**: smtp.sendgrid.net:587
- **Mailgun**: smtp.mailgun.org:587

### Email Templates

HTML email templates are generated in `notifications/services.py`:
- Professional design with Richwell branding
- Responsive layout
- Call-to-action buttons
- Plain text fallback

### Testing Emails

```bash
# Test email configuration
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test message.',
    'noreply@richwell.edu',
    ['test@example.com'],
)
```

---

## API Rate Limiting

### Overview
Prevents API abuse by limiting the number of requests per time period.

### Rate Limits

| User Type | Limit | Period |
|-----------|-------|--------|
| Anonymous | 100 requests | per hour |
| Authenticated | 1000 requests | per hour |
| Login attempts | 5 attempts | per 15 minutes (per IP) |

### Configuration

Configured in `config/settings.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}
```

### Custom Rate Limits

Apply custom rate limits to specific views:

```python
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import UserRateThrottle

class OncePerDayUserThrottle(UserRateThrottle):
    rate = '1/day'

@throttle_classes([OncePerDayUserThrottle])
class SensitiveView(APIView):
    pass
```

### Login Rate Limiting

Login attempts are rate-limited per IP address:
- **Location**: `users/views.py:86-98`
- **Limit**: 5 failed attempts per IP
- **Window**: 15 minutes
- **Response**: HTTP 429-like blocking message

### Cache Backend

Rate limiting uses Django's cache framework (configured in `settings.py`):

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

For production, consider Redis:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## Transcript Generation

### Overview
Generates academic transcripts with grades, GPA, and completion status.

### Features
- **Comprehensive Transcripts**: All grades organized by term
- **GPA Calculation**: Term GPA and cumulative GPA
- **INC Tracking**: Shows incomplete grades with deadlines
- **Unit Tracking**: Total units attempted and earned
- **API Support**: JSON endpoints for programmatic access

### Student Methods

**`Student.get_transcript()` method** (`students/models.py:463-505`):

```python
transcript = student.get_transcript()
# Returns:
{
    'student_id': 'S2024001',
    'name': 'John Doe',
    'course_code': 'BSCS',
    'year_level': 3,
    'status': 'ACTIVE',
    'cumulative_gpa': 2.15,
    'grades_by_term': {
        'Fall 2024': [
            {
                'subject_code': 'COMP101',
                'subject_name': 'Introduction to Computing',
                'units': 3,
                'grade': '2.0'
            },
            ...
        ]
    }
}
```

### Web Endpoints

| URL | Description | Access |
|-----|-------------|--------|
| `/my-grades/` | Student grades view | Students only |
| `/api/v1/students/<id>/transcript/` | JSON transcript | Authenticated |

### Features in My Grades View

**Location**: `users/views.py:398-490`

- Grades organized by term
- Term GPA calculation
- Cumulative GPA
- Total units tracking
- Grade point calculation
- INC status visibility
- Professor remarks

### Grade Calculation Rules

- **Passing grades** (1.0-3.0): Included in GPA
- **Failed grades** (5.0): Included in GPA
- **INC grades**: Excluded from GPA until resolved
- **DRP grades**: Excluded from GPA
- **Grade points**: {1.0: 1.0, 1.5: 1.5, 2.0: 2.0, 2.5: 2.5, 3.0: 3.0, 5.0: 5.0}
- **Weighted by units**: (grade × units) / total_units

---

## Setup and Configuration

### Installation Steps

1. **Add notifications app** (already done in settings.py):
```python
INSTALLED_APPS = [
    ...
    "notifications",
]
```

2. **Run migrations**:
```bash
python manage.py makemigrations notifications
python manage.py migrate
```

3. **Configure email** in `.env`:
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@richwell.edu
SITE_URL=http://localhost:8000
```

4. **Set up cron jobs** (optional):
```cron
# Expire overdue INC grades daily at 2 AM
0 2 * * * cd /path/to/richwell-portal && python manage.py expire_inc_grades

# Send INC reminders daily at 8 AM
0 8 * * * cd /path/to/richwell-portal && python manage.py send_inc_reminders
```

5. **Test the features**:
```bash
# Test INC expiration
python manage.py expire_inc_grades --dry-run

# Test INC reminders
python manage.py send_inc_reminders --dry-run

# Access notifications
curl http://localhost:8000/notifications/unread-count/
```

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Configure real SMTP email backend
- [ ] Set up Redis for caching (recommended)
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up SSL/TLS for secure email
- [ ] Configure cron jobs for automation
- [ ] Set up logging for management commands
- [ ] Test email delivery
- [ ] Monitor rate limiting logs
- [ ] Set up backup for notification data

---

## File Structure

```
richwell-portal/
├── grades/
│   ├── models.py                  # GradeRecord, INCRecord models
│   └── management/
│       └── commands/
│           └── expire_inc_grades.py   # INC expiration command
├── notifications/
│   ├── models.py                  # Notification model
│   ├── admin.py                   # Admin interface
│   ├── services.py                # EmailService, NotificationService
│   ├── signals.py                 # Automatic notification triggers
│   ├── views.py                   # Web endpoints
│   ├── urls.py                    # URL routing
│   └── management/
│       └── commands/
│           └── send_inc_reminders.py  # INC reminder command
├── config/
│   ├── settings.py               # Email & rate limiting config
│   └── urls.py                   # Main URL routing
└── .env.example                  # Environment variables template
```

---

## Support and Maintenance

### Logs

Monitor these log files:
- `/var/log/inc_expiration.log` - INC expiration logs
- `/var/log/inc_reminders.log` - INC reminder logs
- Django error logs for email failures

### Troubleshooting

**Emails not sending**:
1. Check `EMAIL_BACKEND` is set correctly
2. Verify SMTP credentials
3. Check firewall allows outbound SMTP
4. Test with `python manage.py shell`

**Rate limiting not working**:
1. Verify cache backend is configured
2. Check `CACHES` setting in settings.py
3. Test with multiple rapid requests

**INC not expiring**:
1. Check cron job is running
2. Verify `INCRecord.deadline` dates
3. Run with `--dry-run --verbose` to debug

---

## Author
Richwell College IT Team

## Version
1.0 - November 2024

## License
Proprietary - Richwell College Internal Use Only
