from django.shortcuts import render, redirect
from .forms import InterviewForm
from django.contrib.auth.decorators import login_required
from .models import PlacementApplication

# Create your views here.
@login_required
def schedule_interview(request, app_id):

    application = PlacementApplication.objects.get(
        id=app_id
    )

    if request.method == "POST":

        form = InterviewForm(request.POST)

        if form.is_valid():

            interview = form.save(
                commit=False
            )

            interview.application = application

            interview.save()

            application.status = "Interview"

            application.save()

            return redirect(
                "job_applications",
                application.job.id
            )

    else:

        form = InterviewForm()

    return render(

        request,

        "interviews/schedule_interview.html",

        {

            "form": form,

            "application": application

        }

    )