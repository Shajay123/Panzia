# people/management/commands/assign_default_department.py
from django.core.management.base import BaseCommand
from people.models import Employee, Department

class Command(BaseCommand):
    help = 'Assign default department to employees without department'

    def handle(self, *args, **options):
        # Get or create default department
        dept, created = Department.objects.get_or_create(
            name='General',
            defaults={'code': 'GEN', 'description': 'Default department'}
        )
        
        # Get employees without department
        employees = Employee.objects.filter(department__isnull=True)
        count = employees.count()
        
        for employee in employees:
            employee.department = dept
            employee.save()
        
        self.stdout.write(f'✅ Assigned {count} employees to {dept.name} department')