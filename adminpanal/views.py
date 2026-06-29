from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum

from accounts.models import User
from startups.models import StartupProfile
from talents.models import TalentProfile
from courses.models import Course
from sprints.models import Sprint
from placements.models import PlacementJob
from payments.models import SubscriptionHistory, UserSubscription


@staff_member_required
def admin_dashboard(request):

    total_users = User.objects.count()

    total_startups = StartupProfile.objects.count()

    total_talents = TalentProfile.objects.count()

    total_courses = Course.objects.count()

    total_sprints = Sprint.objects.count()

    total_revenue = SubscriptionHistory.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0

    recent_users = User.objects.order_by(
        "-date_joined"
    )[:10]

    recent_payments = SubscriptionHistory.objects.order_by(
        "-created_at"
    )[:10]

    context = {

        "total_users": total_users,
        "total_startups": total_startups,
        "total_talents": total_talents,
        "total_courses": total_courses,
        "total_sprints": total_sprints,
        "total_revenue": total_revenue,

        "recent_users": recent_users,
        "recent_payments": recent_payments,

    }

    return render(
        request,
        "adminpanel/dashboard.html",
        context
    )



