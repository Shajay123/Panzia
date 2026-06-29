from django.db import models

from accounts.models import User

# Create your models here.
class Webinar(models.Model):

    title=models.CharField(max_length=200)

    speaker=models.CharField(max_length=200)

    description=models.TextField()

    webinar_date=models.DateTimeField()

    meeting_link=models.URLField()

    thumbnail=models.ImageField(upload_to="webinars")

    seats=models.IntegerField()

    active=models.BooleanField(default=True)

class WebinarRegistration(models.Model):

    webinar=models.ForeignKey(
        Webinar,
        on_delete=models.CASCADE
    )

    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    joined=models.BooleanField(default=False)