from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm
from startups.models import StartupProfile


# accounts/views.py - Updated registration view

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm
from startups.models import StartupProfile


def register_view(request):
    """User registration view with startup assignment"""
    
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
            "startups": startups
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
                "Invalid username or password"
            )
    
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect('home')


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
    }
    return render(request, 'accounts/onboarding.html', context)