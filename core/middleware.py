# core/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from people.models import Employee


class RoleBasedRedirectMiddleware:
    """
    Middleware to redirect users based on their role
    Django Super Admin has full access to everything
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
        
        # ============================================
        # DJANGO SUPER ADMIN - FULL ACCESS
        # ============================================
        if request.user.is_superuser:
            return None  # Allow full access to everything
        
        # Skip if user is staff (but not super admin)
        if request.user.is_staff:
            return None
        
        # ============================================
        # STARTUP ADMIN, HR, MANAGER - FULL ACCESS TO EVERYTHING
        # ============================================
        if request.user.role in ['startup_admin', 'startup_hr', 'startup_manager']:
            # Allow full access to all pages (don't redirect)
            return None
        
        # ============================================
        # EMPLOYEE - RESTRICTED TO EMPLOYEE PORTAL
        # ============================================
        if request.user.role == 'employee':
            # Allow access to employee portal and related pages
            employee_allowed_paths = [
                '/dashboard/employee/',
                '/people/employee/',
                '/attendance/',
                '/leave/',
                '/payroll/',
                '/employee/',
                '/people/attendance/',
                '/people/leave/',
                '/people/payroll/',
            ]
            for path in employee_allowed_paths:
                if request.path.startswith(path):
                    try:
                        Employee.objects.get(user=request.user)
                        return None
                    except Employee.DoesNotExist:
                        return redirect('home')
            
            # If employee tries to access startup dashboard or other restricted areas
            if request.path.startswith('/dashboard/startup/'):
                return redirect('employee_portal_dashboard')
            
            # If employee tries to access people/HR pages that are restricted
            if request.path.startswith('/people/') and not any(request.path.startswith(p) for p in employee_allowed_paths):
                return redirect('employee_portal_dashboard')
            
            return None
        
        # ============================================
        # TALENT - RESTRICTED TO TALENT DASHBOARD AND RELATED PAGES
        # ============================================
        if request.user.role == 'talent':
            # Allow talent to access these paths
            talent_allowed_paths = [
                '/dashboard/talent/',
                '/sprints/talent-dashboard/',
                '/talents/',
                '/browse-jobs/',
                '/my-applications/',
                '/placements/browse-jobs/',
                '/placements/my-applications/',
                '/placements/browse-jobs/',
                '/placements/my-applications/',
                # Sprint URLs - TALENT SIDE (view only)
                '/sprints/browse/',
                '/sprints/my-applications/',
                '/sprints/my-tasks/',
                '/sprints/apply/',
                '/sprints/detail/',
                '/sprints/submit-task/',
                '/sprints/task/',  # For task_detail view
                # AI Engine
                '/ai_engine/dashboard/',
                '/ai_engine/',
                # Payments
                '/payments/',
                # Jobs/Placements
                '/placements/',
                # Profile
                '/profiles/',
                '/portfolio/',
            ]
            for path in talent_allowed_paths:
                if request.path.startswith(path):
                    return None
            
            # Block talent from accessing startup sprint pages
            startup_sprint_paths = [
                '/sprints/create/',
                '/sprints/my-sprints/',
                '/sprints/edit/',
                '/sprints/delete/',
                '/sprints/applications/',
                '/sprints/accept/',
                '/sprints/reject/',
                '/sprints/members/',
                '/sprints/tasks/',
                '/sprints/create-task/',
                '/sprints/review-submissions/',
                '/sprints/submission-review/',
                '/sprints/approve-submission/',
            ]
            for path in startup_sprint_paths:
                if request.path.startswith(path):
                    return redirect('talent_dashboard')
            
            # If talent tries to access startup dashboard
            if request.path.startswith('/dashboard/startup/'):
                return redirect('talent_dashboard')
            
            # If talent tries to access people/HR pages
            if request.path.startswith('/people/'):
                return redirect('talent_dashboard')
            
            # For any other restricted page, redirect to talent dashboard
            return redirect('talent_dashboard')
        
        return None


class StartupAccessMiddleware:
    """
    Middleware to ensure startup users have proper access
    Django Super Admin has full access to everything
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
        
        # ============================================
        # DJANGO SUPER ADMIN - FULL ACCESS
        # ============================================
        if request.user.is_superuser:
            return None  # Allow full access to everything
        
        # ============================================
        # STARTUP USERS - ADMIN, HR, MANAGER - FULL ACCESS
        # ============================================
        if request.user.role in ['startup_admin', 'startup_hr', 'startup_manager']:
            # Check if they have a startup (redirect to setup if not)
            if not request.user.startup:
                # Don't redirect if already on profile setup page
                if not request.path.startswith('/startups/profile/setup/'):
                    from django.contrib import messages
                    messages.warning(request, 'Please complete your startup profile setup first.')
                    return redirect('startups:startup_profile_setup')
            # Allow full access to everything
            return None
        
        # ============================================
        # EMPLOYEE - RESTRICTED ACCESS
        # ============================================
        if request.user.role == 'employee':
            # Allow access to employee portal and related pages
            employee_allowed_paths = [
                '/dashboard/employee/',
                '/people/employee/',
                '/attendance/',
                '/leave/',
                '/payroll/',
                '/employee/',
                '/people/attendance/',
                '/people/leave/',
                '/people/payroll/',
            ]
            for path in employee_allowed_paths:
                if request.path.startswith(path):
                    try:
                        Employee.objects.get(user=request.user)
                        return None
                    except Employee.DoesNotExist:
                        return redirect('home')
            return redirect('employee_portal_dashboard')
        
        # ============================================
        # TALENT - RESTRICTED ACCESS (Allow sprint URLs)
        # ============================================
        if request.user.role == 'talent':
            talent_allowed_paths = [
                '/dashboard/talent/',
                '/talents/',
                '/browse-jobs/',
                '/my-applications/',
                '/placements/browse-jobs/',
                '/placements/my-applications/',
                '/sprints/browse/',
                '/sprints/my-applications/',
                '/sprints/my-tasks/',
                '/sprints/apply/',
                '/sprints/detail/',
                '/sprints/submit-task/',
                '/sprints/task/',  # For task_detail view
                '/ai_engine/dashboard/',
                '/payments/',
                '/placements/',
                '/profiles/',
                '/portfolio/',
            ]
            for path in talent_allowed_paths:
                if request.path.startswith(path):
                    return None
            return redirect('talent_dashboard')
        
        return None


class StartupProfileRequiredMiddleware:
    """
    Middleware to ensure startup users have a profile
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
        
        # Skip if user is Django super admin
        if request.user.is_superuser:
            return None
        
        # Skip if user is staff
        if request.user.is_staff:
            return None
        
        # Skip if user is talent or employee (they don't need startup profile)
        if request.user.role in ['talent', 'employee']:
            return None
        
        # Skip if user is already on profile setup page
        if request.path.startswith('/startups/profile/setup/'):
            return None
        
        # Skip if user is on login, register, or apply pages
        if request.path.startswith('/accounts/login/') or request.path.startswith('/accounts/register/') or request.path.startswith('/accounts/apply/'):
            return None
        
        # Skip for homepage
        if request.path == '/':
            return None
        
        # For startup users (admin, HR, manager), check if they have a startup
        if request.user.role in ['startup_admin', 'startup_hr', 'startup_manager']:
            if not request.user.startup:
                # Don't redirect if it's an AJAX request
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return None
                
                from django.contrib import messages
                messages.warning(request, 'Please complete your startup profile setup first.')
                return redirect('startups:startup_profile_setup')
        
        return None