from django.urls import path
from . import views

urlpatterns = [

    path(
        '<int:user_id>/',
        views.talent_profile,
        name='talent_profile'
    ),

    path(
    "projects/",
    views.my_projects,
    name="my_projects"
),

path(
    "projects/add/",
    views.add_project,
    name="add_project"
),

path(
    "projects/edit/<int:pk>/",
    views.edit_project,
    name="edit_project"
),

path(
    "projects/delete/<int:pk>/",
    views.delete_project,
    name="delete_project"
),

path(
    "portfolio/<int:user_id>/",
    views.portfolio_showcase,
    name="portfolio_showcase"
),

]