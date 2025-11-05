"""
Management command to automatically expire overdue INC grades.

This command finds all overdue INC records and converts them to failed grades (5.0).
It should be run regularly via cron job or task scheduler.

Usage:
    python manage.py expire_inc_grades
    python manage.py expire_inc_grades --dry-run  # Preview without making changes
    python manage.py expire_inc_grades --verbose  # Show detailed output

Author: Richwell College IT Team
Version: 1.0
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from grades.models import INCRecord


class Command(BaseCommand):
    help = 'Automatically expire overdue INC grades and convert them to 5.0 (Failed)'

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview which INC records would be expired without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each INC record processed',
        )

    def handle(self, *args, **options):
        """
        Execute the command.

        Finds all overdue INC records and converts them to failed grades (5.0).
        """
        dry_run = options['dry_run']
        verbose = options['verbose']

        # Display execution mode
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        self.stdout.write(self.style.NOTICE(f'Starting INC expiration process at {timezone.now()}'))

        # Get all overdue INC records
        overdue_incs = INCRecord.get_overdue()
        total_count = overdue_incs.count()

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No overdue INC records found.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {total_count} overdue INC record(s)'))
        self.stdout.write('')

        # Process each overdue INC
        success_count = 0
        error_count = 0

        for inc in overdue_incs:
            student_id = inc.enrollment.student.student_id
            student_name = inc.enrollment.student.user.get_full_name()
            subject_code = inc.enrollment.subject.code
            subject_name = inc.enrollment.subject.name
            deadline = inc.deadline
            days_overdue = abs(inc.days_remaining())

            # Display info about this INC
            if verbose or dry_run:
                self.stdout.write(
                    f'  • {student_id} ({student_name}) - {subject_code} ({subject_name})'
                )
                self.stdout.write(
                    f'    Deadline: {deadline} ({days_overdue} days overdue)'
                )

            if not dry_run:
                try:
                    # Convert to failed grade
                    inc.convert_to_failed()
                    success_count += 1

                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✓ Converted to 5.0 (Failed)')
                        )

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'    ✗ Error: {str(e)}')
                    )
            else:
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(f'    → Would convert to 5.0 (Failed)')
                    )

            if verbose or dry_run:
                self.stdout.write('')

        # Display summary
        self.stdout.write('─' * 60)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: {total_count} INC record(s) would be expired')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully expired {success_count} INC record(s)')
            )
            if error_count > 0:
                self.stdout.write(
                    self.style.ERROR(f'Failed to expire {error_count} INC record(s)')
                )

        self.stdout.write(self.style.NOTICE(f'Process completed at {timezone.now()}'))
