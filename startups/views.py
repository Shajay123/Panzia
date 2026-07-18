# startups/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import StartupProfile, StartupApplication
from .forms import StartupProfileForm, StartupApplicationForm
from sprints.models import Sprint, SprintMember

# Set up logging
logger = logging.getLogger(__name__)


# ============================================
# ADMIN APPLICATION MANAGEMENT
# ============================================

@login_required
def admin_applications(request):
    """Admin view for managing startup applications"""
    
    print("🔍 [DEBUG] admin_applications view called")
    print(f"👤 [DEBUG] User: {request.user.username} (Role: {request.user.role})")
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        print("❌ [DEBUG] Access denied - not super admin")
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    applications = StartupApplication.objects.all().order_by('-created_at')
    
    pending_count = applications.filter(status='pending').count()
    approved_count = applications.filter(status='approved').count()
    rejected_count = applications.filter(status='rejected').count()
    total_count = applications.count()
    
    print(f"📊 [DEBUG] Applications stats: Total={total_count}, Pending={pending_count}, Approved={approved_count}, Rejected={rejected_count}")
    
    context = {
        'applications': applications,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': total_count,
        'page_title': 'Startup Applications',
        'page_icon': '📋',
    }
    
    return render(request, 'startups/admin/applications.html', context)


@login_required
def admin_application_detail(request, app_id):
    """Admin view for application details"""
    
    print(f"🔍 [DEBUG] admin_application_detail called for app_id: {app_id}")
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        print("❌ [DEBUG] Access denied - not super admin")
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    application = get_object_or_404(StartupApplication, id=app_id)
    print(f"📄 [DEBUG] Application: {application.company_name} - Status: {application.status}")
    
    context = {
        'application': application,
        'page_title': f'Application: {application.company_name}',
        'page_icon': '📄',
    }
    
    return render(request, 'startups/admin/application_detail.html', context)


@login_required
def admin_approve_application(request, app_id):
    """Approve a startup application from admin"""
    
    print(f"✅ [DEBUG] admin_approve_application called for app_id: {app_id}")
    print(f"👤 [DEBUG] Admin user: {request.user.username}")
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        print("❌ [DEBUG] Access denied - not super admin")
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home')
    
    application = get_object_or_404(StartupApplication, id=app_id, status='pending')
    print(f"📄 [DEBUG] Application: {application.company_name} - Applicant: {application.applicant_email}")
    
    try:
        print("🔄 [DEBUG] Calling application.approve()...")
        user, startup = application.approve(request.user)
        print(f"✅ [DEBUG] Approval successful!")
        print(f"👤 [DEBUG] User created: {user.email} (ID: {user.id})")
        print(f"🏢 [DEBUG] Startup created: {startup.company_name} (ID: {startup.id})")
        
        messages.success(
            request, 
            f"✅ Application approved! User '{user.email}' created with startup '{startup.company_name}'."
        )
        print(f"📧 [DEBUG] Approval email should have been sent to: {user.email}")
        
    except Exception as e:
        print(f"❌ [DEBUG] Approval failed with error: {str(e)}")
        import traceback
        print(f"📋 [DEBUG] Full traceback:\n{traceback.format_exc()}")
        messages.error(request, f"Error approving application: {str(e)}")
    
    return redirect('startups:admin_applications')


@login_required
def admin_reject_application(request, app_id):
    """Reject a startup application from admin"""
    
    print(f"❌ [DEBUG] admin_reject_application called for app_id: {app_id}")
    print(f"👤 [DEBUG] Admin user: {request.user.username}")
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        print("❌ [DEBUG] Access denied - not super admin")
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home')
    
    application = get_object_or_404(StartupApplication, id=app_id, status='pending')
    print(f"📄 [DEBUG] Application: {application.company_name} - Applicant: {application.applicant_email}")
    
    if request.method == 'POST':
        reason = request.POST.get('rejection_reason', 'Rejected by admin')
        print(f"📝 [DEBUG] Rejection reason: {reason}")
        
        try:
            print("🔄 [DEBUG] Calling application.reject()...")
            application.reject(request.user, reason)
            print(f"✅ [DEBUG] Rejection successful!")
            messages.success(request, f"Application for '{application.company_name}' rejected.")
        except Exception as e:
            print(f"❌ [DEBUG] Rejection failed with error: {str(e)}")
            import traceback
            print(f"📋 [DEBUG] Full traceback:\n{traceback.format_exc()}")
            messages.error(request, f"Error rejecting application: {str(e)}")
        
        return redirect('startups:admin_applications')
    
    print("⚠️ [DEBUG] GET request to reject - redirecting back")
    return redirect('startups:admin_applications')


# ============================================
# STARTUP PROFILE MANAGEMENT
# ============================================

@login_required
def startup_profile_setup(request):
    """Create or update startup profile"""
    
    print(f"🔍 [DEBUG] startup_profile_setup called by user: {request.user.username}")
    
    profile = None
    
    # Check if user already has a profile via OneToOne
    if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
        profile = request.user.startup_profile
        print(f"📄 [DEBUG] Found profile via OneToOne: {profile.company_name}")
    # Check if user has a profile via ForeignKey
    elif request.user.startup:
        profile = request.user.startup
        print(f"📄 [DEBUG] Found profile via ForeignKey: {profile.company_name}")
    # Try to get from database
    else:
        try:
            profile = StartupProfile.objects.get(user=request.user)
            print(f"📄 [DEBUG] Found profile via database query: {profile.company_name}")
        except StartupProfile.DoesNotExist:
            profile = None
            print("📄 [DEBUG] No existing profile found")

    if request.method == 'POST':
        print("📤 [DEBUG] Processing POST request")
        
        if profile:
            form = StartupProfileForm(request.POST, request.FILES, instance=profile)
            print(f"📝 [DEBUG] Updating existing profile")
        else:
            form = StartupProfileForm(request.POST, request.FILES)
            print(f"📝 [DEBUG] Creating new profile")
        
        if form.is_valid():
            print("✅ [DEBUG] Form is valid")
            startup_profile = form.save(commit=False)
            startup_profile.user = request.user
            startup_profile.save()
            
            # Also update the user's startup field (ForeignKey) for consistency
            request.user.startup = startup_profile
            request.user.save()
            
            print(f"✅ [DEBUG] Profile saved: {startup_profile.company_name} (ID: {startup_profile.id})")
            messages.success(request, f'Startup profile for "{startup_profile.company_name}" saved successfully!')
            return redirect('startup_dashboard')
        else:
            print("❌ [DEBUG] Form is invalid")
            print(f"📋 [DEBUG] Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        print("📖 [DEBUG] Processing GET request")
        if profile:
            form = StartupProfileForm(instance=profile)
        else:
            form = StartupProfileForm()

    return render(request, 'startups/profile_setup.html', {'form': form})


@login_required
def startup_profile_view(request):
    """View the current user's startup profile"""
    
    print(f"🔍 [DEBUG] startup_profile_view called by user: {request.user.username}")
    
    try:
        startup = StartupProfile.objects.get(user=request.user)
        print(f"📄 [DEBUG] Found startup: {startup.company_name}")
    except StartupProfile.DoesNotExist:
        print("❌ [DEBUG] No startup profile found")
        messages.warning(request, 'Please set up your startup profile first.')
        return redirect('startup_profile_setup')
    
    active_sprints = Sprint.objects.filter(startup=startup, status='active')
    completed_sprints = Sprint.objects.filter(startup=startup, status='completed')
    contributors = SprintMember.objects.filter(sprint__startup=startup).count()
    
    print(f"📊 [DEBUG] Sprint stats: Active={active_sprints.count()}, Completed={completed_sprints.count()}, Contributors={contributors}")

    context = {
        'startup': startup,
        'active_sprints': active_sprints,
        'completed_sprints': completed_sprints,
        'active_count': active_sprints.count(),
        'completed_count': completed_sprints.count(),
        'contributors': contributors,
    }

    return render(request, 'startups/profile.html', context)


def startup_profile_detail(request, startup_id):
    """View a specific startup profile by ID"""
    
    print(f"🔍 [DEBUG] startup_profile_detail called for startup_id: {startup_id}")
    
    startup = get_object_or_404(StartupProfile, id=startup_id)
    print(f"📄 [DEBUG] Startup: {startup.company_name}")

    active_sprints = Sprint.objects.filter(startup=startup, status='active')
    completed_sprints = Sprint.objects.filter(startup=startup, status='completed')
    contributors = SprintMember.objects.filter(sprint__startup=startup).count()

    context = {
        'startup': startup,
        'active_sprints': active_sprints,
        'completed_sprints': completed_sprints,
        'active_count': active_sprints.count(),
        'completed_count': completed_sprints.count(),
        'contributors': contributors,
    }

    return render(request, 'startups/profile.html', context)


# ============================================
# STARTUP APPLICATION (PUBLIC)
# ============================================

def startup_application_create(request):
    """Public view for startup owners to apply"""
    
    print("🔍 [DEBUG] startup_application_create called")
    
    if request.method == 'POST':
        print("📤 [DEBUG] Processing POST request")
        form = StartupApplicationForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("✅ [DEBUG] Form is valid")
            application = form.save()
            print(f"✅ [DEBUG] Application saved: {application.company_name} (ID: {application.id})")
            print(f"📧 [DEBUG] Applicant email: {application.applicant_email}")
            
            messages.success(
                request, 
                "✅ Your application has been submitted successfully! "
                "You will receive an email once it's reviewed by our team."
            )
            return redirect('startups:application_success')
        else:
            print("❌ [DEBUG] Form is invalid")
            print(f"📋 [DEBUG] Form errors: {form.errors}")
    else:
        print("📖 [DEBUG] Processing GET request")
        form = StartupApplicationForm()
    
    return render(
        request,
        'startups/application_form.html',
        {
            'form': form,
            'page_title': 'Apply to PANZIA',
            'page_icon': '🚀',
        }
    )


def application_success(request):
    """Application success page"""
    
    print("✅ [DEBUG] application_success page rendered")
    
    return render(
        request,
        'startups/application_success.html',
        {
            'page_title': 'Application Submitted',
            'page_icon': '✅',
        }
    )


# ============================================
# EMAIL TEST VIEW
# ============================================

@login_required
def test_email(request):
    """Test email configuration"""
    
    print("📧 [DEBUG] test_email view called")
    print(f"👤 [DEBUG] User: {request.user.username} (Role: {request.user.role})")
    
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        print("❌ [DEBUG] Access denied - not super admin")
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', request.user.email)
        print(f"📤 [DEBUG] Sending test email to: {email}")
        
        try:
            print("🔄 [DEBUG] Attempting to send email...")
            print(f"📧 [DEBUG] From: {settings.DEFAULT_FROM_EMAIL}")
            print(f"📧 [DEBUG] To: {email}")
            
            send_mail(
                subject='Test Email from PANZIA',
                message=f"""
Hello,

This is a test email from PANZIA.

Your email configuration is working correctly!

Best regards,
PANZIA Team

--- Debug Info ---
From: {settings.DEFAULT_FROM_EMAIL}
To: {email}
Host: {settings.EMAIL_HOST}
Port: {settings.EMAIL_PORT}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            print("✅ [DEBUG] Email sent successfully!")
            messages.success(request, f"✅ Test email sent successfully to {email}!")
            
        except Exception as e:
            print(f"❌ [DEBUG] Email failed with error: {str(e)}")
            import traceback
            print(f"📋 [DEBUG] Full traceback:\n{traceback.format_exc()}")
            messages.error(request, f"❌ Email failed: {str(e)}")
    else:
        print("📖 [DEBUG] Processing GET request - showing form")
    
    # Print email configuration (for debugging)
    print("📧 [DEBUG] Email Configuration:")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    return render(request, 'startups/test_email.html', {
        'page_title': 'Test Email',
        'page_icon': '📧',
    })