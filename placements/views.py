from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from startups.models import StartupProfile

from .forms import PlacementJobForm


@login_required
def create_job(request):

    startup = StartupProfile.objects.get(
        user=request.user
    )

    if request.method == "POST":

        form = PlacementJobForm(request.POST)

        if form.is_valid():

            job = form.save(commit=False)

            job.startup = startup

            job.save()

            return redirect("startup_jobs")

        else:
            print(form.errors)

    else:

        form = PlacementJobForm()

    return render(
        request,
        "placements/create_job.html",
        {
            "form": form
        }
    )


from .models import PlacementJob


@login_required
def startup_jobs(request):

    startup = StartupProfile.objects.get(
        user=request.user
    )

    jobs = PlacementJob.objects.filter(
        startup=startup
    )

    return render(
        request,
        "placements/startup_jobs.html",
        {
            "jobs": jobs
        }
    )


from .models import PlacementApplication

@login_required
def browse_jobs(request):

    jobs = PlacementJob.objects.filter(
        status="Open"
    ).order_by("-created_at")

    applied_jobs = PlacementApplication.objects.filter(
        talent=request.user
    ).values_list(
        "job_id",
        flat=True
    )

    return render(
        request,
        "placements/browse_jobs.html",
        {
            "jobs": jobs,
            "applied_jobs": applied_jobs
        }
    )


from .models import (
    PlacementJob,
    PlacementApplication
)


@login_required
def apply_job(request, job_id):

    job = PlacementJob.objects.get(
        id=job_id
    )

    already_applied = PlacementApplication.objects.filter(
        job=job,
        talent=request.user
    ).exists()

    if already_applied:

        return redirect(
            "browse_jobs"
        )

    if request.method == "POST":

        PlacementApplication.objects.create(

            job=job,

            talent=request.user,

            message=request.POST.get(
                "message"
            )

        )

        return redirect(
            "my_job_applications"
        )

    return render(
        request,
        "placements/apply_job.html",
        {
            "job": job
        }
    )


@login_required
def my_job_applications(request):

    applications = PlacementApplication.objects.filter(
        talent=request.user
    ).select_related(
        "job"
    )

    return render(
        request,
        "placements/my_job_applications.html",
        {
            "applications": applications
        }
    )


@login_required
def job_applications(request, job_id):

    startup = StartupProfile.objects.get(
        user=request.user
    )

    job = PlacementJob.objects.get(
        id=job_id,
        startup=startup
    )

    applications = PlacementApplication.objects.filter(
        job=job
    ).select_related(
        "talent"
    )

    return render(
        request,
        "placements/job_applications.html",
        {
            "job": job,
            "applications": applications
        }
    )


@login_required
def shortlist_application(request, app_id):

    application = PlacementApplication.objects.get(
        id=app_id
    )

    application.status = "Shortlisted"

    application.save()

    return redirect(
        "job_applications",
        application.job.id
    )


@login_required
def interview_application(request, app_id):

    application = PlacementApplication.objects.get(
        id=app_id
    )

    application.status = "Interview"

    application.save()

    return redirect(
        "job_applications",
        application.job.id
    )


@login_required
def hire_application(request, app_id):

    application = PlacementApplication.objects.get(
        id=app_id
    )

    application.status = "Hired"

    application.save()

    return redirect(
        "job_applications",
        application.job.id
    )


from django.db.models import Count

@login_required
def hiring_dashboard(request):

    startup = StartupProfile.objects.get(
        user=request.user
    )

    jobs = PlacementJob.objects.filter(
        startup=startup
    )

    applications = PlacementApplication.objects.filter(
        job__startup=startup
    )

    total_jobs = jobs.count()

    total_applications = applications.count()

    shortlisted = applications.filter(
        status="Shortlisted"
    ).count()

    interviews = applications.filter(
        status="Interview"
    ).count()

    hired = applications.filter(
        status="Hired"
    ).count()

    context = {

        "total_jobs": total_jobs,

        "total_applications": total_applications,

        "shortlisted": shortlisted,

        "interviews": interviews,

        "hired": hired,

        "jobs": jobs

    }

    return render(
        request,
        "placements/hiring_dashboard.html",
        context
    )


from ai_engine.services import calculate_match_score
from accounts.models import User


@login_required
def recommended_candidates(request, job_id):

    job = PlacementJob.objects.get(
        id=job_id
    )

    talents = User.objects.filter(
        role="talent"
    )

    ranked = []

    for talent in talents:

        match_score = calculate_match_score(
            job,
            talent
        )

        ranked.append({

            "talent": talent,

            "score": match_score

        })

    ranked = sorted(

        ranked,

        key=lambda x: x["score"],

        reverse=True

    )

    return render(

        request,

        "placements/recommended_candidates.html",

        {

            "job": job,

            "ranked": ranked[:20]

        }

    )