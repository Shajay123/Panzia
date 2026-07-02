# views.py - Complete People Views

import os
from datetime import date, timedelta
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, models
from django.db.models import Q, Sum
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa

from accounts.models import User
from startups.models import StartupProfile

from .forms import (
    AttendanceForm,
    DepartmentForm,
    DepartmentTimingConfigForm,
    EmployeeDocumentForm,
    EmployeeForm,
    EmployeeLeaveRequestForm,
    EmployeeTimingConfigForm,
    ExitFilterForm,
    ExitRequestForm,
    HolidayFilterForm,
    HolidayForm,
    LeaveRequestFilterForm,
    LeaveRequestForm,
    PayrollFilterForm,
    PayrollForm,
    PayslipForm,
    PerformanceFilterForm,
    PerformanceReviewForm,
)
from .models import (
    Attendance,
    Department,
    DepartmentTimingConfig,
    Employee,
    EmployeeDocument,
    ExitRequest,
    Holiday,
    LeaveRequest,
    Payroll,
    Payslip,
    PerformanceReview,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

# people/views.py - Fixed get_startup

# people/views.py - Fixed get_startup

# people/views.py - Fixed get_startup

# people/views.py - Helper functions at the top

def get_startup(request):
    """Get the startup associated with the current user"""
    
    # Method 1: Check OneToOne relationship (user.startup_profile)
    if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
        return request.user.startup_profile
    
    # Method 2: Check ForeignKey relationship (user.startup)
    if request.user.startup:
        return request.user.startup
    
    # Method 3: If user is super admin, they may not have a startup
    if request.user.is_super_admin():
        startup_id = request.session.get('selected_startup_id')
        if startup_id:
            try:
                return StartupProfile.objects.get(id=startup_id)
            except StartupProfile.DoesNotExist:
                pass
        return None
    
    # Method 4: Check if user is an employee with a startup
    try:
        employee = Employee.objects.get(user=request.user)
        if employee.startup:
            return employee.startup
    except Employee.DoesNotExist:
        pass
    
    # Method 5: Last resort - try to get from database
    try:
        return StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        return None


def get_current_startup(request):
    """
    Get the current startup based on user and session.
    Super admin can switch startups.
    """
    if request.user.is_super_admin():
        selected_id = request.session.get('selected_startup_id')
        if selected_id:
            try:
                return StartupProfile.objects.get(id=selected_id, is_active=True)
            except StartupProfile.DoesNotExist:
                if 'selected_startup_id' in request.session:
                    del request.session['selected_startup_id']
                return None
        return None
    
    # Check OneToOne relationship
    if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
        return request.user.startup_profile
    
    # Check ForeignKey relationship
    if request.user.startup:
        return request.user.startup
    
    # Try database
    try:
        return StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        return None


def get_employee_or_redirect(request):
    """
    Helper function to get employee profile or redirect with message.
    """
    try:
        # Get employee for the current user
        employee = Employee.objects.get(user=request.user)
        
        # Check if employee has a startup
        if not employee.startup:
            messages.error(request, 'No startup associated with your employee profile.')
            return None, 'people_dashboard'
            
        return employee, None
        
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR.')
        return None, 'people_dashboard'


def generate_payslip_pdf(payslip):
    """Generate PDF from HTML template and save to payslip."""
    payroll = payslip.payroll
    employee = payroll.employee
    startup = employee.startup

    context = {
        'payslip': payslip,
        'payroll': payroll,
        'employee': employee,
        'startup': startup,
        'company_name': startup.company_name,
        'generated_date': timezone.now().strftime('%d %B %Y'),
        'generated_time': timezone.now().strftime('%H:%M:%S'),
    }

    html_string = render_to_string('people/payslip_template.html', context)
    payslip.html_content = html_string

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        filename = f"payslip_{employee.employee_id}_{payroll.month}_{payroll.year}_{payslip.id}.pdf"
        payslip_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
        os.makedirs(payslip_dir, exist_ok=True)

        file_path = os.path.join(payslip_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(result.getvalue())

        relative_path = os.path.join('payslips', filename)
        payslip.pdf = relative_path
        payslip.is_generated = True
        payslip.generated_at = timezone.now()
        payslip.save()
        return True
    return False


# people/views.py - Add this view

# people/views.py - Fixed role_based_dashboard

@login_required
def role_based_dashboard(request):
    """
    Redirect users to the appropriate dashboard based on their role
    """
    user = request.user
    
    # Super Admin → People Dashboard (all startups)
    if user.is_super_admin() or user.is_superuser:
        return redirect('people_dashboard')
    
    # Startup Admin, HR, Manager → People Dashboard (their startup)
    if user.is_startup_admin() or user.is_startup_hr() or user.is_startup_manager():
        return redirect('people_dashboard')
    
    # Employee → Employee Portal
    if user.is_employee():
        try:
            employee = Employee.objects.get(user=user)
            return redirect('employee_portal_dashboard')
        except Employee.DoesNotExist:
            messages.error(request, 'Employee profile not found.')
            return redirect('people_dashboard')
    
    # Talent → Talent Dashboard
    if user.is_talent():
        return redirect('talent_dashboard')
    
    # Default fallback
    return redirect('people_dashboard')


# people/views.py - Add these views

@login_required
def employee_timing_config(request, employee_id):
    """Configure employee attendance timings"""
    startup = get_startup(request)
    employee = get_object_or_404(Employee, id=employee_id, startup=startup)
    
    # Check permission
    if not request.user.is_super_admin() and request.user.role not in ['startup_admin', 'startup_hr']:
        messages.error(request, 'You do not have permission to configure timings.')
        return redirect('employee_detail', id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeTimingConfigForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Timing configuration for {employee.user.get_full_name()} updated successfully!')
            return redirect('employee_detail', id=employee_id)
    else:
        form = EmployeeTimingConfigForm(instance=employee)
    
    context = {
        'employee': employee,
        'form': form,
        'page_title': f'Timing Config - {employee.user.get_full_name()}',
        'page_icon': '⏰'
    }
    return render(request, 'people/timing_config.html', context)


@login_required
def department_timing_config(request, department_id):
    """Configure department-level attendance timings"""
    startup = get_startup(request)
    department = get_object_or_404(Department, id=department_id, startup=startup)
    
    # Check permission
    if not request.user.is_super_admin() and request.user.role not in ['startup_admin', 'startup_hr']:
        messages.error(request, 'You do not have permission to configure department timings.')
        return redirect('department_detail', id=department_id)
    
    config, created = DepartmentTimingConfig.objects.get_or_create(department=department)
    
    if request.method == 'POST':
        form = DepartmentTimingConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, f'Timing configuration for {department.name} updated successfully!')
            return redirect('department_detail', id=department_id)
    else:
        form = DepartmentTimingConfigForm(instance=config)
    
    context = {
        'department': department,
        'form': form,
        'config': config,
        'page_title': f'Timing Config - {department.name}',
        'page_icon': '⏰'
    }
    return render(request, 'people/department_timing_config.html', context)


@login_required
def get_employee_timing(request, employee_id):
    """API endpoint to get employee timing configuration"""
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # Get employee-specific settings, fallback to department, then global
        check_in = employee.default_check_in
        check_out = employee.default_check_out
        
        # If not set at employee level, check department
        if not check_in and employee.department:
            dept_config = DepartmentTimingConfig.objects.filter(department=employee.department).first()
            if dept_config:
                check_in = dept_config.work_start_time
                check_out = dept_config.work_end_time
        
        # If still not set, use global defaults
        if not check_in:
            check_in = '09:30'
        if not check_out:
            check_out = '18:30'
        
        return JsonResponse({
            'success': True,
            'data': {
                'default_check_in': str(check_in) if check_in else '09:30',
                'default_check_out': str(check_out) if check_out else '18:30',
                'grace_period': employee.grace_period_minutes or 15,
                'half_day_hours': float(employee.half_day_hours or 4.00),
                'full_day_hours': float(employee.full_day_hours or 8.00),
                'shift': employee.shift or 'morning'
            }
        })
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)

# ============================================================
# DASHBOARD & STARTUP SWITCHING
# ============================================================

# people/views.py - Updated context for people_dashboard

@login_required
def people_dashboard(request):
    """HR Dashboard - Only for startup admins/HR/managers"""
    
    # Check if user has HR access based on role
    has_hr_role = request.user.role in ['startup_admin', 'startup_hr', 'startup_manager']
    
    # If user is a super admin, they have access
    if request.user.is_super_admin() or request.user.is_superuser:
        has_hr_role = True
    
    # If user is staff, they have access
    if request.user.is_staff:
        has_hr_role = True
    
    # If user does NOT have HR access, redirect to employee portal
    if not has_hr_role:
        try:
            employee = Employee.objects.get(user=request.user)
            messages.info(request, 'You do not have HR access. Redirecting to employee portal.')
            return redirect('employee_portal_dashboard')
        except Employee.DoesNotExist:
            messages.error(request, 'You do not have permission to access the HR dashboard.')
            return redirect('home')
    
    # Get startup - check both OneToOne and ForeignKey relationships
    startup = None
    
    # Check OneToOne relationship (startup_profile)
    if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
        startup = request.user.startup_profile
    # Check ForeignKey relationship (startup)
    elif request.user.startup:
        startup = request.user.startup
    
    # If user is an employee, try to get startup from employee profile
    if not startup:
        try:
            employee = Employee.objects.get(user=request.user)
            if employee.startup:
                startup = employee.startup
        except Employee.DoesNotExist:
            pass
    
    # If still no startup and not super admin, redirect to setup
    if not startup and not request.user.is_super_admin():
        messages.error(request, 'No startup associated with your account. Please complete your startup profile setup.')
        return redirect('startup_profile_setup')
    
    # If super admin without startup, create one or handle gracefully
    if not startup and request.user.is_super_admin():
        messages.info(request, 'You are viewing as super admin. Please select or create a startup profile.')
        return redirect('startup_profile_setup')
    
    # Regular dashboard flow
    today = date.today()
    
    if request.user.is_super_admin():
        if startup:
            recent_employees = Employee.objects.filter(startup=startup).order_by("-created_at")[:5]
            employee_count = Employee.objects.filter(startup=startup).count()
            present_today = Attendance.objects.filter(employee__startup=startup, date=today, status="Present").count()
            
            # Calculate attendance percentage safely
            attendance_percentage = 0
            if employee_count > 0:
                attendance_percentage = round((present_today / employee_count) * 100)
            
            context = {
                "employee_count": employee_count,
                "department_count": Department.objects.filter(startup=startup).count(),
                "attendance_count": Attendance.objects.filter(employee__startup=startup).count(),
                "leave_count": LeaveRequest.objects.filter(employee__startup=startup).count(),
                "payroll_count": Payroll.objects.filter(employee__startup=startup).count(),
                "recent_employees": recent_employees,
                "present_today": present_today,
                "absent_today": Attendance.objects.filter(employee__startup=startup, date=today, status="Absent").count(),
                "wfh_today": Attendance.objects.filter(employee__startup=startup, date=today, status="WFH").count(),
                "leave_today": Attendance.objects.filter(employee__startup=startup, date=today, status="Leave").count(),
                "current_startup": startup,
                "is_super_admin": True,
                "today": today,
                "attendance_percentage": attendance_percentage,
            }
        else:
            recent_employees = Employee.objects.all().order_by("-created_at")[:5]
            employee_count = Employee.objects.count()
            present_today = Attendance.objects.filter(date=today, status="Present").count()
            
            attendance_percentage = 0
            if employee_count > 0:
                attendance_percentage = round((present_today / employee_count) * 100)
            
            context = {
                "employee_count": employee_count,
                "department_count": Department.objects.count(),
                "attendance_count": Attendance.objects.count(),
                "leave_count": LeaveRequest.objects.count(),
                "payroll_count": Payroll.objects.count(),
                "recent_employees": recent_employees,
                "present_today": present_today,
                "absent_today": Attendance.objects.filter(date=today, status="Absent").count(),
                "wfh_today": Attendance.objects.filter(date=today, status="WFH").count(),
                "leave_today": Attendance.objects.filter(date=today, status="Leave").count(),
                "current_startup": None,
                "is_super_admin": True,
                "today": today,
                "attendance_percentage": attendance_percentage,
            }
        return render(request, "people/dashboard.html", context)
    
    # Regular HR user flow
    if not startup:
        messages.error(request, 'No startup associated with your account. Please complete your startup profile setup.')
        return redirect('startup_profile_setup')
    
    recent_employees = Employee.objects.filter(startup=startup).order_by("-created_at")[:5]
    employee_count = Employee.objects.filter(startup=startup).count()
    present_today = Attendance.objects.filter(employee__startup=startup, date=today, status="Present").count()
    
    attendance_percentage = 0
    if employee_count > 0:
        attendance_percentage = round((present_today / employee_count) * 100)
    
    context = {
        "employee_count": employee_count,
        "department_count": Department.objects.filter(startup=startup).count(),
        "attendance_count": Attendance.objects.filter(employee__startup=startup).count(),
        "leave_count": LeaveRequest.objects.filter(employee__startup=startup).count(),
        "payroll_count": Payroll.objects.filter(employee__startup=startup).count(),
        "recent_employees": recent_employees,
        "present_today": present_today,
        "absent_today": Attendance.objects.filter(employee__startup=startup, date=today, status="Absent").count(),
        "wfh_today": Attendance.objects.filter(employee__startup=startup, date=today, status="WFH").count(),
        "leave_today": Attendance.objects.filter(employee__startup=startup, date=today, status="Leave").count(),
        "current_startup": startup,
        "is_super_admin": False,
        "today": today,
        "attendance_percentage": attendance_percentage,
    }
    return render(request, "people/dashboard.html", context)




@login_required
def switch_startup(request, startup_id):
    """Allow super admin to switch between startups."""
    if not request.user.is_super_admin():
        messages.error(request, 'You do not have permission to switch startups.')
        return redirect('people_dashboard')

    startup = get_object_or_404(StartupProfile, id=startup_id)
    request.session['selected_startup_id'] = startup.id
    messages.success(request, f'Switched to {startup.company_name} workspace.')

    next_url = request.GET.get('next', 'people_dashboard')
    return redirect(next_url)


@login_required
def reset_startup_view(request):
    """Reset startup view to show all startups (super admin only)."""
    if not request.user.is_super_admin():
        messages.error(request, 'You do not have permission to reset startup view.')
        return redirect('people_dashboard')

    if 'selected_startup_id' in request.session:
        del request.session['selected_startup_id']
        messages.success(request, 'Viewing all startups.')

    next_url = request.GET.get('next', 'people_dashboard')
    return redirect(next_url)


@login_required
def get_startup_list(request):
    """API endpoint to get list of startups for the switch dropdown."""
    if not request.user.is_super_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    startups = StartupProfile.objects.filter(is_active=True)
    data = []
    for startup in startups:
        data.append({
            'id': startup.id,
            'company_name': startup.company_name,
            'employee_count': startup.get_employee_count(),
        })
    return JsonResponse({'startups': data})


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================

@login_required
def employees(request):
    """Employee list - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        employees_list = Employee.objects.select_related("user", "department", "manager").order_by("user__first_name", "user__last_name")
        departments = Department.objects.all()
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        employees_list = Employee.objects.filter(startup=startup).select_related("user", "department", "manager").order_by("user__first_name", "user__last_name")
        departments = Department.objects.filter(startup=startup)

    context = {
        "employees": employees_list,
        "departments": departments,
        "active_count": employees_list.filter(is_active=True).count(),
        "payroll_enabled": employees_list.filter(is_payroll_enabled=True).count(),
    }
    return render(request, "people/employees.html", context)


@login_required
def employee_create(request):
    """Create employee - Only for startup users."""
    startup = request.user.startup

    if not startup and not request.user.is_super_admin():
        messages.error(request, 'You need to have a startup to add employees.')
        return redirect('startup_profile_setup')
    
    # Get departments
    departments = Department.objects.filter(startup=startup) if startup else Department.objects.all()
    
    # Check if departments exist
    if not departments.exists():
        messages.warning(request, 'Please create at least one department before adding employees.')
        # Don't redirect, let them see the warning and create department

    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES, startup=startup)

        if form.is_valid():
            employee_id = form.cleaned_data.get("employee_id")

            if startup and Employee.objects.filter(startup=startup, employee_id=employee_id).exists():
                form.add_error('employee_id', f"An employee with ID '{employee_id}' already exists in your startup.")
            else:
                hire_mode = request.POST.get("hire_mode")
                user = None

                if hire_mode == "talent":
                    talent_user_id = request.POST.get("talent_user")
                    if talent_user_id:
                        user = get_object_or_404(User, id=talent_user_id, role="talent")
                elif hire_mode == "existing":
                    existing_user_id = request.POST.get("existing_user")
                    if existing_user_id:
                        user = get_object_or_404(User, id=existing_user_id)
                else:
                    username = request.POST.get("username")
                    email = request.POST.get("email")
                    first_name = request.POST.get("first_name")
                    last_name = request.POST.get("last_name")

                    if username and email:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            password="ChangeMe@123",
                            role="employee",
                            startup=startup
                        )

                if user:
                    employee = form.save(commit=False)
                    employee.startup = startup
                    employee.user = user
                    employee.is_active = True
                    
                    # ============================================
                    # SAVE TIMING CONFIGURATION FROM FORM
                    # ============================================
                    default_check_in = request.POST.get('default_check_in')
                    default_check_out = request.POST.get('default_check_out')
                    grace_period = request.POST.get('grace_period')
                    shift_type = request.POST.get('shift_type')
                    half_day_hours = request.POST.get('half_day_hours')
                    full_day_hours = request.POST.get('full_day_hours')
                    overtime_enabled = request.POST.get('overtime_enabled') == 'on'
                    
                    if default_check_in:
                        employee.default_check_in = default_check_in
                    if default_check_out:
                        employee.default_check_out = default_check_out
                    if grace_period:
                        employee.grace_period_minutes = int(grace_period) if grace_period else 15
                    if shift_type:
                        employee.shift = shift_type
                    if half_day_hours:
                        employee.half_day_hours = float(half_day_hours) if half_day_hours else 4.00
                    if full_day_hours:
                        employee.full_day_hours = float(full_day_hours) if full_day_hours else 8.00
                    employee.overtime_enabled = overtime_enabled
                    
                    employee.save()
                    
                    messages.success(request, f'Employee "{employee.user.get_full_name()}" added successfully with timing configuration!')
                    return redirect("employees")
    else:
        form = EmployeeForm(startup=startup)

    if startup:
        talent_users = User.objects.filter(role="talent", startup=startup).exclude(employee__isnull=False)
        existing_users = User.objects.filter(employee__isnull=True, startup=startup).exclude(role="talent")
    else:
        talent_users = User.objects.filter(role="talent").exclude(employee__isnull=False)
        existing_users = User.objects.filter(employee__isnull=True).exclude(role="talent")

    return render(request, "people/employee_create.html", {
        "form": form,
        "talent_users": talent_users,
        "existing_users": existing_users,
        "departments": departments,
    })


@login_required
def employee_detail(request, id):
    """Employee detail view."""
    startup = get_startup(request)
    employee = get_object_or_404(Employee, id=id, startup=startup)

    context = {
        "employee": employee,
        "attendance_count": Attendance.objects.filter(employee=employee).count(),
        "leave_count": LeaveRequest.objects.filter(employee=employee).count(),
    }
    return render(request, "people/employee_detail.html", context)


@login_required
def employee_update(request, id):
    """Update employee."""
    startup = get_startup(request)
    employee = get_object_or_404(Employee, id=id, startup=startup)

    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect("employee_detail", id=employee.id)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, "people/employee_update.html", {"form": form, "employee": employee})


@login_required
def employee_delete(request, id):
    """Delete employee."""
    startup = get_startup(request)
    employee = get_object_or_404(Employee, id=id, startup=startup)

    if request.method == "POST":
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect("employees")

    return render(request, "people/employee_delete.html", {"employee": employee})


# ============================================================
# EMPLOYEE PORTAL
# ============================================================

@login_required
def employee_portal_dashboard(request):
    """Employee dashboard - self service portal."""
    
    # ============================================
    # CHECK IF USER IS EMPLOYEE - FIXED
    # ============================================
    
    # If user is not an employee, redirect to appropriate dashboard
    if request.user.role != 'employee':
        messages.warning(request, 'This portal is for employees only.')
        # Redirect based on role
        if request.user.role in ['startup_admin', 'startup_hr', 'startup_manager']:
            return redirect('people_dashboard')
        elif request.user.role == 'talent':
            return redirect('talent_dashboard')
        else:
            return redirect('dashboard_home')
    
    # ============================================
    # GET EMPLOYEE PROFILE
    # ============================================
    
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR.')
        return redirect('people_dashboard')
    
    # Check if employee has a startup
    if not employee.startup:
        messages.error(request, 'No startup associated with your employee profile.')
        return redirect('people_dashboard')

    # ============================================
    # ATTENDANCE CALCULATIONS
    # ============================================
    
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    # Today's attendance
    attendance_today = Attendance.objects.filter(employee=employee, date=today).first()
    
    # Last 30 days attendance
    attendance_last_30 = Attendance.objects.filter(
        employee=employee, 
        date__gte=last_30_days, 
        date__lte=today
    )
    
    total_days = attendance_last_30.count()
    present_days = attendance_last_30.filter(status='Present').count()
    absent_days = attendance_last_30.filter(status='Absent').count()
    leave_days = attendance_last_30.filter(status='Leave').count()
    wfh_days = attendance_last_30.filter(status='WFH').count()
    
    attendance_percentage = round((present_days / total_days) * 100, 1) if total_days > 0 else 0

    # ============================================
    # LEAVE CALCULATIONS
    # ============================================
    
    pending_leaves = LeaveRequest.objects.filter(employee=employee, status='Pending').count()
    approved_leaves = LeaveRequest.objects.filter(employee=employee, status='Approved').count()
    rejected_leaves = LeaveRequest.objects.filter(employee=employee, status='Rejected').count()
    total_leaves = LeaveRequest.objects.filter(employee=employee).count()

    upcoming_leaves = LeaveRequest.objects.filter(
        employee=employee, 
        status__in=['Pending', 'Approved'], 
        from_date__gte=today
    ).order_by('from_date')[:5]

    recent_attendance = Attendance.objects.filter(employee=employee).order_by('-date')[:7]

    # ============================================
    # PAYROLL
    # ============================================
    
    latest_payroll = Payroll.objects.filter(employee=employee).order_by('-year', '-month').first()
    payrolls = Payroll.objects.filter(employee=employee).order_by('-year', '-month')[:3]
    
    # ============================================
    # DOCUMENTS
    # ============================================
    
    documents_count = EmployeeDocument.objects.filter(employee=employee).count()

    # ============================================
    # CONTEXT
    # ============================================
    
    context = {
        'employee': employee,
        'attendance_today': attendance_today,
        'attendance_percentage': attendance_percentage,
        'present_days': present_days,
        'absent_days': absent_days,
        'leave_days': leave_days,
        'wfh_days': wfh_days,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'total_leaves': total_leaves,
        'upcoming_leaves': upcoming_leaves,
        'recent_attendance': recent_attendance,
        'latest_payroll': latest_payroll,
        'payrolls': payrolls,
        'documents_count': documents_count,
        'page_title': 'Employee Dashboard',
        'page_icon': '👤',
        'is_employee_portal': True,  # Add this flag for templates
    }
    
    return render(request, 'people/employee_portal/dashboard.html', context)


@login_required
def employee_portal_profile(request):
    """Employee profile view - Preview Only."""
    
    # Check if user is an employee
    if request.user.role != 'employee':
        messages.warning(request, 'This portal is for employees only.')
        return redirect('people_dashboard')
    
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR.')
        return redirect('people_dashboard')

    return render(request, 'people/employee_portal/profile_preview.html', {
        'employee': employee,
        'page_title': 'My Profile',
        'page_icon': '👤',
        'is_employee_portal': True,
    })


@login_required
def employee_portal_attendance(request):
    """Employee attendance view - View Only."""
    
    # Check if user is an employee
    if request.user.role != 'employee':
        messages.warning(request, 'This portal is for employees only.')
        return redirect('people_dashboard')
    
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR.')
        return redirect('people_dashboard')

    attendances = Attendance.objects.filter(employee=employee).order_by('-date')

    # Filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    status = request.GET.get('status')

    if from_date:
        attendances = attendances.filter(date__gte=from_date)
    if to_date:
        attendances = attendances.filter(date__lte=to_date)
    if status:
        attendances = attendances.filter(status=status)

    total_days = attendances.count()
    present_days = attendances.filter(status='Present').count()
    absent_days = attendances.filter(status='Absent').count()
    leave_days = attendances.filter(status='Leave').count()
    wfh_days = attendances.filter(status='WFH').count()
    attendance_percentage = round((present_days / total_days) * 100, 1) if total_days > 0 else 0

    context = {
        'employee': employee,
        'attendances': attendances,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'leave_days': leave_days,
        'wfh_days': wfh_days,
        'attendance_percentage': attendance_percentage,
        'page_title': 'My Attendance',
        'page_icon': '🕒',
        'is_employee_portal': True,
    }
    return render(request, 'people/employee_portal/attendance.html', context)


# people/views.py - Updated employee_portal_attendance_mark

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# people/views.py - Update employee_portal_attendance_mark

@login_required
@login_required
def employee_portal_attendance_mark(request):
    """Employee mark their own attendance with photo capture."""
    
    # Check if user is an employee
    if request.user.role != 'employee':
        messages.warning(request, 'This portal is for employees only.')
        return redirect('people_dashboard')
    
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR.')
        return redirect('people_dashboard')

    today = timezone.now().date()
    existing_attendance = Attendance.objects.filter(employee=employee, date=today).first()

    if request.method == 'POST':
        status = request.POST.get('status', 'Present')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        notes = request.POST.get('notes', '')
        photo_data = request.POST.get('photo_data')
        location_lat = request.POST.get('location_lat')
        location_lng = request.POST.get('location_lng')
        location_address = request.POST.get('location_address')
        
        # ============================================
        # FIX: Handle empty time values
        # ============================================
        # Convert empty strings to None for time fields
        if check_in == '':
            check_in = None
        if check_out == '':
            check_out = None
        
        # Validate check-in/out
        if check_in and check_out and check_in >= check_out:
            messages.error(request, 'Check Out time must be after Check In time.')
            return redirect('employee_portal_attendance_mark')
        
        # Auto-detect check-in status based on time
        check_in_status = None
        if check_in:
            try:
                check_in_time = datetime.strptime(check_in, '%H:%M').time()
            except ValueError:
                try:
                    check_in_time = datetime.strptime(check_in, '%H:%M:%S').time()
                except ValueError:
                    check_in_time = None
                    
            if check_in_time:
                work_start = datetime.strptime('09:30', '%H:%M').time()
                
                if check_in_time < work_start:
                    check_in_status = 'early'
                elif check_in_time == work_start:
                    check_in_status = 'on_time'
                else:
                    check_in_dt = datetime.combine(today, check_in_time)
                    work_start_dt = datetime.combine(today, work_start)
                    diff_minutes = (check_in_dt - work_start_dt).total_seconds() / 60
                    
                    if diff_minutes <= 15:
                        check_in_status = 'slightly_late'
                    elif diff_minutes <= 30:
                        check_in_status = 'late'
                    else:
                        check_in_status = 'very_late'

        # ============================================
        # HANDLE PHOTO UPLOAD
        # ============================================
        photo_file = None
        if photo_data and photo_data != 'existing' and photo_data != '':
            import base64
            from django.core.files.base import ContentFile
            
            try:
                # Check if it's a base64 string
                if ';base64,' in photo_data:
                    format, imgstr = photo_data.split(';base64,')
                    ext = format.split('/')[-1]
                else:
                    imgstr = photo_data
                    ext = 'jpg'
                
                # Create filename
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                filename = f"attendance_{employee.employee_id}_{today.strftime('%Y%m%d')}_{timestamp}.{ext}"
                
                # Decode and save
                photo_file = ContentFile(base64.b64decode(imgstr), name=filename)
                
            except Exception as e:
                print(f"Error processing photo: {e}")
                messages.warning(request, 'There was an issue with the photo. Please try again.')

        # ============================================
        # SAVE ATTENDANCE
        # ============================================
        
        if existing_attendance:
            # Update existing attendance
            existing_attendance.status = status
            
            # Only update time fields if they have values
            if check_in is not None:
                existing_attendance.check_in = check_in
                existing_attendance.check_in_status = check_in_status
            if check_out is not None:
                existing_attendance.check_out = check_out
                
            if photo_file:
                # Delete old photo if exists
                if existing_attendance.photo:
                    try:
                        existing_attendance.photo.delete(save=False)
                    except:
                        pass
                existing_attendance.photo = photo_file
                
            if location_lat and location_lng:
                existing_attendance.location_lat = location_lat
                existing_attendance.location_lng = location_lng
                existing_attendance.location_address = location_address
                
            existing_attendance.notes = notes
            existing_attendance.device_info = request.META.get('HTTP_USER_AGENT', '')[:255]
            existing_attendance.ip_address = request.META.get('REMOTE_ADDR', '')
            existing_attendance.save()
            
            messages.success(request, 'Attendance updated successfully!')
        else:
            # Create new attendance
            attendance = Attendance.objects.create(
                employee=employee,
                date=today,
                status=status,
                check_in=check_in,  # This will be None if empty
                check_out=check_out,  # This will be None if empty
                check_in_status=check_in_status,
                notes=notes,
                photo=photo_file,
                location_lat=location_lat,
                location_lng=location_lng,
                location_address=location_address,
                device_info=request.META.get('HTTP_USER_AGENT', '')[:255],
                ip_address=request.META.get('REMOTE_ADDR', '')
            )
            messages.success(request, 'Attendance marked successfully!')

        return redirect('employee_portal_attendance')

    context = {
        'employee': employee,
        'existing_attendance': existing_attendance,
        'today': today,
        'page_title': 'Mark Attendance',
        'page_icon': '🕒',
        'work_start': '09:30',
        'grace_period': 15,
    }
    return render(request, 'people/employee_portal/attendance_mark.html', context)

# people/views.py - Add this at the top with other imports

from datetime import datetime, date, timedelta  # Add 'datetime' to the import
@csrf_exempt
@login_required
def attendance_upload_photo(request):
    """AJAX endpoint to upload attendance photo."""
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            employee = Employee.objects.get(user=request.user)
            today = timezone.now().date()
            
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={'status': 'Present'}
            )
            
            attendance.photo = request.FILES['photo']
            attendance.save()
            
            return JsonResponse({
                'success': True,
                'photo_url': attendance.photo.url
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def employee_portal_leave(request):
    """Employee leave view - View Only."""
    employee, redirect_url = get_employee_or_redirect(request)
    if not employee:
        return redirect(redirect_url or 'people_dashboard')

    leaves = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    context = {
        'employee': employee,
        'leaves': leaves,
        'pending_count': leaves.filter(status='Pending').count(),
        'approved_count': leaves.filter(status='Approved').count(),
        'rejected_count': leaves.filter(status='Rejected').count(),
        'page_title': 'My Leaves',
        'page_icon': '🌴'
    }
    return render(request, 'people/employee_portal/leave.html', context)


@login_required
def employee_portal_leave_create(request):
    """Employee create leave request - Apply Only."""
    
    # Check if user is an employee
    if request.user.role != 'employee':
        messages.warning(request, 'This portal is for employees only.')
        return redirect('people_dashboard')
    
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR.')
        return redirect('people_dashboard')

    if request.method == 'POST':
        form = EmployeeLeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = 'Pending'
            leave.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('employee_portal_leave')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeLeaveRequestForm()

    context = {
        'form': form,
        'employee': employee,
        'page_title': 'Apply for Leave',
        'page_icon': '📝',
        'is_employee_portal': True,
    }
    return render(request, 'people/employee_portal/leave_create.html', context)


@login_required
def employee_portal_leave_detail(request, id):
    """Employee leave detail view."""
    employee, redirect_url = get_employee_or_redirect(request)
    if not employee:
        return redirect(redirect_url or 'people_dashboard')

    leave = get_object_or_404(LeaveRequest, id=id, employee=employee)
    duration = (leave.to_date - leave.from_date).days + 1

    context = {
        'employee': employee,
        'leave': leave,
        'duration': duration,
        'page_title': 'Leave Details',
        'page_icon': '📋'
    }
    return render(request, 'people/employee_portal/leave_detail.html', context)


@login_required
def employee_portal_payroll(request):
    """Employee payroll view - View Only."""
    employee, redirect_url = get_employee_or_redirect(request)
    if not employee:
        return redirect(redirect_url or 'people_dashboard')

    payrolls = Payroll.objects.filter(employee=employee).order_by('-year', '-month')

    context = {
        'employee': employee,
        'payrolls': payrolls,
        'page_title': 'My Payroll',
        'page_icon': '💰'
    }
    return render(request, 'people/employee_portal/payroll.html', context)


@login_required
def employee_portal_payslips(request):
    """Employee payslips view - View Only."""
    employee, redirect_url = get_employee_or_redirect(request)
    if not employee:
        return redirect(redirect_url or 'people_dashboard')

    payslips = Payslip.objects.filter(payroll__employee=employee).order_by('-generated_at')

    context = {
        'employee': employee,
        'payslips': payslips,
        'page_title': 'My Payslips',
        'page_icon': '🧾'
    }
    return render(request, 'people/employee_portal/payslips.html', context)


# ============================================================
# DEPARTMENTS
# ============================================================

@login_required
def departments(request):
    """Departments list - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        departments_list = Department.objects.all().prefetch_related("employee_set")
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        departments_list = Department.objects.filter(startup=startup).prefetch_related("employee_set")

    return render(request, "people/departments.html", {"departments": departments_list})


@login_required
def department_create(request):
    """Create department."""
    startup = request.user.startup

    if not startup and not request.user.is_super_admin():
        messages.error(request, 'No startup associated with your account.')
        return redirect('startup_profile_setup')

    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.startup = startup
            department.save()
            messages.success(request, "Department created successfully.")
            return redirect("departments")
    else:
        form = DepartmentForm()

    return render(request, "people/department_create.html", {"form": form})


@login_required
def department_detail(request, id):
    """Department detail."""
    startup = get_startup(request)
    department = get_object_or_404(Department, id=id, startup=startup)
    employees_list = Employee.objects.filter(department=department)

    return render(request, "people/department_detail.html", {
        "department": department,
        "employees": employees_list
    })


@login_required
def department_update(request, id):
    """Update department."""
    startup = get_startup(request)
    department = get_object_or_404(Department, id=id, startup=startup)

    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect("department_detail", id=department.id)
    else:
        form = DepartmentForm(instance=department)

    return render(request, "people/department_update.html", {"form": form, "department": department})


@login_required
def department_delete(request, id):
    """Delete department."""
    startup = get_startup(request)
    department = get_object_or_404(Department, id=id, startup=startup)

    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted successfully.")
        return redirect("departments")

    return render(request, "people/department_delete.html", {"department": department})


# ============================================================
# ATTENDANCE
# ============================================================

@login_required
def attendance(request):
    """Attendance list - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        records = Attendance.objects.select_related("employee", "employee__user").order_by("-date")
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        records = Attendance.objects.select_related("employee", "employee__user").filter(
            employee__startup=startup
        ).order_by("-date")

    today = timezone.now().date()

    # New fields for enhanced attendance
    photo = models.ImageField(upload_to='attendance_photos/', blank=True, null=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_address = models.TextField(blank=True, null=True)
    check_in_late = models.BooleanField(default=False)
    check_out_early = models.BooleanField(default=False)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    check_in_status = models.CharField(max_length=20, blank=True, null=True)  # early, on_time, late
    
    def get_working_hours(self):
        if self.check_in and self.check_out:
            from datetime import datetime
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            delta = check_out_dt - check_in_dt
            return delta.total_seconds() / 3600
        return 0
    
    def get_check_in_status(self):
        if not self.check_in:
            return 'unknown'
        
        # Define work start time (e.g., 9:30 AM)
        work_start = datetime.strptime('09:30', '%H:%M').time()
        
        if self.check_in < work_start:
            return 'early'
        elif self.check_in == work_start:
            return 'on_time'
        else:
            # Calculate how late
            diff = datetime.combine(self.date, self.check_in) - datetime.combine(self.date, work_start)
            minutes_late = diff.total_seconds() / 60
            if minutes_late <= 15:
                return 'slightly_late'
            elif minutes_late <= 30:
                return 'late'
            else:
                return 'very_late'

    

    context = {
        "attendance": records,
        "total": records.filter(date=today).count(),
        "present": records.filter(date=today, status="Present").count(),
        "absent": records.filter(date=today, status="Absent").count(),
        "leave": records.filter(date=today, status="Leave").count(),
        "wfh": records.filter(date=today, status="WFH").count(),
    }
    return render(request, "people/attendance.html", context)


@login_required
def attendance_create(request):
    """Create attendance."""
    startup = request.user.startup

    if not startup and not request.user.is_super_admin():
        messages.error(request, 'No startup associated with your account.')
        return redirect('startup_profile_setup')

    if request.user.is_super_admin():
        employees_list = Employee.objects.filter(is_active=True).select_related("user")
    else:
        employees_list = Employee.objects.filter(startup=startup, is_active=True).select_related("user")

    if request.method == "POST":
        form = AttendanceForm(request.POST, startup=startup)
        form.fields["employee"].queryset = employees_list

        if form.is_valid():
            employee = form.cleaned_data["employee"]
            date_attendance = form.cleaned_data["date"]

            if Attendance.objects.filter(employee=employee, date=date_attendance).exists():
                messages.error(request, f"Attendance already marked for {employee.user.get_full_name()} on {date_attendance}.")
            else:
                try:
                    form.save()
                    messages.success(request, "Attendance marked successfully.")
                    return redirect("attendance")
                except IntegrityError:
                    messages.error(request, "Attendance already exists for this employee.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AttendanceForm(startup=startup)
        form.fields["employee"].queryset = employees_list

    return render(request, "people/attendance_create.html", {"form": form})


@login_required
def attendance_detail(request, id):
    """Attendance detail."""
    startup = get_startup(request)
    attendance_record = get_object_or_404(Attendance, id=id, employee__startup=startup)

    return render(request, "people/attendance_detail.html", {"attendance": attendance_record})


@login_required
def attendance_update(request, id):
    """Update attendance."""
    startup = get_startup(request)
    attendance_record = get_object_or_404(Attendance, id=id, employee__startup=startup)

    employees_list = Employee.objects.filter(startup=startup, is_active=True).select_related("user")

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance_record, startup=startup)
        form.fields["employee"].queryset = employees_list

        if form.is_valid():
            form.save()
            messages.success(request, "Attendance updated.")
            return redirect("attendance_detail", id=attendance_record.id)
    else:
        form = AttendanceForm(instance=attendance_record, startup=startup)
        form.fields["employee"].queryset = employees_list

    return render(request, "people/attendance_update.html", {"form": form, "attendance": attendance_record})


@login_required
def attendance_delete(request, id):
    """Delete attendance."""
    startup = get_startup(request)
    attendance_record = get_object_or_404(Attendance, id=id, employee__startup=startup)

    if request.method == "POST":
        attendance_record.delete()
        messages.success(request, "Attendance deleted.")
        return redirect("attendance")

    return render(request, "people/attendance_delete.html", {"attendance": attendance_record})


@login_required
def attendance_report(request):
    """Attendance report."""
    startup = get_startup(request)

    records = Attendance.objects.select_related("employee", "employee__user").filter(
        employee__startup=startup
    ).order_by("-date")

    employees_list = Employee.objects.filter(startup=startup).select_related("user")

    # Filters
    employee = request.GET.get("employee")
    status = request.GET.get("status")
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    if employee:
        records = records.filter(employee_id=employee)
    if status:
        records = records.filter(status=status)
    if from_date:
        records = records.filter(date__gte=from_date)
    if to_date:
        records = records.filter(date__lte=to_date)

    present = records.filter(status="Present").count()
    absent = records.filter(status="Absent").count()
    leave = records.filter(status="Leave").count()
    wfh = records.filter(status="WFH").count()
    total = records.count()
    attendance_percentage = round((present / total) * 100, 2) if total else 0

    context = {
        "records": records,
        "employees": employees_list,
        "present_count": present,
        "absent_count": absent,
        "leave_count": leave,
        "wfh_count": wfh,
        "attendance_percentage": attendance_percentage,
    }
    return render(request, "people/attendance_report.html", context)


# ============================================================
# LEAVE MANAGEMENT
# ============================================================

@login_required
def leave_dashboard(request):
    """Leave dashboard - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        records = LeaveRequest.objects.all()
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        records = LeaveRequest.objects.filter(employee__startup=startup)

    context = {
        "pending": records.filter(status="Pending").count(),
        "approved": records.filter(status="Approved").count(),
        "rejected": records.filter(status="Rejected").count(),
        "total": records.count(),
        "recent_requests": records.select_related("employee", "employee__user").order_by("-created_at")[:10],
        "approval_rate": round((records.filter(status="Approved").count() / records.count()) * 100, 2) if records.exists() else 0,
    }
    return render(request, "people/leave_dashboard.html", context)


@login_required
def leave_requests(request):
    """Leave requests list - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        requests = LeaveRequest.objects.select_related("employee", "employee__user", "approved_by").order_by("-created_at")
        employees_list = Employee.objects.filter(is_active=True)
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        requests = LeaveRequest.objects.select_related("employee", "employee__user", "approved_by").filter(
            employee__startup=startup
        ).order_by("-created_at")
        employees_list = Employee.objects.filter(startup=startup, is_active=True)

    filter_form = LeaveRequestFilterForm(request.GET)
    filter_form.fields["employee"].queryset = employees_list

    if filter_form.is_valid():
        employee = filter_form.cleaned_data.get("employee")
        status = filter_form.cleaned_data.get("status")
        leave_type = filter_form.cleaned_data.get("leave_type")
        from_date = filter_form.cleaned_data.get("from_date")
        to_date = filter_form.cleaned_data.get("to_date")

        if employee:
            requests = requests.filter(employee=employee)
        if status:
            requests = requests.filter(status=status)
        if leave_type:
            requests = requests.filter(leave_type=leave_type)
        if from_date:
            requests = requests.filter(from_date__gte=from_date)
        if to_date:
            requests = requests.filter(to_date__lte=to_date)

    context = {
        "requests": requests,
        "filter_form": filter_form,
        "employees": employees_list,
        "pending_count": requests.filter(status="Pending").count(),
        "approved_count": requests.filter(status="Approved").count(),
        "rejected_count": requests.filter(status="Rejected").count(),
        "total_count": requests.count(),
    }
    return render(request, "people/leave_requests.html", context)


@login_required
def leave_create(request):
    """Create leave request."""
    startup = get_startup(request)
    employees_list = Employee.objects.filter(startup=startup).select_related("user")

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        form.fields["employee"].queryset = employees_list

        if form.is_valid():
            employee = form.cleaned_data["employee"]
            from_date = form.cleaned_data["from_date"]
            to_date = form.cleaned_data["to_date"]

            if from_date > to_date:
                messages.error(request, "From Date cannot be greater than To Date.")
            else:
                leave = form.save(commit=False)
                leave.status = "Pending"
                leave.approved_by = None
                leave.save()
                messages.success(request, "Leave request submitted successfully.")
                return redirect("leave_requests")
    else:
        form = LeaveRequestForm()
        form.fields["employee"].queryset = employees_list

    return render(request, "people/leave_form.html", {"form": form})


@login_required
def leave_detail(request, id):
    """View leave request details."""
    startup = get_startup(request)

    leave = get_object_or_404(
        LeaveRequest.objects.select_related('employee', 'employee__user', 'approved_by').filter(employee__startup=startup),
        id=id
    )

    duration = (leave.to_date - leave.from_date).days + 1

    context = {
        'leave': leave,
        'duration': duration,
        'page_title': f'Leave Request - {leave.employee}',
        'page_icon': '📋'
    }
    return render(request, 'people/leave_detail.html', context)


@login_required
def leave_update(request, id):
    """Update leave request."""
    startup = get_startup(request)
    leave = get_object_or_404(LeaveRequest, id=id, employee__startup=startup)

    if leave.status != "Pending":
        messages.warning(request, "Only pending requests can be edited.")
        return redirect("leave_detail", id=leave.id)

    employees_list = Employee.objects.filter(startup=startup)

    if request.method == "POST":
        form = LeaveRequestForm(request.POST, instance=leave)
        form.fields["employee"].queryset = employees_list

        if form.is_valid():
            form.save()
            messages.success(request, "Leave request updated.")
            return redirect("leave_detail", id=leave.id)
    else:
        form = LeaveRequestForm(instance=leave)
        form.fields["employee"].queryset = employees_list

    return render(request, "people/leave_form.html", {"form": form, "leave": leave, "is_edit": True})


@login_required
def leave_approve(request, id):
    """Approve leave request."""
    startup = get_startup(request)
    leave = get_object_or_404(LeaveRequest, id=id, employee__startup=startup)

    if leave.status == "Pending":
        leave.status = "Approved"
        leave.approved_by = request.user
        leave.save()
        messages.success(request, "Leave approved successfully.")

    return redirect("leave_detail", id=id)


@login_required
def leave_reject(request, id):
    """Reject leave request."""
    startup = get_startup(request)
    leave = get_object_or_404(LeaveRequest, id=id, employee__startup=startup)

    if leave.status == "Pending":
        leave.status = "Rejected"
        leave.approved_by = request.user
        leave.save()
        messages.success(request, "Leave rejected successfully.")

    return redirect("leave_detail", id=id)


@login_required
def leave_delete(request, id):
    """Delete leave request."""
    startup = get_startup(request)
    leave = get_object_or_404(LeaveRequest, id=id, employee__startup=startup)

    if request.method == "POST":
        leave.delete()
        messages.success(request, "Leave request deleted.")
        return redirect("leave_requests")

    return render(request, "people/leave_confirm_delete.html", {"leave": leave})


# ============================================================
# PAYROLL
# ============================================================

@login_required
def payroll(request):
    """Payroll list - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        payrolls = Payroll.objects.select_related("employee", "employee__user").order_by("-year", "-month")
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        payrolls = Payroll.objects.select_related("employee", "employee__user").filter(
            employee__startup=startup
        ).order_by("-year", "-month")

    filter_form = PayrollFilterForm(request.GET, startup=startup)

    if filter_form.is_valid():
        employee = filter_form.cleaned_data.get('employee')
        month = filter_form.cleaned_data.get('month')
        year = filter_form.cleaned_data.get('year')
        status = filter_form.cleaned_data.get('status')

        if employee:
            payrolls = payrolls.filter(employee=employee)
        if month:
            payrolls = payrolls.filter(month=month)
        if year:
            payrolls = payrolls.filter(year=year)
        if status == 'paid':
            payrolls = payrolls.filter(paid=True)
        elif status == 'pending':
            payrolls = payrolls.filter(paid=False)

    context = {
        "payrolls": payrolls,
        "filter_form": filter_form,
        "total_payrolls": payrolls.count(),
        "paid_count": payrolls.filter(paid=True).count(),
        "pending_count": payrolls.filter(paid=False).count(),
        "total_salary": payrolls.aggregate(total=Sum("net_salary"))["total"] or 0,
    }
    return render(request, "people/payroll.html", context)


@login_required
def payroll_create(request):
    """Create payroll."""
    startup = get_startup(request)
    employees_list = Employee.objects.filter(startup=startup, is_active=True).select_related("user")

    if request.method == "POST":
        form = PayrollForm(request.POST, startup=startup)
        form.fields["employee"].queryset = employees_list

        if form.is_valid():
            employee = form.cleaned_data["employee"]
            month = form.cleaned_data["month"]
            year = form.cleaned_data["year"]

            if Payroll.objects.filter(employee=employee, month=month, year=year).exists():
                messages.error(request, f"Payroll already exists for {employee.user.get_full_name()} ({month} {year}).")
            else:
                payroll = form.save()
                messages.success(request, f"Payroll for {employee.user.get_full_name()} - {month} {year} created successfully!")
                return redirect("payroll_detail", id=payroll.id)
    else:
        form = PayrollForm(startup=startup)
        form.fields["employee"].queryset = employees_list

    return render(request, "people/payroll_form.html", {
        "form": form,
        "employees": employees_list,
        "is_edit": False,
        "page_title": "Create Payroll",
        "page_icon": "💰",
    })


@login_required
def payroll_detail(request, id):
    """Payroll detail."""
    startup = get_startup(request)
    payroll = get_object_or_404(
        Payroll.objects.select_related("employee", "employee__user", "employee__department"),
        id=id,
        employee__startup=startup
    )

    return render(request, "people/payroll_detail.html", {"payroll": payroll})


@login_required
def payroll_update(request, id):
    """Update payroll."""
    startup = get_startup(request)
    payroll = get_object_or_404(Payroll, id=id, employee__startup=startup)

    if payroll.paid:
        messages.warning(request, "Paid payroll cannot be edited.")
        return redirect("payroll_detail", id=payroll.id)

    employees_list = Employee.objects.filter(startup=startup, is_active=True).select_related("user")

    if request.method == "POST":
        form = PayrollForm(request.POST, instance=payroll, startup=startup)
        form.fields["employee"].queryset = employees_list

        if form.is_valid():
            form.save()
            messages.success(request, "Payroll updated successfully.")
            return redirect("payroll_detail", id=payroll.id)
    else:
        form = PayrollForm(instance=payroll, startup=startup)
        form.fields["employee"].queryset = employees_list

    return render(request, "people/payroll_form.html", {
        "form": form,
        "employees": employees_list,
        "payroll": payroll,
        "is_edit": True,
        "page_title": "Update Payroll",
        "page_icon": "✏️",
    })


@login_required
def payroll_mark_paid(request, id):
    """Mark payroll as paid and auto-generate payslip."""
    startup = get_startup(request)
    payroll = get_object_or_404(Payroll, id=id, employee__startup=startup)

    if payroll.paid:
        messages.warning(request, "Payroll already marked as paid.")
    else:
        payroll.paid = True
        payroll.paid_date = timezone.now().date()
        payroll.save()
        messages.success(request, f"Payroll for {payroll.employee} - {payroll.month} {payroll.year} marked as paid!")

        # Auto-generate payslip
        try:
            payslip, created = Payslip.objects.get_or_create(payroll=payroll, defaults={'is_generated': False})
            if created or not payslip.is_generated:
                if generate_payslip_pdf(payslip):
                    messages.success(request, '✅ Payslip has been generated automatically!')
                else:
                    messages.warning(request, '⚠️ Payroll marked as paid but payslip generation failed.')
        except Exception as e:
            messages.error(request, f'❌ Error generating payslip: {str(e)}')

    return redirect("payroll_detail", id=payroll.id)


@login_required
def payroll_delete(request, id):
    """Delete payroll."""
    startup = get_startup(request)
    payroll = get_object_or_404(Payroll, id=id, employee__startup=startup)

    if payroll.paid:
        messages.warning(request, "Paid payroll cannot be deleted.")
        return redirect("payroll_detail", id=payroll.id)

    if request.method == "POST":
        employee_name = str(payroll.employee)
        month_year = f"{payroll.month} {payroll.year}"
        payroll.delete()
        messages.success(request, f"Payroll for {employee_name} - {month_year} deleted successfully.")
        return redirect("payroll")

    return render(request, "people/payroll_confirm_delete.html", {"payroll": payroll})


# ============================================================
# PAYSLIPS
# ============================================================

@login_required
def payslips(request):
    """Payslips list - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        payslips_list = Payslip.objects.select_related(
            'payroll', 'payroll__employee', 'payroll__employee__user'
        ).order_by('-generated_at')
        paid_payrolls = Payroll.objects.filter(paid=True).count()
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        payslips_list = Payslip.objects.select_related(
            'payroll', 'payroll__employee', 'payroll__employee__user'
        ).filter(
            payroll__employee__startup=startup
        ).order_by('-generated_at')
        paid_payrolls = Payroll.objects.filter(employee__startup=startup, paid=True).count()

    current_month = timezone.now().strftime('%B %Y')

    # Apply filters
    search = request.GET.get('search')
    month = request.GET.get('month')
    year = request.GET.get('year')

    if search:
        payslips_list = payslips_list.filter(
            Q(payroll__employee__user__first_name__icontains=search) |
            Q(payroll__employee__user__last_name__icontains=search) |
            Q(payroll__employee__employee_id__icontains=search)
        )
    if month:
        payslips_list = payslips_list.filter(payroll__month=month)
    if year:
        payslips_list = payslips_list.filter(payroll__year=year)

    context = {
        'payslips': payslips_list,
        'paid_payrolls': paid_payrolls,
        'current_month': current_month,
        'total_payslips': payslips_list.count(),
    }
    return render(request, 'people/payslips.html', context)


@login_required
def payslip_create(request):
    """Generate a new payslip."""
    startup = get_startup(request)

    if request.method == 'POST':
        form = PayslipForm(request.POST, request.FILES, startup=startup)
        if form.is_valid():
            payroll = form.cleaned_data['payroll']

            if Payslip.objects.filter(payroll=payroll).exists():
                messages.error(request, f'Payslip already exists for {payroll.employee} - {payroll.month} {payroll.year}.')
            else:
                payslip = form.save()
                messages.success(request, f'Payslip for {payroll.employee} - {payroll.month} {payroll.year} generated successfully!')
                return redirect('payslip_detail', id=payslip.id)
    else:
        form = PayslipForm(startup=startup)
        if Payroll.objects.filter(employee__startup=startup, paid=True).count() == 0:
            messages.warning(request, 'No paid payrolls found. Please mark payrolls as paid first.')

    context = {
        'form': form,
        'is_edit': False,
        'page_title': 'Generate Payslip',
        'page_icon': '📄'
    }
    return render(request, 'people/payslip_form.html', context)


@login_required
def payslip_detail(request, id):
    """View payslip details."""
    startup = get_startup(request)

    payslip = get_object_or_404(
        Payslip.objects.select_related(
            'payroll', 'payroll__employee', 'payroll__employee__user', 'payroll__employee__department'
        ),
        id=id,
        payroll__employee__startup=startup
    )

    context = {
        'payslip': payslip,
        'page_title': f'Payslip - {payslip.payroll.employee}',
        'page_icon': '📄'
    }
    return render(request, 'people/payslip_detail.html', context)


@login_required
def payslip_update(request, id):
    """Update payslip."""
    startup = get_startup(request)
    payslip = get_object_or_404(Payslip.objects.filter(payroll__employee__startup=startup), id=id)

    if request.method == 'POST':
        form = PayslipForm(request.POST, request.FILES, instance=payslip, startup=startup)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payslip updated successfully!')
            return redirect('payslip_detail', id=payslip.id)
    else:
        form = PayslipForm(instance=payslip, startup=startup)

    context = {
        'form': form,
        'payslip': payslip,
        'is_edit': True,
        'page_title': 'Update Payslip',
        'page_icon': '✏️'
    }
    return render(request, 'people/payslip_form.html', context)


@login_required
def payslip_delete(request, id):
    """Delete payslip."""
    startup = get_startup(request)
    payslip = get_object_or_404(Payslip.objects.filter(payroll__employee__startup=startup), id=id)

    if request.method == 'POST':
        employee_name = str(payslip.payroll.employee)
        month_year = f"{payslip.payroll.month} {payslip.payroll.year}"
        payslip.delete()
        messages.success(request, f'Payslip for {employee_name} - {month_year} deleted successfully.')
        return redirect('payslips')

    context = {
        'payslip': payslip,
        'page_title': 'Delete Payslip',
        'page_icon': '🗑️'
    }
    return render(request, 'people/payslip_confirm_delete.html', context)


# ============================================================
# PERFORMANCE REVIEWS
# ============================================================

@login_required
def performance(request):
    """View all performance reviews."""
    startup = get_startup(request)

    reviews = PerformanceReview.objects.select_related(
        'employee', 'employee__user', 'reviewer'
    ).filter(
        employee__startup=startup
    ).order_by('-created_at')

    filter_form = PerformanceFilterForm(request.GET, startup=startup)

    if filter_form.is_valid():
        employee = filter_form.cleaned_data.get('employee')
        rating = filter_form.cleaned_data.get('rating')
        review_period = filter_form.cleaned_data.get('review_period')
        from_date = filter_form.cleaned_data.get('from_date')
        to_date = filter_form.cleaned_data.get('to_date')

        if employee:
            reviews = reviews.filter(employee=employee)
        if rating:
            reviews = reviews.filter(rating=rating)
        if review_period:
            reviews = reviews.filter(review_period=review_period)
        if from_date:
            reviews = reviews.filter(created_at__date__gte=from_date)
        if to_date:
            reviews = reviews.filter(created_at__date__lte=to_date)

    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0

    context = {
        'reviews': reviews,
        'filter_form': filter_form,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'page_title': 'Performance Reviews',
        'page_icon': '⭐'
    }
    return render(request, 'people/performance.html', context)


@login_required
def performance_create(request):
    """Create a new performance review."""
    startup = get_startup(request)

    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST, startup=startup)
        if form.is_valid():
            review = form.save()
            messages.success(request, f'Performance review for {review.employee} created!')
            return redirect('performance_detail', id=review.id)
    else:
        form = PerformanceReviewForm(startup=startup)

    context = {
        'form': form,
        'is_edit': False,
        'page_title': 'Create Performance Review',
        'page_icon': '⭐'
    }
    return render(request, 'people/performance_form.html', context)


@login_required
def performance_detail(request, id):
    """View performance review details."""
    startup = get_startup(request)

    review = get_object_or_404(
        PerformanceReview.objects.select_related('employee', 'employee__user', 'reviewer'),
        id=id,
        employee__startup=startup
    )

    context = {
        'review': review,
        'page_title': f'Review - {review.employee}',
        'page_icon': '📄'
    }
    return render(request, 'people/performance_detail.html', context)


@login_required
def performance_update(request, id):
    """Update a performance review."""
    startup = get_startup(request)
    review = get_object_or_404(PerformanceReview.objects.filter(employee__startup=startup), id=id)

    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST, instance=review, startup=startup)
        if form.is_valid():
            form.save()
            messages.success(request, 'Performance review updated!')
            return redirect('performance_detail', id=review.id)
    else:
        form = PerformanceReviewForm(instance=review, startup=startup)

    context = {
        'form': form,
        'review': review,
        'is_edit': True,
        'page_title': 'Update Performance Review',
        'page_icon': '✏️'
    }
    return render(request, 'people/performance_form.html', context)


@login_required
def performance_delete(request, id):
    """Delete a performance review."""
    startup = get_startup(request)
    review = get_object_or_404(PerformanceReview.objects.filter(employee__startup=startup), id=id)

    if request.method == 'POST':
        employee_name = str(review.employee)
        review.delete()
        messages.success(request, f'Performance review for {employee_name} deleted!')
        return redirect('performance')

    context = {
        'review': review,
        'page_title': 'Delete Performance Review',
        'page_icon': '🗑️'
    }
    return render(request, 'people/performance_confirm_delete.html', context)


# ============================================================
# DOCUMENTS
# ============================================================

@login_required
def documents(request):
    """Employee documents list."""
    startup = get_startup(request)

    docs = EmployeeDocument.objects.select_related(
        "employee", "employee__user", "employee__department"
    ).filter(
        employee__startup=startup
    ).order_by("-uploaded_at")

    context = {
        "documents": docs,
        "total_documents": docs.count(),
        "employees_count": Employee.objects.filter(startup=startup).count(),
    }
    return render(request, "people/documents.html", context)


@login_required
def document_create(request):
    """Upload document."""
    startup = get_startup(request)

    if request.method == "POST":
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            if doc.employee.startup != startup:
                messages.error(request, "Invalid employee selected.")
                return redirect("documents")
            doc.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect("documents")
    else:
        form = EmployeeDocumentForm()
        form.fields["employee"].queryset = Employee.objects.filter(startup=startup)

    return render(request, "people/document_create.html", {"form": form})


@login_required
def document_detail(request, id):
    """Document detail."""
    startup = get_startup(request)
    document = get_object_or_404(EmployeeDocument, id=id, employee__startup=startup)

    return render(request, "people/document_detail.html", {"document": document})


@login_required
def document_update(request, id):
    """Update document."""
    startup = get_startup(request)
    document = get_object_or_404(EmployeeDocument, id=id, employee__startup=startup)

    if request.method == "POST":
        form = EmployeeDocumentForm(request.POST, request.FILES, instance=document)
        form.fields["employee"].queryset = Employee.objects.filter(startup=startup)

        if form.is_valid():
            form.save()
            messages.success(request, "Document updated successfully.")
            return redirect("document_detail", id=document.id)
    else:
        form = EmployeeDocumentForm(instance=document)
        form.fields["employee"].queryset = Employee.objects.filter(startup=startup)

    return render(request, "people/document_update.html", {"form": form, "document": document})


@login_required
def document_delete(request, id):
    """Delete document."""
    startup = get_startup(request)
    document = get_object_or_404(EmployeeDocument, id=id, employee__startup=startup)

    if request.method == "POST":
        document.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect("documents")

    return render(request, "people/document_delete.html", {"document": document})


# ============================================================
# ONBOARDING
# ============================================================

@login_required
def onboarding(request):
    """Employee Onboarding dashboard - Filtered by startup."""
    startup = request.user.startup

    if request.user.is_super_admin():
        employees_list = Employee.objects.select_related('user', 'department').order_by('-joining_date')
    else:
        if not startup:
            messages.error(request, 'No startup associated with your account.')
            return redirect('startup_profile_setup')
        employees_list = Employee.objects.filter(startup=startup).select_related('user', 'department').order_by('-joining_date')

    # Calculate statistics
    total_employees = employees_list.count()
    onboarding_count = employees_list.filter(status='onboarding').count()
    probation_count = employees_list.filter(status='probation').count()
    active_count = employees_list.filter(status='active').count()

    # Calculate onboarding progress for each employee
    for employee in employees_list:
        if employee.status == 'onboarding':
            employee.onboarding_progress = 30
        elif employee.status == 'probation':
            employee.onboarding_progress = 70
        elif employee.status == 'active':
            employee.onboarding_progress = 100
        else:
            employee.onboarding_progress = 0

        employee.completed_tasks = 0
        employee.total_tasks = 6

        if employee.onboarding_progress >= 100:
            employee.completed_tasks = 6
        elif employee.onboarding_progress >= 70:
            employee.completed_tasks = 4
        elif employee.onboarding_progress >= 30:
            employee.completed_tasks = 2

    total_tasks_completed = sum([emp.completed_tasks for emp in employees_list])
    total_tasks_possible = sum([emp.total_tasks for emp in employees_list])

    overall_progress = round((total_tasks_completed / total_tasks_possible) * 100) if total_tasks_possible > 0 else 0

    pending_tasks = total_tasks_possible - total_tasks_completed
    in_progress = employees_list.filter(status__in=['onboarding', 'probation']).count()

    departments_list = Department.objects.filter(startup=startup) if startup else Department.objects.all()

    context = {
        'employees': employees_list,
        'total_employees': total_employees,
        'onboarding_count': onboarding_count,
        'probation_count': probation_count,
        'active_count': active_count,
        'overall_progress': overall_progress,
        'pending_tasks': pending_tasks,
        'completed_tasks': total_tasks_completed,
        'in_progress': in_progress,
        'departments': departments_list,
    }
    return render(request, 'people/onboarding.html', context)


# ============================================================
# EXIT MANAGEMENT
# ============================================================

@login_required
def exit_management(request):
    """View all exit requests."""
    startup = get_startup(request)

    exit_requests = ExitRequest.objects.select_related(
        'employee', 'employee__user', 'approved_by'
    ).filter(
        employee__startup=startup
    ).order_by('-created_at')

    filter_form = ExitFilterForm(request.GET, startup=startup)

    if filter_form.is_valid():
        employee = filter_form.cleaned_data.get('employee')
        status = filter_form.cleaned_data.get('status')
        reason = filter_form.cleaned_data.get('reason')
        from_date = filter_form.cleaned_data.get('from_date')
        to_date = filter_form.cleaned_data.get('to_date')

        if employee:
            exit_requests = exit_requests.filter(employee=employee)
        if status:
            exit_requests = exit_requests.filter(status=status)
        if reason:
            exit_requests = exit_requests.filter(reason=reason)
        if from_date:
            exit_requests = exit_requests.filter(resignation_date__gte=from_date)
        if to_date:
            exit_requests = exit_requests.filter(resignation_date__lte=to_date)

    context = {
        'exit_requests': exit_requests,
        'filter_form': filter_form,
        'total_exits': exit_requests.count(),
        'pending_count': exit_requests.filter(status='Pending').count(),
        'approved_count': exit_requests.filter(status='Approved').count(),
        'completed_count': exit_requests.filter(status='Completed').count(),
        'rejected_count': exit_requests.filter(status='Rejected').count(),
    }
    return render(request, 'people/exit_management.html', context)


@login_required
def exit_create(request):
    """Create a new exit request."""
    startup = get_startup(request)

    if request.method == 'POST':
        form = ExitRequestForm(request.POST, startup=startup)
        if form.is_valid():
            exit_request = form.save()
            messages.success(request, f'Exit request for {exit_request.employee} created successfully!')
            return redirect('exit_detail', id=exit_request.id)
    else:
        form = ExitRequestForm(startup=startup)

    context = {
        'form': form,
        'is_edit': False,
        'page_title': 'Create Exit Request',
        'page_icon': '🚪'
    }
    return render(request, 'people/exit_form.html', context)


@login_required
def exit_detail(request, id):
    """View exit request details."""
    startup = get_startup(request)

    exit_request = get_object_or_404(
        ExitRequest.objects.select_related(
            'employee', 'employee__user', 'employee__department', 'approved_by'
        ),
        id=id,
        employee__startup=startup
    )

    context = {
        'exit_request': exit_request,
        'days_remaining': exit_request.get_days_remaining(),
        'notice_period': exit_request.get_notice_period_days(),
        'page_title': f'Exit - {exit_request.employee}',
        'page_icon': '📄'
    }
    return render(request, 'people/exit_detail.html', context)


@login_required
def exit_update(request, id):
    """Update exit request."""
    startup = get_startup(request)
    exit_request = get_object_or_404(ExitRequest.objects.filter(employee__startup=startup), id=id)

    if request.method == 'POST':
        form = ExitRequestForm(request.POST, instance=exit_request, startup=startup)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exit request updated successfully!')
            return redirect('exit_detail', id=exit_request.id)
    else:
        form = ExitRequestForm(instance=exit_request, startup=startup)

    context = {
        'form': form,
        'exit_request': exit_request,
        'is_edit': True,
        'page_title': 'Update Exit Request',
        'page_icon': '✏️'
    }
    return render(request, 'people/exit_form.html', context)


@login_required
def exit_approve(request, id):
    """Approve exit request."""
    startup = get_startup(request)
    exit_request = get_object_or_404(ExitRequest.objects.filter(employee__startup=startup), id=id)

    if exit_request.status != 'Pending':
        messages.warning(request, 'This request is already processed.')
        return redirect('exit_detail', id=exit_request.id)

    exit_request.status = 'Approved'
    exit_request.approved_by = request.user
    exit_request.approved_date = timezone.now().date()
    exit_request.save()

    # Update employee status
    employee = exit_request.employee
    employee.status = 'notice_period'
    employee.save()

    messages.success(request, f'Exit request for {exit_request.employee} approved!')
    return redirect('exit_detail', id=exit_request.id)


@login_required
def exit_reject(request, id):
    """Reject exit request."""
    startup = get_startup(request)
    exit_request = get_object_or_404(ExitRequest.objects.filter(employee__startup=startup), id=id)

    if exit_request.status != 'Pending':
        messages.warning(request, 'This request is already processed.')
        return redirect('exit_detail', id=exit_request.id)

    exit_request.status = 'Rejected'
    exit_request.approved_by = request.user
    exit_request.approved_date = timezone.now().date()
    exit_request.save()

    messages.success(request, f'Exit request for {exit_request.employee} rejected.')
    return redirect('exit_detail', id=exit_request.id)


@login_required
def exit_complete(request, id):
    """Mark exit as completed."""
    startup = get_startup(request)
    exit_request = get_object_or_404(ExitRequest.objects.filter(employee__startup=startup), id=id)

    if exit_request.status != 'Approved':
        messages.warning(request, 'Only approved exits can be completed.')
        return redirect('exit_detail', id=exit_request.id)

    exit_request.status = 'Completed'
    exit_request.save()

    # Update employee status
    employee = exit_request.employee
    employee.status = 'exited'
    employee.is_active = False
    employee.save()

    messages.success(request, f'Exit for {exit_request.employee} completed!')
    return redirect('exit_detail', id=exit_request.id)


@login_required
def exit_delete(request, id):
    """Delete exit request."""
    startup = get_startup(request)
    exit_request = get_object_or_404(ExitRequest.objects.filter(employee__startup=startup), id=id)

    if exit_request.status not in ['Pending', 'Rejected']:
        messages.warning(request, 'Only pending or rejected requests can be deleted.')
        return redirect('exit_detail', id=exit_request.id)

    if request.method == 'POST':
        employee_name = str(exit_request.employee)
        exit_request.delete()
        messages.success(request, f'Exit request for {employee_name} deleted.')
        return redirect('exit_management')

    context = {
        'exit_request': exit_request,
        'page_title': 'Delete Exit Request',
        'page_icon': '🗑️'
    }
    return render(request, 'people/exit_confirm_delete.html', context)


# ============================================================
# HOLIDAYS
# ============================================================

@login_required
def holidays(request):
    """View all holidays with filters."""
    startup = get_startup(request)

    holidays_list = Holiday.objects.all().order_by('date')

    filter_form = HolidayFilterForm(request.GET)

    if filter_form.is_valid():
        holiday_type = filter_form.cleaned_data.get('holiday_type')
        year = filter_form.cleaned_data.get('year')
        status = filter_form.cleaned_data.get('status')

        if holiday_type:
            holidays_list = holidays_list.filter(holiday_type=holiday_type)
        if year:
            holidays_list = holidays_list.filter(date__year=year)
        if status == 'upcoming':
            holidays_list = holidays_list.filter(date__gte=timezone.now().date())
        elif status == 'past':
            holidays_list = holidays_list.filter(date__lt=timezone.now().date())

    context = {
        'holidays': holidays_list,
        'filter_form': filter_form,
        'total_holidays': holidays_list.count(),
        'upcoming_holidays': holidays_list.filter(date__gte=timezone.now().date()).count(),
        'past_holidays': holidays_list.filter(date__lt=timezone.now().date()).count(),
        'current_year': timezone.now().year,
    }
    return render(request, 'people/holidays.html', context)


@login_required
def holiday_create(request):
    """Create a new holiday."""
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save()
            messages.success(request, f'Holiday "{holiday.name}" created successfully!')
            return redirect('holidays')
    else:
        form = HolidayForm()

    context = {
        'form': form,
        'is_edit': False,
        'page_title': 'Add Holiday',
        'page_icon': '🎉',
    }
    return render(request, 'people/holiday_form.html', context)


@login_required
def holiday_detail(request, id):
    """View holiday details."""
    holiday = get_object_or_404(Holiday, id=id)

    context = {
        'holiday': holiday,
        'page_title': f'Holiday - {holiday.name}',
        'page_icon': '📅'
    }
    return render(request, 'people/holiday_detail.html', context)


@login_required
def holiday_update(request, id):
    """Update a holiday."""
    holiday = get_object_or_404(Holiday, id=id)

    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, f'Holiday "{holiday.name}" updated successfully!')
            return redirect('holidays')
    else:
        form = HolidayForm(instance=holiday)

    context = {
        'form': form,
        'holiday': holiday,
        'is_edit': True,
        'page_title': 'Update Holiday',
        'page_icon': '✏️'
    }
    return render(request, 'people/holiday_form.html', context)


@login_required
def holiday_delete(request, id):
    """Delete a holiday."""
    holiday = get_object_or_404(Holiday, id=id)

    if request.method == 'POST':
        holiday_name = holiday.name
        holiday.delete()
        messages.success(request, f'Holiday "{holiday_name}" deleted successfully!')
        return redirect('holidays')

    context = {
        'holiday': holiday,
        'page_title': 'Delete Holiday',
        'page_icon': '🗑️'
    }
    return render(request, 'people/holiday_confirm_delete.html', context)


# ============================================================
# PAYSLIP PDF GENERATION & HELPERS
# ============================================================

@login_required
def payslip_download(request, id):
    """Download payslip PDF."""
    startup = get_startup(request)
    payslip = get_object_or_404(Payslip.objects.filter(payroll__employee__startup=startup), id=id)

    return redirect(payslip.pdf.url)


@login_required
def payslip_preview(request, id):
    """Preview payslip HTML before download."""
    startup = get_startup(request)
    payslip = get_object_or_404(Payslip, id=id, payroll__employee__startup=startup)

    if payslip.html_content:
        html_content = payslip.html_content
    else:
        payroll = payslip.payroll
        employee = payroll.employee
        context = {
            'payslip': payslip,
            'payroll': payroll,
            'employee': employee,
            'startup': startup,
            'company_name': startup.company_name,
            'generated_date': timezone.now().strftime('%d %B %Y'),
            'generated_time': timezone.now().strftime('%H:%M:%S'),
        }
        html_content = render_to_string('people/payslip_template.html', context)

    return HttpResponse(html_content)


@login_required
def payslip_regenerate(request, id):
    """Regenerate payslip PDF."""
    startup = get_startup(request)
    payslip = get_object_or_404(Payslip, id=id, payroll__employee__startup=startup)

    if payslip.pdf:
        try:
            old_path = os.path.join(settings.MEDIA_ROOT, payslip.pdf.name)
            if os.path.exists(old_path):
                os.remove(old_path)
        except:
            pass

    success = generate_payslip_pdf(payslip)

    if success:
        messages.success(request, '✅ Payslip regenerated successfully!')
    else:
        messages.error(request, '❌ Failed to regenerate payslip.')

    return redirect('payslip_detail', id=payslip.id)


@login_required
def payslip_download_pdf(request, id):
    """Download payslip PDF."""
    startup = get_startup(request)
    payslip = get_object_or_404(Payslip, id=id, payroll__employee__startup=startup)

    if payslip.pdf and payslip.is_generated:
        file_path = os.path.join(settings.MEDIA_ROOT, payslip.pdf.name)
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            filename = f"payslip_{payslip.payroll.employee.employee_id}_{payslip.payroll.month}_{payslip.payroll.year}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            success = generate_payslip_pdf(payslip)
            if success:
                response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
                filename = f"payslip_{payslip.payroll.employee.employee_id}_{payslip.payroll.month}_{payslip.payroll.year}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                messages.error(request, 'Failed to generate payslip. Please try again.')
                return redirect('payslip_detail', id=payslip.id)
    else:
        success = generate_payslip_pdf(payslip)
        if success:
            file_path = os.path.join(settings.MEDIA_ROOT, payslip.pdf.name)
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            filename = f"payslip_{payslip.payroll.employee.employee_id}_{payslip.payroll.month}_{payslip.payroll.year}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            messages.error(request, 'Failed to generate payslip. Please try again.')
            return redirect('payslip_detail', id=payslip.id)


@login_required
def payslip_bulk_generate(request):
    """Bulk generate payslips for all paid payrolls."""
    startup = get_startup(request)

    paid_payrolls = Payroll.objects.filter(
        employee__startup=startup,
        paid=True
    ).exclude(
        payslip__isnull=False
    )

    if request.method == 'POST':
        generated_count = 0
        failed_count = 0

        for payroll in paid_payrolls:
            try:
                payslip = Payslip.objects.create(
                    payroll=payroll,
                    is_generated=False
                )
                success = generate_payslip_pdf(payslip)
                if success:
                    generated_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1

        if generated_count > 0:
            messages.success(request, f'✅ {generated_count} payslips generated successfully!')
        if failed_count > 0:
            messages.warning(request, f'⚠️ {failed_count} payslips failed to generate.')

        return redirect('payslips')

    context = {
        'paid_payrolls': paid_payrolls,
        'total_count': paid_payrolls.count(),
        'page_title': 'Bulk Generate Payslips',
        'page_icon': '📄'
    }
    return render(request, 'people/payslip_bulk_generate.html', context)