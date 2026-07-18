from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import RegisterForm, StartupApplicationForm, UserApprovalForm
from .models import User
from startups.models import StartupProfile, StartupApplication


def startup_application_view(request):
    """Startup registration application view"""
    
    if request.method == "POST":
        form = StartupApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save()
            messages.success(
                request, 
                "✅ Your application has been submitted successfully! "
                "You will receive an email once it's reviewed by our team."
            )
            return redirect('accounts:application_success')
    else:
        form = StartupApplicationForm()
    
    return render(
        request,
        "accounts/startup_application.html",
        {
            "form": form,
            "page_title": "Apply to PANZIA",
            "page_icon": "🚀",
        }
    )


def application_success(request):
    """Application success page"""
    return render(
        request,
        "accounts/application_success.html",
        {
            "page_title": "Application Submitted",
            "page_icon": "✅",
        }
    )


def register_view(request):
    """User registration view (for invited users)"""
    
    # Check if user is already logged in
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # If user selected a startup, assign it
            startup_id = request.POST.get('startup')
            if startup_id:
                try:
                    startup = StartupProfile.objects.get(id=startup_id)
                    user.startup = startup
                except StartupProfile.DoesNotExist:
                    pass
            
            # Users registered through invitation are pre-approved
            user.is_approved = True
            user.save()
            login(request, user)
            
            # Redirect based on role
            if user.is_superuser or user.role == 'super_admin':
                return redirect("admin_dashboard")
            elif user.role in ['startup_admin', 'startup_hr', 'startup_manager']:
                return redirect("people_dashboard")
            elif user.role == 'employee':
                return redirect("employee_portal_dashboard")
            else:
                return redirect("home")
    else:
        form = RegisterForm()
    
    # Get startups for dropdown
    startups = StartupProfile.objects.filter(is_active=True)
    
    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
            "startups": startups,
            "page_title": "Create Account",
            "page_icon": "👤",
        }
    )


def login_view(request):
    """User login view"""
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(
            request,
            username=username,
            password=password
        )
        
        if user is not None:
            # Check if user is approved
            if not user.is_approved and user.role != 'super_admin':
                messages.warning(
                    request,
                    "⏳ Your account is pending approval. Please wait for admin to approve your account."
                )
                return render(request, "accounts/login.html")
            
            login(request, user)
            
            # Redirect based on role
            if user.is_superuser or user.role == 'super_admin':
                return redirect("admin_dashboard")
            elif user.role in ['startup_admin', 'startup_hr', 'startup_manager']:
                return redirect("people_dashboard")
            elif user.role == 'employee':
                return redirect("employee_portal_dashboard")
            else:
                return redirect("home")
        else:
            messages.error(
                request,
                "❌ Invalid username or password"
            )
    
    return render(request, "accounts/login.html")


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def onboarding(request):
    """Onboarding page after registration"""
    
    # Get the role from URL or session
    role = request.GET.get('role', 'startup_owner')
    
    # If user already completed onboarding, redirect to dashboard
    if request.user.is_authenticated and hasattr(request.user, 'profile_completed'):
        return redirect('dashboard')
    
    context = {
        'role': role,
        'page_title': 'Onboarding - PANZIA',
        'page_icon': '🚀',
    }
    return render(request, 'accounts/onboarding.html', context)


# ============================================
# ADMIN: MANAGE APPLICATIONS
# ============================================

@login_required
def admin_applications(request):
    """Admin view for managing startup applications"""
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    pending = StartupApplication.objects.filter(status='pending')
    approved = StartupApplication.objects.filter(status='approved')
    rejected = StartupApplication.objects.filter(status='rejected')
    
    context = {
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'page_title': 'Manage Applications',
        'page_icon': '📋',
    }
    
    return render(request, 'accounts/admin/applications.html', context)


@login_required
def admin_application_detail(request, app_id):
    """Admin view for application details"""
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    application = get_object_or_404(StartupApplication, id=app_id)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'approve':
            try:
                user, startup = application.approve(request.user)
                messages.success(
                    request, 
                    f"✅ Application approved! User {user.email} created with startup {startup.company_name}."
                )
                return redirect('accounts:admin_applications')
            except Exception as e:
                messages.error(request, f"Error approving application: {str(e)}")
        
        elif action == 'reject':
            reason = request.POST.get('rejection_reason')
            application.reject(request.user, reason)
            messages.success(request, "Application rejected successfully.")
            return redirect('accounts:admin_applications')
    
    context = {
        'application': application,
        'page_title': f'Application: {application.company_name}',
        'page_icon': '📄',
    }
    
    return render(request, 'accounts/admin/application_detail.html', context)


@login_required
def admin_pending_users(request):
    """Admin view for managing pending users"""
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    pending_users = User.objects.filter(is_approved=False, role='pending')
    
    context = {
        'pending_users': pending_users,
        'page_title': 'Pending Users',
        'page_icon': '👥',
    }
    
    return render(request, 'accounts/admin/pending_users.html', context)


@login_required
def admin_approve_user(request, user_id):
    """Admin view for approving a user"""
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id, is_approved=False)
    
    if request.method == "POST":
        form = UserApprovalForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.approve(request.user, role)
            messages.success(request, f"✅ User {user.email} approved successfully!")
            return redirect('accounts:admin_pending_users')
    else:
        form = UserApprovalForm()
    
    context = {
        'form': form,
        'pending_user': user,
        'page_title': f'Approve User: {user.email}',
        'page_icon': '✅',
    }
    
    return render(request, 'accounts/admin/approve_user.html', context)


@login_required
def admin_reject_user(request, user_id):
    """Admin view for rejecting a user"""
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id, is_approved=False)
    
    if request.method == "POST":
        reason = request.POST.get('rejection_reason')
        user.reject(reason)
        messages.success(request, f"User {user.email} rejected.")
        return redirect('accounts:admin_pending_users')
    
    context = {
        'user': user,
        'page_title': f'Reject User: {user.email}',
        'page_icon': '❌',
    }
    
    return render(request, 'accounts/admin/reject_user.html', context)