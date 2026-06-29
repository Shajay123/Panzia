"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sales/',include('sales.urls')),
    path('intelligence/',include('intelligence.urls')),
    path('execution/', include('execution.urls')),
    path('analytics/', include('analytics.urls')),
    path('crm/', include('crm.urls')),
    path('operations/', include('operations.urls')),
    path('legal/',include('legal.urls')),
    path('people/', include('people.urls')),
    path('compliance/', include('compliance.urls')),
    path('finance/', include('finance.urls')),
    path('admin-dashboard/', include('adminpanal.urls')),
    path('', include('website.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('offers/', include('offers.urls')),
    path('interviews/', include('interviews.urls')),
    path('ai_engine/',include('ai_engine.urls')),
    path('courses/', include('courses.urls')),
    path('placements/', include('placements.urls')),
    path('webinars/', include('webinars.urls')),
    path('mentors/', include('mentors.urls')),
    path('payments/', include('payments.urls')),
    path('certificates/', include('certificates.urls')),
    path('internships/', include('internships.urls')),
    path('projects/', include('projects.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('sprints/', include('sprints.urls')),
    path('reputation/', include('reputation.urls')),
    path('talents/', include('talents.urls')),
    path('notifications/', include('notifications.urls')),
    path('startups/', include('startups.urls')),
    path('activities/', include('activities.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
