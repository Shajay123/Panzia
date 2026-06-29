
from django.db import models
from django.conf import settings

class Event(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title=models.CharField(max_length=255)

    description=models.TextField(blank=True)

    start_date=models.DateTimeField()

    end_date=models.DateTimeField()

    reminder=models.BooleanField(default=True)

    event_type=models.CharField(
        max_length=100,
        default="General"
    )

    created_at=models.DateTimeField(auto_now_add=True)


