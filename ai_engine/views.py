from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse

from accounts.models import User

from talents.models import PortfolioProject
from certificates.models import Certificate
from reputation.models import ReputationScore, Review
from sprints.models import Activity, SprintMember
from courses.models import Enrollment

from .models import Resume, CareerGoal
from .forms import CareerGoalForm

from .services import (
    generate_resume,
    recommend_courses,
    generate_roadmap
)

from .resume_builder import build_resume_data

from .utils.pdf_generator import (
    build_pdf,
    generate_resume_pdf
)


# ===============================
# RESUME BUILDER PAGE
# ===============================

@login_required
def resume_builder(request):

    projects = PortfolioProject.objects.filter(
        user=request.user
    )

    certificates = Certificate.objects.filter(
        user=request.user
    )

    sprints = SprintMember.objects.filter(
        user=request.user
    )

    return render(
        request,
        "ai_engine/resume_builder.html",
        {
            "projects": projects,
            "certificates": certificates,
            "sprints": sprints
        }
    )


# ===============================
# RESUME PDF DOWNLOAD
# ===============================

@login_required
def download_resume_pdf(request):

    resume_text = generate_resume(
        request
    )

    pdf_path = f"resume_{request.user.id}.pdf"

    build_pdf(
        pdf_path,
        resume_text
    )

    return FileResponse(
        open(pdf_path, "rb"),
        as_attachment=True,
        filename="resume.pdf"
    )


# ===============================
# MODERN RESUME PDF
# ===============================

@login_required
def download_resume(request):

    data = build_resume_data(
        request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="resume.pdf"'

    generate_resume_pdf(
        data,
        response
    )

    return response


# ===============================
# AI COURSE RECOMMENDATIONS
# ===============================

@login_required
def ai_recommendations(request):

    recommendations = recommend_courses(
        request.user
    )

    return render(
        request,
        "ai_engine/recommendations.html",
        {
            "recommendations": recommendations
        }
    )


# ===============================
# GENERATE RESUME PREVIEW
# ===============================

@login_required
def generate_resume(request):

    user = request.user

    projects = PortfolioProject.objects.filter(
        user=user
    )

    certificates = Certificate.objects.filter(
        user=user
    )

    sprints = SprintMember.objects.filter(
        user=user
    )

    reputation = ReputationScore.objects.get(
        user=user
    )

    project_text = ""

    for p in projects:

        project_text += f"""
- {p.title}
({p.project_type})
{p.description}
"""

    certificate_text = ""

    for c in certificates:

        certificate_text += f"""
- {c.course.title}
"""

    sprint_text = ""

    for s in sprints:

        sprint_text += f"""
- {s.sprint.title}
"""

    resume_text = f"""

{user.username}

PANZIA Builder

REPUTATION SCORE:
{reputation.overall_score}

DEPLOYMENT SCORE:
{reputation.deployment_score}

PROJECTS

{project_text}

CERTIFICATIONS

{certificate_text}

SPRINT EXPERIENCE

{sprint_text}

"""

    Resume.objects.create(

        user=user,

        title=f"{user.username} Resume",

        generated_resume=resume_text

    )

    return render(
        request,
        "ai_engine/resume_preview.html",
        {
            "resume": resume_text
        }
    )


# ===============================
# AI RESUME PAGE
# ===============================

@login_required
def ai_resume(request):

    data = build_resume_data(
        request.user
    )

    if not data:
        return HttpResponse(
            "Please complete Talent Profile first."
        )

    return render(
        request,
        "ai_engine/ai_resume.html",
        data
    )



# ===============================
# CAREER ROADMAP
# ===============================

@login_required
def career_roadmap(request):

    goal_obj, created = CareerGoal.objects.get_or_create(

        user=request.user,

        defaults={
            "goal": "AI Engineer"
        }

    )

    if request.method == "POST":

        form = CareerGoalForm(
            request.POST,
            instance=goal_obj
        )

        if form.is_valid():
            form.save()

    else:

        form = CareerGoalForm(
            instance=goal_obj
        )

    roadmap = generate_roadmap(
        goal_obj.goal
    )

    return render(

        request,

        "ai_engine/career_roadmap.html",

        {

            "form": form,

            "roadmap": roadmap,

            "goal": goal_obj

        }

    )


@login_required
def ai_dashboard(request):

    return render(
        request,
        "ai_engine/ai_dashboard.html"
    )