from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from core.subscription import has_active_subscription
from reputation.views import calculate_deployment_score

from .models import Sprint, Submission, Task
from .forms import SprintForm, TaskForm
from .utils import create_activity
from startups.models import StartupProfile

from payments.models import UserSubscription
from django.contrib import messages

@login_required
def execution_dashboard(request):
    """Execution Dashboard - Overview of all sprints."""
    
    try:
        startup_profile = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'total_sprints': 0,
            'active_sprints': 0,
            'completed_sprints': 0,
            'open_sprints': 0,
            'recent_sprints': [],
            'page_title': 'Execution Dashboard',
            'page_icon': '🚀',
            'page_subtitle': 'Manage your sprints and execution',
            'no_startup': True,
        }
        return render(request, 'sprints/execution_dashboard.html', context)
    
    sprints = Sprint.objects.filter(startup=startup_profile)
    
    total_sprints = sprints.count()
    active_sprints = sprints.filter(status='active').count()
    completed_sprints = sprints.filter(status='completed').count()
    open_sprints = sprints.filter(status='open').count()
    
    recent_sprints = sprints.order_by('-created_at')[:5]
    
    context = {
        'total_sprints': total_sprints,
        'active_sprints': active_sprints,
        'completed_sprints': completed_sprints,
        'open_sprints': open_sprints,
        'recent_sprints': recent_sprints,
        'page_title': 'Execution Dashboard',
        'page_icon': '🚀',
        'page_subtitle': 'Manage your sprints and execution',
        'no_startup': False,
    }
    return render(request, 'sprints/execution_dashboard.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Sprint
from .forms import SprintForm
from startups.models import StartupProfile
from payments.subscription_checker import get_plan, can_create_sprint


@login_required
def create_sprint(request):
    # Get startup profile
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found. Please set up your profile first.')
        return redirect('startup_profile_setup')
    
    # Check subscription plan
    plan = get_plan(request.user)
    
    # Check if user can create sprint based on their plan
    if not can_create_sprint(request.user):
        messages.warning(request, f'Your {plan} plan does not allow creating more sprints. Please upgrade your plan.')
        # FIXED: Added 'payments:' namespace
        return redirect('payments:subscription_plans')
    
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            sprint = form.save(commit=False)
            sprint.startup = startup
            sprint.created_by = request.user
            sprint.save()
            messages.success(request, f'Sprint "{sprint.title}" created successfully!')
            return redirect('startup_sprints')
    else:
        form = SprintForm()
    
    context = {
        'form': form,
        'startup': startup,
        'current_plan': plan,
        'page_title': 'Create Sprint',
        'page_icon': '🚀',
    }
    
    return render(request, 'sprints/create_sprint.html', context)

@login_required
def edit_sprint(request, sprint_id):
    """Edit an existing sprint"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')
    
    # Get the sprint - ensure it belongs to the user's startup
    sprint = get_object_or_404(Sprint, id=sprint_id, startup=startup)
    
    if request.method == 'POST':
        form = SprintForm(request.POST, instance=sprint)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sprint "{sprint.title}" updated successfully!')
            return redirect('startup_sprints')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SprintForm(instance=sprint)
    
    context = {
        'form': form,
        'sprint': sprint,
        'startup': startup,
        'page_title': f'Edit Sprint: {sprint.title}',
        'page_icon': '✏️',
        'is_edit': True,  # This flag tells the template it's edit mode
    }
    
    # Use the same template as create_sprint
    return render(request, 'sprints/create_sprint.html', context)


@login_required
def delete_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id, startup__user=request.user)
    
    if request.method == 'POST':
        sprint_title = sprint.title
        sprint.delete()
        messages.success(request, f'Sprint "{sprint_title}" deleted successfully!')
        return redirect('startup_sprints')
    
    return redirect('startup_sprints')


@login_required
def startup_sprints(request):
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')
    
    sprints = Sprint.objects.filter(startup=startup).order_by('-created_at')
    
    context = {
        'sprints': sprints,
        'startup': startup,
        'page_title': 'My Sprints',
        'page_icon': '📋',
    }
    
    return render(request, 'sprints/startup_sprints.html', context)

@login_required
def browse_sprints(request):

    sprints = Sprint.objects.filter(
        status='open'
    ).select_related(
        'startup'
    )

    return render(
        request,
        'sprints/browse_sprints.html',
        {
            'sprints': sprints
        }
    )



from .models import SprintApplication

@login_required
def apply_sprint(request, sprint_id):

    sprint = Sprint.objects.get(id=sprint_id)

    already_applied = SprintApplication.objects.filter(
        sprint=sprint,
        talent=request.user
    ).exists()

    if already_applied:
        return redirect('browse_sprints')

    if request.method == 'POST':

        SprintApplication.objects.create(
            sprint=sprint,
            talent=request.user,
            message=request.POST.get('message')
        )

        return redirect('my_applications')

    return render(
        request,
        'sprints/apply_sprint.html',
        {
            'sprint': sprint
        }
    )


from .models import SprintApplication

@login_required
def sprint_applications(request, sprint_id):

    startup_profile = StartupProfile.objects.get(
        user=request.user
    )

    sprint = Sprint.objects.get(
        id=sprint_id,
        startup=startup_profile
    )

    applications = SprintApplication.objects.filter(
        sprint=sprint
    )

    return render(
        request,
        'sprints/sprint_applications.html',
        {
            'sprint': sprint,
            'applications': applications
        }
    )


from .models import SprintMember

@login_required
def accept_application(request, app_id):

    application = SprintApplication.objects.get(
        id=app_id
    )

    if application.sprint.startup.user != request.user:
        return redirect('startup_sprints')

    application.status = 'accepted'
    application.sprint.status='active'
    application.sprint.save()
    application.save()

    create_activity(
        application.talent,
        f"Joined Sprint {application.sprint.title}"
    )

    create_activity(
        request.user,
        f"Accepted {application.talent.username}"
    )

    SprintMember.objects.get_or_create(
        sprint=application.sprint,
        user=application.talent
    )

    return redirect(
        'sprint_applications',
        application.sprint.id
    )


@login_required
def sprint_members(request, sprint_id):

    sprint = Sprint.objects.get(
        id=sprint_id
    )

    members = SprintMember.objects.filter(
        sprint=sprint
    )

    return render(
        request,
        'sprints/sprint_members.html',
        {
            'sprint': sprint,
            'members': members
        }
    )

from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def create_task(request, sprint_id):

    sprint = Sprint.objects.get(id=sprint_id)

    if request.method == 'POST':

        form = TaskForm(request.POST)

        form.fields['assigned_to'].queryset = User.objects.filter(
            sprintmember__sprint=sprint
        )

        if form.is_valid():

            task = form.save(commit=False)
            task.sprint = sprint
            task.save()

            print("TASK SAVED:", task.id)

            return redirect(
                'sprint_tasks',
                sprint.id
            )

        else:
            print(form.errors)

    else:

        form = TaskForm()

        form.fields['assigned_to'].queryset = User.objects.filter(
            sprintmember__sprint=sprint
        )

    return render(
        request,
        'tasks/create_task.html',
        {
            'form': form,
            'sprint': sprint
        }
    )


@login_required
def sprint_tasks(request, sprint_id):

    sprint = Sprint.objects.get(id=sprint_id)

    tasks = Task.objects.filter(
        sprint=sprint
    ).order_by('-created_at')

    return render(
        request,
        'tasks/task_board.html',
        {
            'sprint': sprint,
            'tasks': tasks
        }
    )



@login_required
def submit_task(request, task_id):

    task = Task.objects.get(
        id=task_id
    )

    existing = Submission.objects.filter(
        task=task,
        user=request.user
    ).exists()

    if existing:
        return redirect("my_tasks")

    if request.method == "POST":

        Submission.objects.create(
            task=task,
            user=request.user,
            github_url=request.POST.get("github_url"),
            drive_url=request.POST.get("drive_url"),
            notes=request.POST.get("notes")
        )

        task.status = "review"
        task.save()

        create_activity(
            request.user,
            f"Submitted Task {task.title}"
        )

        return redirect("my_tasks")

    return render(
        request,
        "tasks/submit_task.html",
        {
            "task": task
        }
    )

@login_required
def my_applications(request):

    applications = SprintApplication.objects.filter(
        talent=request.user
    ).select_related(
        'sprint'
    )

    pending_count = applications.filter(
        status='pending'
    ).count()

    accepted_count = applications.filter(
        status='accepted'
    ).count()

    rejected_count = applications.filter(
        status='rejected'
    ).count()

    

    context = {

        'applications': applications,

        'pending_count': pending_count,

        'accepted_count': accepted_count,

        'rejected_count': rejected_count,

    }

    return render(
        request,
        'sprints/my_applications.html',
        context
    )


@login_required
def reject_application(request, app_id):

    application = SprintApplication.objects.get(
        id=app_id
    )

    application.status = 'rejected'

    application.save()

    return redirect(
        'sprint_applications',
        application.sprint.id
    )


from reputation.models import ReputationScore, Review

@login_required
def sprint_detail(request, sprint_id):

    sprint = Sprint.objects.get(
        id=sprint_id
    )

    members = sprint.members.all()

    tasks = sprint.tasks.all()

    reviews = Review.objects.filter(
        sprint=sprint
    )

    total_tasks = tasks.count()

    completed_tasks = tasks.filter(
        status='completed'
    ).count()

    progress = 0

    if total_tasks > 0:
        progress = int(
            completed_tasks * 100 / total_tasks
        )

    return render(
        request,
        'sprints/sprint_detail.html',
        {
            'sprint': sprint,
            'members': members,
            'tasks': tasks,
            'reviews': reviews,
            'progress': progress
        }
    )

@login_required
def task_detail(request, task_id):

    task = Task.objects.get(id=task_id)

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'sprint': task.sprint   # ✅ ADD THIS
    })


@login_required
def my_tasks(request):

    tasks = Task.objects.filter(
        assigned_to=request.user
    )

    return render(
        request,
        'tasks/my_tasks.html',
        {
            'tasks': tasks
        }
    )



@login_required
def review_submissions(request, sprint_id):

    sprint = Sprint.objects.get(
        id=sprint_id
    )

    tasks = Task.objects.filter(
        sprint=sprint
    )

    submissions = Submission.objects.filter(
        task__in=tasks
    )

    return render(
        request,
        'tasks/review_submissions.html',
        {
            'sprint': sprint,
            'submissions': submissions
        }
    )


from django.contrib import messages
from django.utils import timezone

@login_required
def submission_review(request, submission_id):

    submission = get_object_or_404(
        Submission,
        id=submission_id
    )

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "approve":

            submission.reviewed = True
            submission.reviewed_at = timezone.now()
            submission.save()

            submission.task.status = "completed"
            submission.task.save()

            create_activity(
                submission.user,
                f"Task Approved : {submission.task.title}"
            )

            messages.success(
                request,
                "Submission approved successfully."
            )

        elif action == "reject":

            submission.task.status = "assigned"
            submission.task.save()

            create_activity(
                submission.user,
                f"Task Rejected : {submission.task.title}"
            )

            messages.warning(
                request,
                "Submission rejected."
            )

        return redirect(
            "submission_review",
            submission.id
        )

    return render(
    request,
    "tasks/submission_review.html",
    {
        "submission": submission,
        "review_url": f"/reputation/review/{submission.task.sprint.id}/{submission.user.id}/"
    }
)


from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from reputation.models import ReputationScore
from reputation.views import calculate_deployment_score
from sprints.utils import create_activity
from talents.models import PortfolioProject

@login_required
def approve_submission(request, submission_id):

    submission = Submission.objects.get(
        id=submission_id
    )

    task = submission.task
    sprint = task.sprint

    # Mark submission reviewed

    submission.reviewed = True
    submission.reviewed_at = timezone.now()
    submission.save()

    # Mark task completed

    task.status = "completed"
    task.save()

    # Create activity

    create_activity(
        submission.user,
        f"Task Approved : {task.title}"
    )

    # Update reputation

    reputation, created = ReputationScore.objects.get_or_create(
        user=submission.user
    )

    reputation.tasks_completed += 1
    reputation.save()

    calculate_deployment_score(
        submission.user
    )

    # -----------------------------------
    # ADD TO PORTFOLIO AUTOMATICALLY
    # -----------------------------------

    all_completed = not sprint.tasks.exclude(
        status="completed"
    ).exists()

    if all_completed:

        PortfolioProject.objects.get_or_create(

            user=submission.user,

            title=sprint.title,

            sprint_id=task.sprint.id,

            defaults={

                "project_type": "Sprint",

                "description": sprint.description,

                "skills": sprint.required_skills,

                "github_url": submission.github_url,

                "title": task.sprint.title,

                "description": task.sprint.description,

                "is_verified": True,

            }

        )

    # -----------------------------------

    return redirect(
        "review_submissions",
        sprint.id
    )