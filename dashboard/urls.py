from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('startup/', views.startup_dashboard, name='startup_dashboard'),
    path('talent/', views.talent_dashboard, name='talent_dashboard'),   
]