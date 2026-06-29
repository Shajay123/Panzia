from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import StartupProfile
from .forms import StartupProfileForm


@login_required
def startup_profile_setup(request):

    profile, created = StartupProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        form = StartupProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            print("PROFILE SAVED")

            print(profile.logo)

            return redirect('startup_dashboard')

        else:

            print(form.errors)

    else:

        form = StartupProfileForm(
            instance=profile
        )

    return render(
        request,
        'startups/profile_setup.html',
        {
            'form': form
        }
    )


from django.shortcuts import render, get_object_or_404

from .models import StartupProfile
from sprints.models import Sprint, SprintMember


def startup_profile(request, startup_id):

    

    startup = get_object_or_404(
        StartupProfile,
        id=startup_id
    )

    active_sprints = Sprint.objects.filter(
        startup=startup,
        status='active'
    )

    completed_sprints = Sprint.objects.filter(
        startup=startup,
        status='completed'
    )

    contributors = SprintMember.objects.filter(
        sprint__startup=startup
    ).count()

    context = {

        'startup': startup,

        'active_sprints': active_sprints,

        'completed_sprints': completed_sprints,

        'active_count': active_sprints.count(),

        'completed_count': completed_sprints.count(),

        'contributors': contributors,

        'startup_profile': startup_profile,

    }

    return render(
        request,
        'startups/profile.html',
        context
    )