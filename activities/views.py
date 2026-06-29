from django.shortcuts import render

from sprints.models import Activity


def activity_feed(request):

    activities = Activity.objects.select_related(
        'user'
    ).order_by(
        '-created_at'
    )[:100]

    return render(
        request,
        'activities/feed.html',
        {
            'activities': activities
        }
    )