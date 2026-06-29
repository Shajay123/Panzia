from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from placements.models import PlacementApplication


class Interview(models.Model):

    STATUS_CHOICES = (

        ("Scheduled","Scheduled"),
        ("Completed","Completed"),
        ("Cancelled","Cancelled")

    )

    application = models.OneToOneField(
        PlacementApplication,
        on_delete=models.CASCADE
    )

    interview_date = models.DateTimeField()

    meeting_link = models.URLField()

    notes = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Scheduled"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.application.talent.username