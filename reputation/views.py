from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from sprints.utils import create_activity
from sprints.models import Sprint, Submission, Task
from .forms import ReviewForm
from .models import Review, ReputationScore

from sprints.models import Sprint


# ==========================
# LEADERBOARD
# ==========================

def leaderboard(request):

    rankings = ReputationScore.objects.select_related(
        "user"
    ).order_by(
        "-deployment_score",
        "-overall_score"
    )[:100]

    return render(
        request,
        "reputation/leaderboard.html",
        {
            "rankings": rankings
        }
    )


# ==========================
# GIVE REVIEW
# ==========================

@login_required
def give_review(request, sprint_id, talent_id):

    sprint = Sprint.objects.get(
        id=sprint_id
    )

    members = sprint.members.all()

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.sprint = sprint
            review.talent_id = talent_id
            review.reviewer = request.user

            review.save()

            update_reputation(review.talent)
            calculate_deployment_score(review.talent)

            return redirect(
                "sprint_detail",
                sprint.id
            )

    else:
        form = ReviewForm()

    return render(
        request,
        "reputation/give_review.html",
        {
            "form": form,
            "members": members
        }
    )


# ==========================
# AUTO CALCULATE REPUTATION
# ==========================

def update_reputation(user):

    reviews = Review.objects.filter(
        talent=user
    )

    count = reviews.count()

    if count == 0:
        return

    total_rating = sum(
        review.rating
        for review in reviews
    )

    avg_rating = total_rating / count

    reputation, created = ReputationScore.objects.get_or_create(
        user=user
    )

    overall_score = int(
        avg_rating * 20
    )

    reputation.overall_score = overall_score

    if overall_score >= 90:
        reputation.rank_tier = 'Gold'

    elif overall_score >= 70:
        reputation.rank_tier = 'Silver'

    else:
        reputation.rank_tier = 'Bronze'

    reputation.completed_sprints = count

    reputation.execution_score = overall_score
    reputation.reliability_score = overall_score
    reputation.collaboration_score = overall_score

    reputation.save()


def calculate_deployment_score(user):

    reputation = ReputationScore.objects.get(
        user=user
    )

    score = (
        reputation.completed_sprints * 10
        + reputation.tasks_completed * 5
        + reputation.reviews_received * 3
        + reputation.applications_accepted * 2
        + reputation.overall_score
    )

    reputation.deployment_score = score

    reputation.save()





from .models import MonthlyRanking

def monthly_rankings(request):

    rankings = MonthlyRanking.objects.order_by(
        '-score'
    )

    return render(
        request,
        'reputation/monthly_rankings.html',
        {
            'rankings': rankings
        }
    )


from reputation.models import ReputationScore

def top_builders(request):

    builders = ReputationScore.objects.select_related(
        'user'
    ).order_by(
        '-deployment_score'
    )[:100]

    return render(
        request,
        'reputation/top_builders.html',
        {
            'builders': builders
        }
    )