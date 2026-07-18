from django.urls import path
from . import views

urlpatterns = [
    # ============================================
    # JOB CRUD
    # ============================================
    path("create-job/", views.create_job, name="create_job"),
    path("edit-job/<int:job_id>/", views.edit_job, name="edit_job"),
    path("delete-job/<int:job_id>/", views.delete_job, name="delete_job"),
    path("startup-jobs/", views.startup_jobs, name="startup_jobs"),
    
    # ============================================
    # TALENT - BROWSE & APPLY
    # ============================================
    path("browse-jobs/", views.browse_jobs, name="browse_jobs"),
    path("apply-job/<int:job_id>/", views.apply_job, name="apply_job"),
    path("my-applications/", views.my_job_applications, name="my_job_applications"),
    
    # ============================================
    # STARTUP - APPLICATION MANAGEMENT
    # ============================================
    path("job-applications/<int:job_id>/", views.job_applications, name="job_applications"),
    path("shortlist/<int:app_id>/", views.shortlist_application, name="shortlist_application"),
    path("interview/<int:app_id>/", views.interview_application, name="interview_application"),
    path("hire/<int:app_id>/", views.hire_application, name="hire_application"),
    path("reject/<int:app_id>/", views.reject_application, name="reject_application"),
    
    # ============================================
    # DASHBOARD
    # ============================================
    path("dashboard/", views.hiring_dashboard, name="hiring_dashboard"),
    
    # ============================================
    # AI RECOMMENDATIONS
    # ============================================
    path("recommended/<int:job_id>/", views.recommended_candidates, name="recommended_candidates"),
]