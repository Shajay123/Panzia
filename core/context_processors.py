# core/context_processors.py

from people.models import Employee


def user_roles(request):
    """
    Add user role information to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        # ============================================
        # DJANGO SUPER ADMIN - SEPARATE & PRIVILEGED
        # ============================================
        context['is_django_super_admin'] = request.user.is_superuser
        context['is_super_admin'] = request.user.is_super_admin()  # Custom super admin role
        context['is_platform_admin'] = request.user.is_superuser or request.user.is_super_admin()
        
        # Startup specific roles
        context['is_startup_admin'] = request.user.is_startup_admin()
        context['is_startup_hr'] = request.user.is_startup_hr()
        context['is_startup_manager'] = request.user.is_startup_manager()
        context['is_employee'] = request.user.is_employee()
        context['is_talent'] = request.user.is_talent()
        context['is_staff_user'] = request.user.is_staff or request.user.is_superuser
        
        # ============================================
        # STARTUP ADMIN AND HR HAVE EQUAL ACCESS
        # ============================================
        
        # Check if user has startup access (admin, HR, manager)
        context['is_startup_user'] = (
            request.user.is_startup_admin() or 
            request.user.is_startup_hr() or 
            request.user.is_startup_manager()
        )
        
        # Check if user has HR access (admin, HR, manager all have equal access)
        # Django super admin also has full access
        context['has_hr_access'] = (
            request.user.is_superuser or  # Django super admin has full access
            request.user.is_super_admin() or 
            request.user.is_startup_admin() or 
            request.user.is_startup_hr() or 
            request.user.is_startup_manager() or
            request.user.is_staff
        )
        
        # Check if user has people management access (admin, HR, manager all have equal access)
        context['has_people_access'] = (
            request.user.is_superuser or  # Django super admin has full access
            request.user.is_super_admin() or 
            request.user.is_startup_admin() or 
            request.user.is_startup_hr() or 
            request.user.is_startup_manager() or
            request.user.is_staff
        )
        
        # Check if user is a startup admin or HR (for specific features)
        context['is_startup_admin_or_hr'] = (
            request.user.is_startup_admin() or 
            request.user.is_startup_hr()
        )
        
        # ============================================
        # STARTUP INFO
        # ============================================
        
        # Get startup info (only for startup users)
        if request.user.startup:
            context['user_startup'] = request.user.startup
            context['user_startup_id'] = request.user.startup.id
            context['user_startup_name'] = request.user.startup.company_name
            context['startup_logo'] = request.user.startup.logo
        else:
            context['user_startup'] = None
            context['user_startup_id'] = None
            context['user_startup_name'] = None
            context['startup_logo'] = None
        
        # ============================================
        # EMPLOYEE PROFILE
        # ============================================
        
        # Check if user has employee profile
        try:
            employee = Employee.objects.get(user=request.user)
            context['has_employee_profile'] = True
            context['employee_profile'] = employee
            context['employee_id'] = employee.id
            context['employee_name'] = employee.user.get_full_name()
            context['employee_designation'] = employee.designation
        except Employee.DoesNotExist:
            context['has_employee_profile'] = False
            context['employee_profile'] = None
            context['employee_id'] = None
            context['employee_name'] = None
            context['employee_designation'] = None
    
    return context


# Alias for backward compatibility
startup_context = user_roles