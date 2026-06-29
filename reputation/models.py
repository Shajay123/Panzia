from django.db import models
from django.conf import settings

from sprints.models import Sprint

class ReputationScore(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    execution_score = models.IntegerField(default=0)

    reliability_score = models.IntegerField(default=0)

    collaboration_score = models.IntegerField(default=0)

    completed_sprints = models.IntegerField(default=0)

    applications_accepted = models.IntegerField(default=0)

    sprint_completion_rate = models.IntegerField(default=0)

    tasks_completed = models.IntegerField(default=0)

    reviews_received = models.IntegerField(default=0)

    deployment_score = models.IntegerField(default=0)

    overall_score = models.IntegerField(default=0)

    rank_tier = models.CharField(
        max_length=20,
        default='Bronze'
    )

    def __str__(self):
        return self.user.username

class Review(models.Model):

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE
    )

    talent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    feedback = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


from django.db import models
from django.conf import settings

class MonthlyRanking(models.Model):

    month = models.CharField(
        max_length=20
    )

    year = models.IntegerField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    score = models.IntegerField(
        default=0
    )

    rank = models.IntegerField(
        default=0
    )

    class Meta:
        ordering = ['rank']