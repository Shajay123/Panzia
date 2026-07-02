# core/context_processors.py

from people.models import Employee


def startup_context(request):
    """
    Add startup and user role information to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        # Basic role checks
        context['is_super_admin'] = request.user.is_super_admin()
        context['is_startup_admin'] = request.user.is_startup_admin()
        context['is_startup_hr'] = request.user.is_startup_hr()
        context['is_startup_manager'] = request.user.is_startup_manager()
        context['is_employee'] = request.user.is_employee()
        context['is_talent'] = request.user.is_talent()
        context['is_staff_user'] = request.user.is_staff or request.user.is_superuser
        
        # Check if user has HR access
        context['has_hr_access'] = (
            request.user.is_super_admin() or 
            request.user.is_startup_admin() or 
            request.user.is_startup_hr() or 
            request.user.is_startup_manager() or
            request.user.is_staff or 
            request.user.is_superuser
        )
        
        # Get startup info
        if request.user.startup:
            context['user_startup'] = request.user.startup
            context['user_startup_id'] = request.user.startup.id
            context['user_startup_name'] = request.user.startup.company_name
        else:
            context['user_startup'] = None
            context['user_startup_id'] = None
            context['user_startup_name'] = None
        
        # Check if user has employee profile
        try:
            employee = Employee.objects.get(user=request.user)
            context['has_employee_profile'] = True
            context['employee_profile'] = employee
            context['employee_id'] = employee.id
            context['employee_name'] = employee.user.get_full_name()
        except Employee.DoesNotExist:
            context['has_employee_profile'] = False
            context['employee_profile'] = None
            context['employee_id'] = None
            context['employee_name'] = None
    
    return context


# core/context_processors.py

from people.models import Employee


def user_roles(request):
    """
    Add user role information to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        # Basic role checks
        context['is_super_admin'] = request.user.is_super_admin()
        context['is_startup_admin'] = request.user.is_startup_admin()
        context['is_startup_hr'] = request.user.is_startup_hr()
        context['is_startup_manager'] = request.user.is_startup_manager()
        context['is_employee'] = request.user.is_employee()
        context['is_talent'] = request.user.is_talent()
        context['is_staff_user'] = request.user.is_staff or request.user.is_superuser
        
        # Check if user has HR access
        context['has_hr_access'] = (
            request.user.is_super_admin() or 
            request.user.is_startup_admin() or 
            request.user.is_startup_hr() or 
            request.user.is_startup_manager() or
            request.user.is_staff or 
            request.user.is_superuser
        )
        
        # Get startup info
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
        
        # Check if user has employee profile
        try:
            employee = Employee.objects.get(user=request.user)
            context['has_employee_profile'] = True
            context['employee_profile'] = employee
            context['employee_id'] = employee.id
            context['employee_name'] = employee.user.get_full_name()
        except Employee.DoesNotExist:
            context['has_employee_profile'] = False
            context['employee_profile'] = None
            context['employee_id'] = None
            context['employee_name'] = None
    
    return context


# Alias for backward compatibility
startup_context = user_roles