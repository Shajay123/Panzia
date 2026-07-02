from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import StartupProfile
from .forms import StartupProfileForm
from sprints.models import Sprint, SprintMember


@login_required
def startup_profile_setup(request):
    # ==================================
    # GET OR CREATE PROFILE - FIXED
    # ==================================
    
    profile = None
    
    # Check if user already has a profile via OneToOne
    if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
        profile = request.user.startup_profile
    # Check if user has a profile via ForeignKey
    elif request.user.startup:
        profile = request.user.startup
    # Try to get from database
    else:
        try:
            profile = StartupProfile.objects.get(user=request.user)
        except StartupProfile.DoesNotExist:
            profile = None

    if request.method == 'POST':
        if profile:
            form = StartupProfileForm(request.POST, request.FILES, instance=profile)
        else:
            form = StartupProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            startup_profile = form.save(commit=False)
            startup_profile.user = request.user
            startup_profile.save()
            
            # CRITICAL: Also update the user's startup field (ForeignKey) for consistency
            # This ensures both relationships point to the same profile
            request.user.startup = startup_profile
            request.user.save()
            
            messages.success(request, f'Startup profile for "{startup_profile.company_name}" saved successfully!')
            return redirect('startup_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(form.errors)
    else:
        if profile:
            form = StartupProfileForm(instance=profile)
        else:
            form = StartupProfileForm()

    return render(request, 'startups/profile_setup.html', {'form': form})


def startup_profile(request, startup_id):
    startup = get_object_or_404(StartupProfile, id=startup_id)

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