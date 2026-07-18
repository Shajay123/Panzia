from django.urls import path
from . import views

app_name = 'startups'

urlpatterns = [
    # Profile Setup
    path('profile/setup/', views.startup_profile_setup, name='startup_profile_setup'),
    
    # Profile Views
    # Current user's profile (no ID needed)
    path('profile/', views.startup_profile_view, name='startup_profile'),
    
    # Specific startup profile by ID (for public viewing)
    path('profile/<int:startup_id>/', views.startup_profile_detail, name='startup_profile_detail'),
    
    # Alternative: If you want the old pattern (startup_id at root)
    # path('<int:startup_id>/', views.startup_profile_detail, name='startup_profile_detail'),
    
    # Public Application
    path('apply/', views.startup_application_create, name='startup_application_create'),
    path('application-success/', views.application_success, name='application_success'),
    path('test-email/', views.test_email, name='test_email'),
    
    # Admin Application Management
    path('admin/applications/', views.admin_applications, name='admin_applications'),
    path('admin/application/<int:app_id>/', views.admin_application_detail, name='admin_application_detail'),
    path('admin/application/<int:app_id>/approve/', views.admin_approve_application, name='admin_approve_application'),
    path('admin/application/<int:app_id>/reject/', views.admin_reject_application, name='admin_reject_application'),
]