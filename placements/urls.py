from django.urls import path
from . import views

urlpatterns = [

    path(
        "create-job/",
        views.create_job,
        name="create_job"
    ),

    path(
        "startup-jobs/",
        views.startup_jobs,
        name="startup_jobs"
    ),

    path(
        "browse-jobs/",
        views.browse_jobs,
        name="browse_jobs"
    ),

    path(
        "apply-job/<int:job_id>/",
        views.apply_job,
        name="apply_job"
    ),

    path(
        "my-applications/",
        views.my_job_applications,
        name="my_job_applications"
    ),

    path(
        "job-applications/<int:job_id>/",
        views.job_applications,
        name="job_applications"
    ),

    path(
        "shortlist/<int:app_id>/",
        views.shortlist_application,
        name="shortlist_application"
    ),

    path(
        "interview/<int:app_id>/",
        views.interview_application,
        name="interview_application"
    ),

    path(
        "hire/<int:app_id>/",
        views.hire_application,
        name="hire_application"
    ),

    path(
        "dashboard/",
        views.hiring_dashboard,
        name="hiring_dashboard"
    ),

    path(
        "recommended/<int:job_id>/",
        views.recommended_candidates,
        name="recommended_candidates"
    ),

]