from django.urls import path
from . import views



urlpatterns = [

    path(
        "resume-builder/",
        views.resume_builder,
        name="resume_builder"
    ),

    path(
        "resume-preview/",
        views.generate_resume,
        name="generate_resume"
    ),

    path(
        "resume/",
        views.ai_resume,
        name="ai_resume"
    ),

    path(
        "resume/download/",
        views.download_resume,
        name="download_resume"
    ),

    path(
        "resume-pdf/",
        views.download_resume_pdf,
        name="download_resume_pdf"
    ),

    path(
        "recommendations/",
        views.ai_recommendations,
        name="ai_recommendations"
    ),

    path(
        "career-roadmap/",
        views.career_roadmap,
        name="career_roadmap"
    ),
    path(
    "dashboard/",
    views.ai_dashboard,
    name="ai_dashboard"
),


]