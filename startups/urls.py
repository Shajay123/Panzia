from django.urls import path
from . import views

urlpatterns = [

    path(
        'profile/setup/',
        views.startup_profile_setup,
        name='startup_profile_setup'
    ),

    path(
        '<int:startup_id>/',
        views.startup_profile,
        name='startup_profile'
    ),

]