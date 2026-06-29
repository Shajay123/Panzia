from django.urls import path
from . import views

urlpatterns = [

    path(
        'leaderboard/',
        views.leaderboard,
        name='leaderboard'
    ),

    # reputation/urls.py

path(
    "review/<int:sprint_id>/<int:talent_id>/",
    views.give_review,
    name="give_review"
),

    path(
    'monthly-rankings/',
    views.monthly_rankings,
    name='monthly_rankings'
    ),

    path(
    'top-builders/',
    views.top_builders,
    name='top_builders'
    ),

]