from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from payments.subscription_checker import get_plan
from startups.models import StartupProfile
from sprints.models import (
    Sprint,
    SprintMember,
    SprintApplication,
    Task,
    Activity
)
from reputation.models import ReputationScore
from people.models import Employee, Attendance, LeaveRequest, Payroll


@login_required
def dashboard_home(request):
    """Redirect to appropriate dashboard based on user role"""
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    role = request.user.role.lower() if request.user.role else ''
    
    print(f"🔄 [DEBUG] dashboard_home called for user: {request.user.username}")
    print(f"👤 [DEBUG] Role: {role}")
    print(f"🏢 [DEBUG] Has startup: {bool(request.user.startup)}")
    
    # Super admin redirect to admin applications
    if request.user.is_superuser or role == 'super_admin':
        print("📋 [DEBUG] Redirecting to admin applications")
        return redirect('startups:admin_applications')
    elif role in ['startup_admin', 'startup_hr', 'startup_manager']:
        print("🏢 [DEBUG] Redirecting to startup dashboard")
        return redirect('startup_dashboard')
    elif role == 'employee':
        print("👤 [DEBUG] Redirecting to employee dashboard")
        return redirect('employee_dashboard')
    elif role == 'talent':
        print("🌟 [DEBUG] Redirecting to talent dashboard")
        return redirect('talent_dashboard')
    else:
        print("❓ [DEBUG] Unknown role, redirecting to startup dashboard")
        return redirect('startup_dashboard')


@login_required
def startup_dashboard(request):
    """Startup dashboard for startup users"""
    
    print(f"🚀 [DEBUG] startup_dashboard called for user: {request.user.username}")
    print(f"👤 [DEBUG] User role: {request.user.role}")
    
    # Super admin should not access this page
    if request.user.is_superuser or request.user.role == 'super_admin':
        print("👑 [DEBUG] Super admin accessing startup dashboard - redirecting")
        return redirect('startups:admin_applications')
    
    # ==================================
    # GET STARTUP PROFILE
    # ==================================
    
    startup_profile = None
    
    # Method 1: Check OneToOne relationship (user.startup_profile)
    if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
        startup_profile = request.user.startup_profile
        print(f"✅ [DEBUG] Found startup via OneToOne: {startup_profile.company_name}")
    # Method 2: Check ForeignKey relationship (user.startup)
    elif request.user.startup:
        startup_profile = request.user.startup
        print(f"✅ [DEBUG] Found startup via ForeignKey: {startup_profile.company_name}")
    # Method 3: Try to get from database using user
    else:
        try:
            startup_profile = StartupProfile.objects.get(user=request.user)
            print(f"✅ [DEBUG] Found startup via database query: {startup_profile.company_name}")
        except StartupProfile.DoesNotExist:
            print("❌ [DEBUG] No startup profile found")
            pass
    
    # If still no startup profile found, redirect to setup
    if not startup_profile:
        print("⚠️ [DEBUG] No startup profile - redirecting to setup")
        messages.warning(request, 'Please complete your startup profile setup first.')
        return redirect('startups:startup_profile_setup')

    # ==================================
    # CURRENT PLAN
    # ==================================
    
    current_plan = get_plan(request.user)
    print(f"💎 [DEBUG] Current plan: {current_plan}")

    # ==================================
    # PROFILE COMPLETION
    # ==================================

    fields = [
        startup_profile.company_name,
        startup_profile.tagline,
        startup_profile.industry,
        startup_profile.description,
        startup_profile.website,
        startup_profile.logo
    ]

    completed = sum(1 for field in fields if field)
    profile_completion = round((completed / len(fields)) * 100) if fields else 0
    print(f"📊 [DEBUG] Profile completion: {profile_completion}%")

    # ==================================
    # SPRINT STATS
    # ==================================

    total_sprints = Sprint.objects.filter(startup=startup_profile).count()
    active_sprints = Sprint.objects.filter(startup=startup_profile, status='active').count()
    completed_sprints = Sprint.objects.filter(startup=startup_profile, status='completed').count()
    open_sprints = Sprint.objects.filter(startup=startup_profile, status='open').count()
    
    print(f"📊 [DEBUG] Sprint stats: Total={total_sprints}, Active={active_sprints}, Completed={completed_sprints}, Open={open_sprints}")

    # ==================================
    # MEMBERS & APPLICATIONS
    # ==================================

    contributors = SprintMember.objects.filter(sprint__startup=startup_profile).count()
    applications = SprintApplication.objects.filter(sprint__startup=startup_profile).count()
    accepted_members = SprintApplication.objects.filter(
        sprint__startup=startup_profile, 
        status='accepted'
    ).count()
    
    print(f"👥 [DEBUG] Contributors: {contributors}, Applications: {applications}, Accepted: {accepted_members}")

    # ==================================
    # COMPLETION RATE
    # ==================================

    completion_rate = round((completed_sprints / total_sprints) * 100) if total_sprints > 0 else 0

    # ==================================
    # RECENT SPRINTS
    # ==================================

    recent_sprints = Sprint.objects.filter(startup=startup_profile).order_by('-created_at')[:5]

    # ==================================
    # TASKS
    # ==================================

    total_tasks = Task.objects.filter(sprint__startup=startup_profile).count()
    active_tasks = Task.objects.filter(
        sprint__startup=startup_profile, 
        status='in_progress'
    ).count()
    completed_tasks = Task.objects.filter(
        sprint__startup=startup_profile, 
        status='completed'
    ).count()

    # ==================================
    # ACTIVITIES
    # ==================================

    activities = Activity.objects.filter(user=request.user).order_by('-created_at')[:8]

    # ==================================
    # CONTEXT
    # ==================================

    context = {
        'startup_profile': startup_profile,
        'user_startup': startup_profile,
        'profile_completion': profile_completion,
        'total_sprints': total_sprints,
        'active_sprints': active_sprints,
        'completed_sprints': completed_sprints,
        'open_sprints': open_sprints,
        'contributors': contributors,
        'applications': applications,
        'accepted_members': accepted_members,
        'completion_rate': completion_rate,
        'recent_sprints': recent_sprints,
        'activities': activities,
        'total_tasks': total_tasks,
        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,
        'current_plan': current_plan,
        'startup_id': startup_profile.id,
    }

    print("✅ [DEBUG] Rendering startup dashboard")
    return render(request, 'dashboard/startup_dashboard.html', context)


@login_required
def talent_dashboard(request):
    """Talent dashboard"""
    
    print(f"🌟 [DEBUG] talent_dashboard called for user: {request.user.username}")
    
    applications = SprintApplication.objects.filter(talent=request.user).count()
    joined_sprints = SprintMember.objects.filter(user=request.user).count()
    tasks = Task.objects.filter(assigned_to=request.user).count()
    reputation, created = ReputationScore.objects.get_or_create(user=request.user)
    current_plan = get_plan(request.user)

    context = {
        'applications': applications,
        'joined_sprints': joined_sprints,
        'tasks': tasks,
        'reputation': reputation,
        'current_plan': current_plan,
        'page_title': 'Talent Dashboard',
        'page_icon': '🌟',
    }

    return render(request, 'dashboard/talent_dashboard.html', context)


@login_required
def employee_portal_dashboard(request):
    """Employee portal dashboard"""
    
    print(f"👤 [DEBUG] employee_portal_dashboard called for user: {request.user.username}")
    
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.warning(request, 'Employee profile not found.')
        return redirect('home')
    
    # Today
    today = timezone.now().date()
    attendance_today = Attendance.objects.filter(employee=employee, date=today).first()
    
    # This week's attendance (Monday to Sunday)
    week_start = today - timedelta(days=today.weekday())
    
    # Get all days of the week with attendance status
    week_attendance = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        attendance = Attendance.objects.filter(employee=employee, date=day_date).first()
        week_attendance.append({
            'date': day_date,
            'status': attendance.status if attendance else None,
            'is_today': day_date == today
        })
    
    # Calculate weekly stats
    present_days = sum(1 for day in week_attendance if day['status'] == 'present')
    absent_days = sum(1 for day in week_attendance if day['status'] == 'absent')
    leave_days = sum(1 for day in week_attendance if day['status'] == 'on_leave')
    wfh_days = sum(1 for day in week_attendance if day['status'] == 'wfh')
    
    # Recent leaves (last 5)
    recent_leaves = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:5]
    
    # Leave counts
    pending_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Pending'
    ).count()
    
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Approved'
    ).count()
    
    # Latest payroll
    latest_payroll = Payroll.objects.filter(
        employee=employee
    ).order_by('-created_at').first()
    
    context = {
        'employee': employee,
        'attendance_today': attendance_today,
        'present_days': present_days,
        'absent_days': absent_days,
        'leave_days': leave_days,
        'wfh_days': wfh_days,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'latest_payroll': latest_payroll,
        'week_attendance': week_attendance,
        'recent_leaves': recent_leaves,
        'today': today,
        'page_title': 'Employee Dashboard',
        'page_icon': '👤',
    }
    
    return render(request, 'dashboard/employee_dashboard.html', context)