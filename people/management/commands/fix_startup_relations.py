# people/management/commands/fix_startup_relations.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from people.models import Employee
from startups.models import StartupProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix startup relations for employees and users'

    def handle(self, *args, **options):
        self.stdout.write('Fixing startup relations...')
        
        # Fix employees without startup
        employees_without_startup = Employee.objects.filter(startup__isnull=True)
        count = employees_without_startup.count()
        self.stdout.write(f'Found {count} employees without startup')
        
        for emp in employees_without_startup:
            if emp.user.startup:
                emp.startup = emp.user.startup
                emp.save()
                self.stdout.write(f'  - Fixed {emp.user.username}')
        
        # Fix users without startup
        users_without_startup = User.objects.filter(startup__isnull=True, role__in=['startup_admin', 'startup_hr', 'startup_manager', 'employee'])
        count = users_without_startup.count()
        self.stdout.write(f'Found {count} users without startup')
        
        for user in users_without_startup:
            try:
                emp = Employee.objects.get(user=user)
                if emp.startup:
                    user.startup = emp.startup
                    user.save()
                    self.stdout.write(f'  - Fixed {user.username}')
            except Employee.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS('Done!'))