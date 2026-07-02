# core/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from people.models import Employee


class RoleBasedRedirectMiddleware:
    """
    Middleware to redirect users based on their role
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None
        
        # Skip if user is super admin or staff
        if request.user.is_superuser or request.user.is_staff:
            return None
        
        # Check if user is trying to access HR dashboard
        if request.path.startswith('/people/') and not request.path.startswith('/people/employee/'):
            # Check if user is a regular employee
            try:
                employee = Employee.objects.get(user=request.user)
                # If user is a regular employee (not admin/HR/manager)
                if request.user.role not in ['startup_admin', 'startup_hr', 'startup_manager']:
                    # Redirect to employee portal
                    return redirect('employee_portal_dashboard')
            except Employee.DoesNotExist:
                pass
        
        return None