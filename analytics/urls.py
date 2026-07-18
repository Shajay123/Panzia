from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    
    # Daily Snapshot
    path('daily-snapshot/', views.daily_snapshot, name='daily_snapshot'),
    path('daily-snapshot/create/', views.daily_snapshot_create, name='daily_snapshot_create'),
    
    # Weekly Report
    path('weekly-report/', views.weekly_report, name='weekly_report'),
    path('weekly-report/create/', views.weekly_report_create, name='weekly_report_create'),
    
    # Monthly Report
    path('monthly-report/', views.monthly_report, name='monthly_report'),
    path('monthly-report/create/', views.monthly_report_create, name='monthly_report_create'),
    
    # Runway Calculator
    path('runway-calculator/', views.runway_calculator, name='runway_calculator'),
    path('runway-calculator/calculate/', views.runway_calculate, name='runway_calculate'),
    
    # Burn Rate
    path('burn-rate/', views.burn_rate, name='burn_rate'),
    path('burn-rate/create/', views.burn_rate_create, name='burn_rate_create'),
    
    # Investor Reports
    path('investor-reports/', views.investor_reports, name='investor_reports'),
    path('investor-reports/create/', views.investor_report_create, name='investor_report_create'),
    path('investor-reports/<int:pk>/', views.investor_report_detail, name='investor_report_detail'),
    
    # Leaderboard
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('monthly-rankings/', views.monthly_rankings, name='monthly_rankings'),
]