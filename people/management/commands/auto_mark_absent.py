# people/management/commands/auto_mark_absent.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from people.models import Attendance, Employee

class Command(BaseCommand):
    help = 'Auto-mark absent employees at the end of the day'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to mark absent (YYYY-MM-DD). Defaults to today.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        # Get date
        if options.get('date'):
            from datetime import datetime
            date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(f'📅 Processing attendance for {date}')
        
        # Get all active employees
        active_employees = Employee.objects.filter(is_active=True)
        total = active_employees.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No active employees found'))
            return
        
        marked_count = 0
        absent_count = 0
        already_absent = 0
        
        for employee in active_employees:
            existing = Attendance.objects.filter(
                employee=employee,
                date=date
            ).first()
            
            if not existing:
                if not dry_run:
                    Attendance.objects.create(
                        employee=employee,
                        date=date,
                        status='Absent',
                        notes='Auto-marked absent (No check-in recorded)'
                    )
                absent_count += 1
                self.stdout.write(
                    f'{"[DRY RUN] " if dry_run else "✅ "}'
                    f'Marked {employee.user.get_full_name()} as absent'
                )
            elif existing.status == 'Absent':
                already_absent += 1
            else:
                marked_count += 1
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(f'📊 Summary for {date}:')
        self.stdout.write(f'  Total Employees: {total}')
        self.stdout.write(f'  Already Marked: {marked_count}')
        self.stdout.write(f'  Already Absent: {already_absent}')
        self.stdout.write(f'  Newly Absent: {absent_count}')
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️ DRY RUN - No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Auto-absent marking completed'))