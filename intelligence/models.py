from django.db import models

from startups.models import StartupProfile

# Create your models here.
class AIRecommendation(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    category = models.CharField(
        max_length=100
    )

    recommendation = models.TextField()

    priority = models.CharField(
        max_length=20
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )