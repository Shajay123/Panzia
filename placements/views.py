from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from startups.models import StartupProfile
from accounts.models import User
from ai_engine.services import calculate_match_score

from .forms import PlacementJobForm
from .models import PlacementJob, PlacementApplication


# ============================================
# JOB CRUD OPERATIONS
# ============================================

@login_required
def create_job(request):
    """Create a new job posting."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found. Please complete your startup profile.')
        return redirect('startup_profile_setup')

    if request.method == "POST":
        form = PlacementJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.startup = startup
            # Set default status if not provided
            if not job.status:
                job.status = 'Open'
            job.save()
            messages.success(request, f'Job "{job.title}" created successfully!')
            return redirect("startup_jobs")
        else:
            messages.error(request, 'Please correct the errors below.')
            print("Form errors:", form.errors)
    else:
        form = PlacementJobForm(initial={'status': 'Open'})

    return render(request, "placements/create_job.html", {"form": form})


@login_required
def edit_job(request, job_id):
    """Edit an existing job posting."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')

    job = get_object_or_404(PlacementJob, id=job_id, startup=startup)

    if request.method == "POST":
        form = PlacementJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job "{job.title}" updated successfully!')
            return redirect("startup_jobs")
        else:
            messages.error(request, 'Please correct the errors below.')
            print("Form errors:", form.errors)
    else:
        form = PlacementJobForm(instance=job)

    return render(request, "placements/edit_job.html", {
        "form": form,
        "job": job
    })


@login_required
def delete_job(request, job_id):
    """Delete a job posting."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')

    job = get_object_or_404(PlacementJob, id=job_id, startup=startup)

    if request.method == "POST":
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted successfully!')
        return redirect("startup_jobs")

    return render(request, "placements/delete_job.html", {"job": job})


@login_required
def startup_jobs(request):
    """View all jobs for the startup."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')

    jobs = PlacementJob.objects.filter(startup=startup).order_by('-created_at')
    
    # Count applications for each job
    for job in jobs:
        job.application_count = PlacementApplication.objects.filter(job=job).count()

    return render(request, "placements/startup_jobs.html", {
        "jobs": jobs,
        "active_jobs": jobs.filter(status='Open').count(),
        "pending_jobs": jobs.filter(status='Pending').count(),
        "closed_jobs": jobs.filter(status='Closed').count(),
    })


# ============================================
# TALENT - BROWSE & APPLY
# ============================================

@login_required
def browse_jobs(request):
    """Browse all open jobs for talents."""
    jobs = PlacementJob.objects.filter(
        status="Open"
    ).order_by("-created_at")

    applied_jobs = PlacementApplication.objects.filter(
        talent=request.user
    ).values_list("job_id", flat=True)

    return render(request, "placements/browse_jobs.html", {
        "jobs": jobs,
        "applied_jobs": applied_jobs
    })


@login_required
def apply_job(request, job_id):
    """Apply for a job."""
    job = get_object_or_404(PlacementJob, id=job_id)

    already_applied = PlacementApplication.objects.filter(
        job=job,
        talent=request.user
    ).exists()

    if already_applied:
        messages.warning(request, 'You have already applied for this job.')
        return redirect("browse_jobs")

    if request.method == "POST":
        application = PlacementApplication.objects.create(
            job=job,
            talent=request.user,
            message=request.POST.get("message", "")
        )
        messages.success(request, f'Successfully applied for "{job.title}"!')
        return redirect("my_job_applications")

    return render(request, "placements/apply_job.html", {"job": job})


@login_required
def my_job_applications(request):
    """View all applications by the talent."""
    applications = PlacementApplication.objects.filter(
        talent=request.user
    ).select_related("job").order_by("-applied_at")

    return render(request, "placements/my_job_applications.html", {
        "applications": applications
    })


# ============================================
# STARTUP - APPLICATION MANAGEMENT
# ============================================

@login_required
def job_applications(request, job_id):
    """View all applications for a specific job."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')

    job = get_object_or_404(PlacementJob, id=job_id, startup=startup)
    applications = PlacementApplication.objects.filter(
        job=job
    ).select_related("talent").order_by("-applied_at")

    # Count applications by status
    status_counts = {
        'pending': applications.filter(status='Pending').count(),
        'shortlisted': applications.filter(status='Shortlisted').count(),
        'interview': applications.filter(status='Interview').count(),
        'hired': applications.filter(status='Hired').count(),
        'rejected': applications.filter(status='Rejected').count(),
    }

    return render(request, "placements/job_applications.html", {
        "job": job,
        "applications": applications,
        "status_counts": status_counts
    })


@login_required
def shortlist_application(request, app_id):
    """Shortlist an application."""
    application = get_object_or_404(PlacementApplication, id=app_id)
    
    if application.job.startup.user != request.user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('hiring_dashboard')

    application.status = "Shortlisted"
    application.save()
    messages.success(request, f'Application from {application.talent.get_full_name()} shortlisted!')
    return redirect("job_applications", application.job.id)


@login_required
def interview_application(request, app_id):
    """Move application to interview stage."""
    application = get_object_or_404(PlacementApplication, id=app_id)
    
    if application.job.startup.user != request.user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('hiring_dashboard')

    application.status = "Interview"
    application.save()
    messages.success(request, f'Application from {application.talent.get_full_name()} moved to interview!')
    return redirect("job_applications", application.job.id)


@login_required
def hire_application(request, app_id):
    """Hire a candidate."""
    application = get_object_or_404(PlacementApplication, id=app_id)
    
    if application.job.startup.user != request.user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('hiring_dashboard')

    application.status = "Hired"
    application.save()
    messages.success(request, f'Congratulations! {application.talent.get_full_name()} has been hired!')
    return redirect("job_applications", application.job.id)


@login_required
def reject_application(request, app_id):
    """Reject an application."""
    application = get_object_or_404(PlacementApplication, id=app_id)
    
    if application.job.startup.user != request.user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('hiring_dashboard')

    application.status = "Rejected"
    application.save()
    messages.info(request, f'Application from {application.talent.get_full_name()} rejected.')
    return redirect("job_applications", application.job.id)


# ============================================
# DASHBOARD
# ============================================

@login_required
def hiring_dashboard(request):
    """Hiring dashboard with analytics."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')

    jobs = PlacementJob.objects.filter(startup=startup)
    applications = PlacementApplication.objects.filter(job__startup=startup)

    total_jobs = jobs.count()
    total_applications = applications.count()
    shortlisted = applications.filter(status="Shortlisted").count()
    interviews = applications.filter(status="Interview").count()
    hired = applications.filter(status="Hired").count()
    rejected = applications.filter(status="Rejected").count()
    pending = applications.filter(status="Pending").count()

    context = {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "shortlisted": shortlisted,
        "interviews": interviews,
        "hired": hired,
        "rejected": rejected,
        "pending": pending,
        "jobs": jobs,
    }
    return render(request, "placements/hiring_dashboard.html", context)


# ============================================
# AI RECOMMENDATIONS
# ============================================

@login_required
def recommended_candidates(request, job_id):
    """Get AI-powered candidate recommendations."""
    job = get_object_or_404(PlacementJob, id=job_id)
    
    # Get all talent users
    talents = User.objects.filter(role="talent")
    
    ranked = []
    for talent in talents:
        match_score = calculate_match_score(job, talent)
        ranked.append({
            "talent": talent,
            "score": match_score
        })
    
    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    return render(request, "placements/recommended_candidates.html", {
        "job": job,
        "ranked": ranked[:20]
    })