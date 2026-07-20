# sprints/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ============================================
    # STARTUP SIDE (with sidebar)
    # ============================================
    
    # Dashboard
    path('', views.execution_dashboard, name='execution_dashboard'),
    
    # Sprint Management
    path('create/', views.create_sprint, name='create_sprint'),
    path('my-sprints/', views.startup_sprints, name='startup_sprints'),
    path('edit/<int:sprint_id>/', views.edit_sprint, name='edit_sprint'),
    path('delete/<int:sprint_id>/', views.delete_sprint, name='delete_sprint'),
    
    # Sprint Details & Members
    path('detail/<int:sprint_id>/', views.sprint_detail, name='sprint_detail'),
    path('members/<int:sprint_id>/', views.sprint_members, name='sprint_members'),
    
    # Applications
    path('applications/<int:sprint_id>/', views.sprint_applications, name='sprint_applications'),
    path('accept/<int:app_id>/', views.accept_application, name='accept_application'),
    path('reject/<int:app_id>/', views.reject_application, name='reject_application'),
    
    # Tasks (Startup)
    path('tasks/<int:sprint_id>/', views.sprint_tasks, name='sprint_tasks'),
    path('create-task/<int:sprint_id>/', views.create_task, name='create_task'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    
    # Review Submissions (Startup)
    path('review-submissions/<int:sprint_id>/', views.review_submissions, name='review_submissions'),
    path('submission-review/<int:submission_id>/', views.submission_review, name='submission_review'),
    path('approve-submission/<int:submission_id>/', views.approve_submission, name='approve_submission'),
    
    # ============================================
    # TALENT SIDE (no sidebar)
    # ============================================
    
    # Talent Dashboard
    path('talent-dashboard/', views.talent_dashboard, name='talent_dashboard'),  # ✅ NEW
    
    # Browse & Apply
    path('browse/', views.browse_sprints, name='browse_sprints'),
    path('apply/<int:sprint_id>/', views.apply_sprint, name='apply_sprint'),
    
    # My Applications & Tasks
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    
    # Submit Task
    path('submit-task/<int:task_id>/', views.submit_task, name='submit_task'),
]