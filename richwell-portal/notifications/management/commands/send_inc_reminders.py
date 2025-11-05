"""
Management command to send INC deadline reminder notifications.

This command should be run daily via cron job to send reminders at 30, 14, and 7 days
before INC deadlines.

Usage:
    python manage.py send_inc_reminders
    python manage.py send_inc_reminders --days 30,14,7
    python manage.py send_inc_reminders --dry-run

Author: Richwell College IT Team
Version: 1.0
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Send INC deadline reminder notifications'

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--days',
            type=str,
            default='30,14,7',
            help='Comma-separated list of days before deadline to send reminders (default: 30,14,7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview reminders without sending emails',
        )

    def handle(self, *args, **options):
        """
        Execute the command.

        Sends INC deadline reminders for specified days before deadline.
        """
        dry_run = options['dry_run']
        days_list = [int(d.strip()) for d in options['days'].split(',')]

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No emails will be sent'))

        self.stdout.write(
            self.style.NOTICE(f'Starting INC reminder process at {timezone.now()}')
        )
        self.stdout.write(f'Sending reminders for: {", ".join(str(d) for d in days_list)} days before deadline')
        self.stdout.write('')

        total_sent = 0

        for days in days_list:
            self.stdout.write(f'Processing {days}-day reminders...')

            if not dry_run:
                count = NotificationService.send_inc_reminders(days_before=days)
                total_sent += count
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Sent {count} reminder(s)')
                )
            else:
                # In dry-run, just show what would be processed
                from grades.models import INCRecord
                from datetime import timedelta

                target_date = timezone.now().date() + timedelta(days=days)
                inc_records = INCRecord.objects.filter(
                    deadline=target_date,
                    resolved_at__isnull=True,
                    archived=False
                )
                count = inc_records.count()
                total_sent += count

                self.stdout.write(
                    self.style.WARNING(f'  → Would send {count} reminder(s)')
                )

                if count > 0 and days == days_list[0]:  # Show details for first batch only
                    for inc in inc_records[:5]:  # Show max 5
                        student = inc.enrollment.student
                        subject = inc.enrollment.subject
                        self.stdout.write(
                            f'    • {student.student_id} - {subject.code} '
                            f'(deadline: {inc.deadline})'
                        )
                    if count > 5:
                        self.stdout.write(f'    ... and {count - 5} more')

            self.stdout.write('')

        # Summary
        self.stdout.write('─' * 60)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would send {total_sent} total reminder(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {total_sent} total reminder(s)')
            )

        self.stdout.write(
            self.style.NOTICE(f'Process completed at {timezone.now()}')
        )
