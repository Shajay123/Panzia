from django.shortcuts import render, get_object_or_404
from .models import PortfolioProject
from .forms import PortfolioProjectForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from accounts.models import User

from reputation.models import (
    ReputationScore,
    Review
)

from sprints.models import (
    Activity,
    SprintMember,
    Sprint
)
from courses.models import Enrollment
from certificates.models import Certificate
from .models import PortfolioProject

def talent_profile(request, user_id):

    talent = get_object_or_404(
        User,
        id=user_id
    )

    reputation, created = ReputationScore.objects.get_or_create(
        user=talent
    )

    completed_sprints = SprintMember.objects.filter(
        user=talent
    ).count()

    sprint_memberships = SprintMember.objects.filter(
        user=talent
    ).select_related(
        'sprint'
    ).order_by(
        '-joined_at'
    )

    reviews = Review.objects.filter(
        talent=talent
    ).order_by(
        '-created_at'
    )

    activities = Activity.objects.filter(
        user=talent
    ).order_by(
        '-created_at'
    )[:20]


    enrollments = Enrollment.objects.filter(
        user=talent
    ).select_related(
        "course"
    )

    certificates = Certificate.objects.filter(
        user=talent
    ).select_related(
        'course'
    )

    portfolio_projects = PortfolioProject.objects.filter(
        user=talent
    ).order_by("-created_at")

    

    context = {

        'talent': talent,

        'reputation': reputation,

        'completed_sprints': completed_sprints,

        'reviews': reviews,

        'activities': activities,

        'sprint_memberships': sprint_memberships,

        'enrollments': enrollments,

        'certificates': certificates,

        'portfolio_projects': portfolio_projects,

    }

    return render(
        request,
        'talents/profile.html',
        context
    )




@login_required
def my_projects(request):

    projects = PortfolioProject.objects.filter(
        user=request.user
    ).order_by("-created_at")

    # Create skill_list for template
    for project in projects:
        project.skill_list = [
            skill.strip()
            for skill in (project.skills or "").split(",")
            if skill.strip()
        ]

    return render(
        request,
        "talents/my_projects.html",
        {
            "projects": projects
        }
    )



@login_required
def add_project(request):

    form = PortfolioProjectForm(
        request.POST or None,
        request.FILES or None
    )

    if form.is_valid():

        project = form.save(
            commit=False
        )

        project.user = request.user

        project.save()

        return redirect(
            "my_projects"
        )

    return render(
        request,
        "talents/add_project.html",
        {
            "form": form
        }
    )



@login_required
def edit_project(
    request,
    pk
):

    project = get_object_or_404(
        PortfolioProject,
        id=pk,
        user=request.user
    )

    form = PortfolioProjectForm(
        request.POST or None,
        request.FILES or None,
        instance=project
    )

    if form.is_valid():

        form.save()

        return redirect(
            "my_projects"
        )

    return render(
        request,
        "talents/add_project.html",
        {
            "form": form
        }
    )


@login_required
def delete_project(
    request,
    pk
):

    project = get_object_or_404(
        PortfolioProject,
        id=pk,
        user=request.user
    )

    project.delete()

    return redirect(
        "my_projects"
    )


from reputation.models import ReputationScore, Review
from certificates.models import Certificate
from sprints.models import SprintMember


def portfolio_showcase(request, user_id):

    talent = get_object_or_404(
        User,
        id=user_id
    )

    projects = PortfolioProject.objects.filter(
        user=talent
    ).order_by("-created_at")

    for project in projects:
        project.skill_list = [
            skill.strip()
            for skill in project.skills.split(",")
            if skill.strip()
        ]

    reputation, created = ReputationScore.objects.get_or_create(
        user=talent
    )

    certificates = Certificate.objects.filter(
        user=talent
    )

    reviews = Review.objects.filter(
        talent=talent
    )[:5]

    completed_sprints = SprintMember.objects.filter(
        user=talent
    ).count()

    return render(
        request,
        "talents/portfolio_showcase.html",
        {
            "talent": talent,
            "projects": projects,
            "reputation": reputation,
            "certificates": certificates,
            "reviews": reviews,
            "completed_sprints": completed_sprints,
        }
    )