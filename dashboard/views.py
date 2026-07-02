from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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


@login_required
def dashboard_home(request):
    if request.user.role == 'startup_admin' or request.user.role == 'startup_hr' or request.user.role == 'startup_manager':
        return redirect('startup_dashboard')
    elif request.user.role == 'employee':
        return redirect('employee_portal_dashboard')
    elif request.user.role == 'talent':
        return redirect('talent_dashboard')
    else:
        # Super admin or unknown role
        return redirect('startup_dashboard')


@login_required
def startup_dashboard(request):
    # ==================================
    # GET STARTUP PROFILE - FIXED
    # ==================================
    
    startup_profile = None
    
    # Method 1: Check OneToOne relationship (user.startup_profile)
    if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
        startup_profile = request.user.startup_profile
    # Method 2: Check ForeignKey relationship (user.startup)
    elif request.user.startup:
        startup_profile = request.user.startup
    # Method 3: Try to get from database using user
    else:
        try:
            startup_profile = StartupProfile.objects.get(user=request.user)
        except StartupProfile.DoesNotExist:
            pass
    
    # If still no startup profile found, redirect to setup
    if not startup_profile:
        messages.warning(request, 'Please complete your startup profile setup first.')
        return redirect('startup_profile_setup')

    # ==================================
    # CURRENT PLAN
    # ==================================
    
    current_plan = get_plan(request.user)

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

    # ==================================
    # SPRINT STATS
    # ==================================

    total_sprints = Sprint.objects.filter(startup=startup_profile).count()
    active_sprints = Sprint.objects.filter(startup=startup_profile, status='active').count()
    completed_sprints = Sprint.objects.filter(startup=startup_profile, status='completed').count()
    open_sprints = Sprint.objects.filter(startup=startup_profile, status='open').count()

    # ==================================
    # MEMBERS & APPLICATIONS
    # ==================================

    contributors = SprintMember.objects.filter(sprint__startup=startup_profile).count()
    applications = SprintApplication.objects.filter(sprint__startup=startup_profile).count()
    accepted_members = SprintApplication.objects.filter(sprint__startup=startup_profile, status='accepted').count()

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
    completed_tasks = Task.objects.filter(sprint__startup=startup_profile, status='completed').count()

    # ==================================
    # ACTIVITIES
    # ==================================

    activities = Activity.objects.filter(user=request.user).order_by('-created_at')[:8]

    # ==================================
    # CONTEXT
    # ==================================

    context = {
        'startup_profile': startup_profile,
        'user_startup': startup_profile,  # For template compatibility
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
        'completed_tasks': completed_tasks,
        'current_plan': current_plan,
    }

    return render(request, 'dashboard/startup_dashboard.html', context)


@login_required
def talent_dashboard(request):
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
    }

    return render(request, 'dashboard/talent_dashboard.html', context)