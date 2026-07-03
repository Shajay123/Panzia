# people/management/commands/fix_orphaned_attendance.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from people.models import Attendance, Employee

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix attendance records without employee association'

    def handle(self, *args, **options):
        # Find attendance records without employee
        orphaned = Attendance.objects.filter(employee__isnull=True)
        count = orphaned.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No orphaned attendance records found.'))
            return
        
        self.stdout.write(f'Found {count} attendance records without employee.')
        
        # Get first active employee to assign
        first_employee = Employee.objects.filter(is_active=True).first()
        
        if not first_employee:
            self.stdout.write(self.style.ERROR('❌ No active employees found. Cannot fix.'))
            return
        
        for attendance in orphaned:
            attendance.employee = first_employee
            attendance.save()
            self.stdout.write(f'Fixed attendance {attendance.id} -> {first_employee}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Fixed {count} orphaned attendance records.'))