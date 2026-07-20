# sprints/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from accounts.models import User
from reputation.views import calculate_deployment_score
from startups.models import StartupProfile

from .models import Sprint, Submission, Task, SprintApplication, SprintMember
from .forms import SprintForm, TaskForm
from .utils import create_activity, update_sprint_progress


# ============================================
# EXECUTION DASHBOARD (Startup)
# ============================================

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
        return render(request, 'sprints/startup/execution_dashboard.html', context)
    
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
    return render(request, 'sprints/startup/execution_dashboard.html', context)


# ============================================
# SPRINT CRUD (Startup)
# ============================================

@login_required
def create_sprint(request):
    """Create a new sprint."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found. Please set up your profile first.')
        return redirect('startup_profile_setup')
    
    # Check subscription plan
    from payments.subscription_checker import get_plan, can_create_sprint
    plan = get_plan(request.user)
    
    if not can_create_sprint(request.user):
        messages.warning(request, f'Your {plan} plan does not allow creating more sprints. Please upgrade your plan.')
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
    
    # Get sprint count for the progress bar
    sprint_count = Sprint.objects.filter(startup=startup).count()
    
    context = {
        'form': form,
        'startup': startup,
        'current_plan': plan,
        'sprint_count': sprint_count,
        'sprint_limit': 5 if plan == 'FREE' else 20 if plan == 'PRO' else 100,
        'remaining_sprints': (5 if plan == 'FREE' else 20 if plan == 'PRO' else 100) - sprint_count,
        'page_title': 'Create Sprint',
        'page_icon': '🚀',
        'is_edit': False,
    }
    return render(request, 'sprints/startup/create_sprint.html', context)


@login_required
def edit_sprint(request, sprint_id):
    """Edit an existing sprint."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')
    
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
        'is_edit': True,
    }
    return render(request, 'sprints/startup/create_sprint.html', context)


@login_required
def delete_sprint(request, sprint_id):
    """Delete a sprint."""
    sprint = get_object_or_404(Sprint, id=sprint_id, startup__user=request.user)
    
    if request.method == 'POST':
        sprint_title = sprint.title
        sprint.delete()
        messages.success(request, f'Sprint "{sprint_title}" deleted successfully!')
        return redirect('startup_sprints')
    
    return redirect('startup_sprints')


@login_required
def startup_sprints(request):
    """View all sprints for a startup."""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')
    
    sprints = Sprint.objects.filter(startup=startup).order_by('-created_at')
    
    # Count by status
    active_count = sprints.filter(status='active').count()
    completed_count = sprints.filter(status='completed').count()
    open_count = sprints.filter(status='open').count()
    
    context = {
        'sprints': sprints,
        'startup': startup,
        'active_count': active_count,
        'completed_count': completed_count,
        'open_count': open_count,
        'page_title': 'My Sprints',
        'page_icon': '📋',
    }
    return render(request, 'sprints/startup/startup_sprints.html', context)


# ============================================
# SPRINT DETAIL (Shared)
# ============================================

@login_required
def sprint_detail(request, sprint_id):
    """View sprint details - accessible to both startup and talent."""
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    # Check if user has access
    is_member = SprintMember.objects.filter(sprint=sprint, user=request.user).exists()
    is_owner = sprint.startup.user == request.user
    
    if not is_member and not is_owner and request.user.role == 'talent':
        messages.error(request, 'You do not have access to this sprint.')
        return redirect('browse_sprints')
    
    members = sprint.members.all()
    tasks = sprint.tasks.all()
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    # Check application status for talent
    application_status = None
    if request.user.role == 'talent':
        try:
            application = SprintApplication.objects.get(sprint=sprint, talent=request.user)
            application_status = application.status
        except SprintApplication.DoesNotExist:
            application_status = None
    
    # Check if user has applied
    applied_sprint_ids = []
    if request.user.role == 'talent':
        applied_sprint_ids = SprintApplication.objects.filter(
            talent=request.user
        ).values_list('sprint_id', flat=True)
    
    context = {
        'sprint': sprint,
        'members': members,
        'tasks': tasks,
        'progress': progress,
        'application_status': application_status,
        'is_member': is_member,
        'is_owner': is_owner,
        'applied_sprint_ids': list(applied_sprint_ids),
        'page_title': sprint.title,
        'page_icon': '🚀',
    }
    
    # Redirect to appropriate template based on role
    if request.user.role in ['startup_admin', 'startup_hr', 'startup_manager']:
        return render(request, 'sprints/startup/sprint_detail.html', context)
    else:
        return render(request, 'sprints/talent/sprint_detail.html', context)


# ============================================
# STARTUP - SPRINT APPLICATIONS
# ============================================

@login_required
def sprint_applications(request, sprint_id):
    """View all applications for a sprint."""
    try:
        startup_profile = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, 'Startup profile not found.')
        return redirect('startup_profile_setup')
    
    sprint = get_object_or_404(Sprint, id=sprint_id, startup=startup_profile)
    applications = SprintApplication.objects.filter(
        sprint=sprint
    ).select_related('talent').order_by('-applied_at')
    
    context = {
        'sprint': sprint,
        'applications': applications,
        'page_title': f'Applications for {sprint.title}',
        'page_icon': '👥',
        'page_subtitle': 'Review and manage talent applications',
    }
    return render(request, 'sprints/startup/sprint_applications.html', context)


@login_required
def accept_application(request, app_id):
    """Accept a sprint application."""
    application = get_object_or_404(SprintApplication, id=app_id)
    
    if application.sprint.startup.user != request.user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('startup_sprints')
    
    if application.status != 'pending':
        messages.warning(request, 'This application has already been processed.')
        return redirect('sprint_applications', application.sprint.id)
    
    application.status = 'accepted'
    application.save()
    
    # Update sprint status if it was open
    if application.sprint.status == 'open':
        application.sprint.status = 'active'
        application.sprint.save()
    
    # Add to sprint members
    SprintMember.objects.get_or_create(
        sprint=application.sprint,
        user=application.talent
    )
    
    create_activity(
        application.talent,
        f"Joined Sprint: {application.sprint.title}"
    )
    create_activity(
        request.user,
        f"Accepted {application.talent.username} into {application.sprint.title}"
    )
    
    messages.success(request, f'Accepted {application.talent.username} into the sprint!')
    return redirect('sprint_applications', application.sprint.id)


@login_required
def reject_application(request, app_id):
    """Reject a sprint application."""
    application = get_object_or_404(SprintApplication, id=app_id)
    
    if application.sprint.startup.user != request.user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('startup_sprints')
    
    if application.status != 'pending':
        messages.warning(request, 'This application has already been processed.')
        return redirect('sprint_applications', application.sprint.id)
    
    application.status = 'rejected'
    application.save()
    
    messages.info(request, f'Rejected {application.talent.username} from the sprint.')
    return redirect('sprint_applications', application.sprint.id)


# ============================================
# STARTUP - SPRINT MEMBERS
# ============================================

@login_required
def sprint_members(request, sprint_id):
    """View all members of a sprint."""
    sprint = get_object_or_404(Sprint, id=sprint_id, startup__user=request.user)
    members = SprintMember.objects.filter(sprint=sprint).select_related('user')
    
    context = {
        'sprint': sprint,
        'members': members,
        'page_title': f'Members - {sprint.title}',
        'page_icon': '👤',
        'page_subtitle': 'View all team members working on this sprint',
    }
    return render(request, 'sprints/startup/sprint_members.html', context)


# ============================================
# TALENT - APPLY TO SPRINT
# ============================================

@login_required
def apply_sprint(request, sprint_id):
    """Apply to a sprint."""
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    if sprint.status != 'open':
        messages.warning(request, 'This sprint is no longer accepting applications.')
        return redirect('browse_sprints')
    
    already_applied = SprintApplication.objects.filter(
        sprint=sprint,
        talent=request.user
    ).exists()
    
    if already_applied:
        messages.warning(request, 'You have already applied to this sprint.')
        return redirect('browse_sprints')
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        SprintApplication.objects.create(
            sprint=sprint,
            talent=request.user,
            message=message,
            status='pending'
        )
        create_activity(
            request.user,
            f"Applied to sprint: {sprint.title}"
        )
        messages.success(request, f'Successfully applied to "{sprint.title}"!')
        return redirect('my_applications')
    
    context = {
        'sprint': sprint,
        'page_title': f'Apply to {sprint.title}',
        'page_icon': '📝',
        'page_subtitle': 'Showcase your skills and explain why you\'re the right builder',
    }
    return render(request, 'sprints/talent/apply_sprint.html', context)


# ============================================
# TALENT - MY APPLICATIONS
# ============================================

@login_required
def my_applications(request):
    """View all sprint applications by the talent."""
    applications = SprintApplication.objects.filter(
        talent=request.user
    ).select_related('sprint', 'sprint__startup').order_by('-applied_at')
    
    pending_count = applications.filter(status='pending').count()
    accepted_count = applications.filter(status='accepted').count()
    rejected_count = applications.filter(status='rejected').count()
    
    context = {
        'applications': applications,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'page_title': 'My Sprint Applications',
        'page_icon': '📨',
        'page_subtitle': 'Track your sprint applications',
    }
    return render(request, 'sprints/talent/my_applications.html', context)


# ============================================
# TALENT - BROWSE SPRINTS
# ============================================

@login_required
def browse_sprints(request):
    """Browse all open sprints for talents."""
    sprints = Sprint.objects.filter(
        status='open'
    ).select_related('startup').order_by('-created_at')
    
    applied_sprint_ids = SprintApplication.objects.filter(
        talent=request.user
    ).values_list('sprint_id', flat=True)
    
    accepted_sprints = SprintApplication.objects.filter(
        talent=request.user,
        status='accepted'
    ).values_list('sprint_id', flat=True)
    
    context = {
        'sprints': sprints,
        'applied_sprint_ids': list(applied_sprint_ids),
        'accepted_sprint_ids': list(accepted_sprints),
        'page_title': 'Browse Sprints',
        'page_icon': '🚀',
        'page_subtitle': 'Find and join startup sprints',
    }
    return render(request, 'sprints/talent/browse_sprints.html', context)


# ============================================
# TASKS - STARTUP SIDE
# ============================================

@login_required
def create_task(request, sprint_id):
    """Create a task for a sprint."""
    sprint = get_object_or_404(Sprint, id=sprint_id, startup__user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.sprint = sprint
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('sprint_tasks', sprint.id)
    else:
        form = TaskForm()
        form.fields['assigned_to'].queryset = User.objects.filter(
            sprintmember__sprint=sprint
        )
    
    context = {
        'form': form,
        'sprint': sprint,
        'page_title': f'Create Task - {sprint.title}',
        'page_icon': '➕',
        'page_subtitle': 'Assign work to your sprint team members',
    }
    return render(request, 'sprints/startup/create_task.html', context)


@login_required
def sprint_tasks(request, sprint_id):
    """View all tasks for a sprint."""
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    # Check access
    is_owner = sprint.startup.user == request.user
    is_member = SprintMember.objects.filter(sprint=sprint, user=request.user).exists()
    
    if not is_owner and not is_member:
        messages.error(request, 'You do not have access to this sprint.')
        return redirect('browse_sprints')
    
    tasks = Task.objects.filter(sprint=sprint).order_by('-created_at')
    
    context = {
        'sprint': sprint,
        'tasks': tasks,
        'page_title': f'Tasks - {sprint.title}',
        'page_icon': '📋',
        'page_subtitle': 'Manage and monitor all tasks',
    }
    
    if is_owner:
        return render(request, 'sprints/startup/task_board.html', context)
    else:
        return render(request, 'sprints/talent/task_board.html', context)


@login_required
def task_detail(request, task_id):
    """View task details."""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has access
    has_access = (
        task.assigned_to == request.user or
        task.sprint.startup.user == request.user
    )
    
    if not has_access:
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('my_tasks')
    
    # Get submissions for this task
    submissions = Submission.objects.filter(task=task).order_by('-submitted_at')
    
    # Pass today's date for deadline calculation
    from datetime import date, timedelta
    today = date.today()
    today_plus_3 = today + timedelta(days=3)
    
    context = {
        'task': task,
        'sprint': task.sprint,
        'submissions': submissions,
        'today': today,
        'today_plus_3': today_plus_3,
        'page_title': f'Task: {task.title}',
        'page_icon': '📄',
    }
    
    if task.sprint.startup.user == request.user:
        return render(request, 'sprints/startup/task_detail.html', context)
    else:
        return render(request, 'sprints/talent/task_detail.html', context)


# ============================================
# TALENT - SUBMIT TASK
# ============================================

@login_required
def submit_task(request, task_id):
    """Submit a task for review."""
    task = get_object_or_404(Task, id=task_id)
    
    if task.assigned_to != request.user:
        messages.error(request, 'This task is not assigned to you.')
        return redirect('my_tasks')
    
    existing = Submission.objects.filter(task=task, user=request.user).exists()
    if existing:
        messages.warning(request, 'You have already submitted this task.')
        return redirect('my_tasks')
    
    if request.method == "POST":
        submission = Submission.objects.create(
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
            f"Submitted Task: {task.title}"
        )
        messages.success(request, f'Task "{task.title}" submitted successfully!')
        return redirect("my_tasks")
    
    context = {
        "task": task,
        "page_title": f'Submit Task: {task.title}',
        "page_icon": "📤",
        "page_subtitle": "Submit your work for review",
    }
    return render(request, "sprints/talent/submit_task.html", context)


# ============================================
# TALENT - MY TASKS
# ============================================

@login_required
def my_tasks(request):
    """View all tasks assigned to the talent."""
    tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('sprint').order_by('-created_at')
    
    # Use correct status names from your model
    pending_count = tasks.filter(status='pending').count()
    progress_count = tasks.filter(status='progress').count()
    review_count = tasks.filter(status='review').count()
    completed_count = tasks.filter(status='completed').count()
    
    context = {
        'tasks': tasks,
        'pending_count': pending_count,
        'progress_count': progress_count,
        'review_count': review_count,
        'completed_count': completed_count,
        'page_title': 'My Tasks',
        'page_icon': '✅',
        'page_subtitle': 'View and manage your assigned tasks',
    }
    return render(request, 'sprints/talent/my_tasks.html', context)




# ============================================
# STARTUP - REVIEW SUBMISSIONS
# ============================================

@login_required
def review_submissions(request, sprint_id):
    """Review all submissions for a sprint."""
    sprint = get_object_or_404(Sprint, id=sprint_id, startup__user=request.user)
    tasks = Task.objects.filter(sprint=sprint)
    submissions = Submission.objects.filter(task__in=tasks).select_related('user', 'task')
    
    # Count pending and reviewed
    pending_count = submissions.filter(reviewed=False).count()
    reviewed_count = submissions.filter(reviewed=True).count()
    
    context = {
        'sprint': sprint,
        'submissions': submissions,
        'pending_count': pending_count,
        'reviewed_count': reviewed_count,
        'page_title': f'Review Submissions - {sprint.title}',
        'page_icon': '📊',
        'page_subtitle': 'Review and approve talent submissions',
    }
    return render(request, 'sprints/startup/review_submissions.html', context)


# ============================================
# STARTUP - SUBMISSION REVIEW (Single)
# ============================================

@login_required
def submission_review(request, submission_id):
    """Review a single submission."""
    submission = get_object_or_404(Submission, id=submission_id)
    
    if submission.task.sprint.startup.user != request.user:
        messages.error(request, 'You do not have permission to review this submission.')
        return redirect('my_tasks')
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "approve":
            # Mark submission as reviewed
            submission.reviewed = True
            submission.reviewed_at = timezone.now()
            submission.save()
            
            # Update task status to completed
            submission.task.status = "completed"
            submission.task.save()
            
            # Create activity log
            create_activity(
                submission.user,
                f"Task Approved: {submission.task.title}"
            )
            
            # Update reputation
            from reputation.models import ReputationScore
            reputation, _ = ReputationScore.objects.get_or_create(user=submission.user)
            reputation.tasks_completed += 1
            reputation.save()
            calculate_deployment_score(submission.user)
            
            # Update sprint progress
            sprint = submission.task.sprint
            from .utils import update_sprint_progress
            progress = update_sprint_progress(sprint)
            
            # Check if all tasks in sprint are completed
            all_completed = not sprint.tasks.exclude(status="completed").exists()
            
            if all_completed:
                try:
                    from talents.models import PortfolioProject
                    # ✅ FIX: Get skills as a list, not a QuerySet
                    skills_list = list(sprint.required_skills.all())
                    
                    portfolio, created = PortfolioProject.objects.get_or_create(
                        user=submission.user,
                        sprint_id=sprint.id,
                        defaults={
                            "project_type": "Sprint",
                            "title": sprint.title,
                            "description": sprint.description,
                            "github_url": submission.github_url,
                            "is_verified": True,
                        }
                    )
                    
                    # ✅ FIX: Add skills separately if the field exists
                    if hasattr(portfolio, 'skills'):
                        portfolio.skills.set(skills_list)
                        portfolio.save()
                    
                    if created:
                        messages.success(request, f"✅ Submission approved and added to portfolio! Sprint progress: {progress}%")
                    else:
                        messages.success(request, f"✅ Submission approved! Sprint progress: {progress}%")
                except ImportError:
                    messages.success(request, f"✅ Submission approved! Sprint progress: {progress}%")
                except Exception as e:
                    messages.success(request, f"✅ Submission approved! (Portfolio: {str(e)})")
            else:
                messages.success(request, f"✅ Submission approved! Sprint progress: {progress}%")
            
            return redirect("review_submissions", submission.task.sprint.id)
            
        elif action == "reject":
            # Get rejection reason
            rejection_reason = request.POST.get("rejection_reason", "").strip()
            
            if not rejection_reason:
                messages.error(request, "Please provide a reason for rejection.")
                context = {
                    "submission": submission,
                    "page_title": f'Review Submission - {submission.task.title}',
                    "page_icon": "📝",
                    "page_subtitle": "Review the submitted work and provide feedback",
                }
                return render(request, "sprints/startup/submission_review.html", context)
            
            # Save rejection reason
            submission.rejection_reason = rejection_reason
            submission.reviewed = True
            submission.reviewed_at = timezone.now()
            submission.save()
            
            # Set task status back to 'pending'
            submission.task.status = "pending"
            submission.task.save()
            
            # Create activity log
            create_activity(
                submission.user,
                f"Task Rejected: {submission.task.title} - Reason: {rejection_reason[:100]}"
            )
            
            messages.warning(request, f"❌ Submission rejected: {rejection_reason[:100]}")
            return redirect("review_submissions", submission.task.sprint.id)
    
    context = {
        "submission": submission,
        "page_title": f'Review Submission - {submission.task.title}',
        "page_icon": "📝",
        "page_subtitle": "Review the submitted work and provide feedback",
    }
    return render(request, "sprints/startup/submission_review.html", context)



# ============================================
# STARTUP - APPROVE SUBMISSION (Alternative)
# ============================================

@login_required
def approve_submission(request, submission_id):
    """Approve a submission and add to portfolio."""
    submission = get_object_or_404(Submission, id=submission_id)
    task = submission.task
    sprint = task.sprint
    
    # Check permission
    if sprint.startup.user != request.user:
        messages.error(request, 'You do not have permission to approve this submission.')
        return redirect('my_tasks')
    
    # Check if already reviewed
    if submission.reviewed:
        messages.warning(request, 'This submission has already been reviewed.')
        return redirect("review_submissions", sprint.id)
    
    # Mark submission as reviewed
    submission.reviewed = True
    submission.reviewed_at = timezone.now()
    submission.save()
    
    # Update task status to completed
    task.status = "completed"
    task.save()
    
    # Create activity log
    create_activity(
        submission.user,
        f"Task Approved: {task.title}"
    )
    
    # Update reputation
    from reputation.models import ReputationScore
    reputation, _ = ReputationScore.objects.get_or_create(user=submission.user)
    reputation.tasks_completed += 1
    reputation.save()
    calculate_deployment_score(submission.user)
    
    # Update sprint progress
    from .utils import update_sprint_progress
    progress = update_sprint_progress(sprint)
    
    # Check if all tasks in sprint are completed
    all_completed = not sprint.tasks.exclude(status="completed").exists()
    
    if all_completed:
        # Add to portfolio
        try:
            from talents.models import PortfolioProject
            # ✅ FIX: Get skills as a list
            skills_list = list(sprint.required_skills.all())
            
            portfolio, created = PortfolioProject.objects.get_or_create(
                user=submission.user,
                sprint_id=sprint.id,
                defaults={
                    "project_type": "Sprint",
                    "title": sprint.title,
                    "description": sprint.description,
                    "github_url": submission.github_url,
                    "is_verified": True,
                }
            )
            
            # ✅ FIX: Add skills separately
            if hasattr(portfolio, 'skills'):
                portfolio.skills.set(skills_list)
                portfolio.save()
            
            if created:
                messages.success(request, f'✅ Submission approved and added to portfolio! Sprint progress: {progress}%')
            else:
                messages.success(request, f'✅ Submission approved! Sprint progress: {progress}%')
        except ImportError:
            messages.success(request, f'✅ Submission approved! Sprint progress: {progress}%')
        except Exception as e:
            messages.success(request, f'✅ Submission approved! Sprint progress: {progress}%')
    else:
        messages.success(request, f'✅ Submission approved! Sprint progress: {progress}%')
    
    return redirect("review_submissions", sprint.id)



# ============================================
# TALENT - DASHBOARD
# ============================================

@login_required
def talent_dashboard(request):
    """Talent Dashboard - Overview of sprints, applications, and tasks."""
    
    # Get all sprints the talent has applied to
    applications = SprintApplication.objects.filter(
        talent=request.user
    ).select_related('sprint', 'sprint__startup')
    
    # Get all sprints the talent is a member of
    member_sprints = SprintMember.objects.filter(
        user=request.user
    ).select_related('sprint', 'sprint__startup')
    
    # Get all tasks assigned to the talent
    tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('sprint')
    
    # Counts
    total_applications = applications.count()
    pending_applications = applications.filter(status='pending').count()
    accepted_applications = applications.filter(status='accepted').count()
    rejected_applications = applications.filter(status='rejected').count()
    
    total_member_sprints = member_sprints.count()
    
    # Task counts
    pending_tasks = tasks.filter(status='pending').count()
    progress_tasks = tasks.filter(status='progress').count()
    review_tasks = tasks.filter(status='review').count()
    completed_tasks = tasks.filter(status='completed').count()
    total_tasks = tasks.count()
    
    # Get recent applications
    recent_applications = applications.order_by('-applied_at')[:5]
    
    # Get recent tasks
    recent_tasks = tasks.order_by('-created_at')[:5]
    
    # Get reputation score
    try:
        from reputation.models import ReputationScore
        reputation = ReputationScore.objects.get(user=request.user)
    except:
        reputation = None
    
    context = {
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'accepted_applications': accepted_applications,
        'rejected_applications': rejected_applications,
        'total_member_sprints': total_member_sprints,
        'pending_tasks': pending_tasks,
        'progress_tasks': progress_tasks,
        'review_tasks': review_tasks,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'recent_applications': recent_applications,
        'recent_tasks': recent_tasks,
        'reputation': reputation,
        'page_title': 'Talent Dashboard',
        'page_icon': '🏠',
        'page_subtitle': 'Overview of your sprint activities',
    }
    return render(request, 'sprints/talent/talent_dashboard.html', context)