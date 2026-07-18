from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Onboarding
    path('onboarding/', views.onboarding, name='onboarding'),
    
    # Startup Application
    path('apply/', views.startup_application_view, name='startup_application'),
    path('application-success/', views.application_success, name='application_success'),
    
    # Admin - Applications
    path('admin/applications/', views.admin_applications, name='admin_applications'),
    path('admin/applications/<int:app_id>/', views.admin_application_detail, name='admin_application_detail'),
    
    # Admin - Pending Users
    path('admin/pending-users/', views.admin_pending_users, name='admin_pending_users'),
    path('admin/approve-user/<int:user_id>/', views.admin_approve_user, name='admin_approve_user'),
    path('admin/reject-user/<int:user_id>/', views.admin_reject_user, name='admin_reject_user'),
]