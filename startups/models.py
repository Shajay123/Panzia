from django.db import models
from django.conf import settings


class StartupProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    company_name = models.CharField(max_length=255)

    tagline = models.CharField(
    max_length=255,
    blank=True,
    default=""
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    industry = models.CharField(max_length=100)

    description = models.TextField()

    logo = models.ImageField(
        upload_to='startup_logos/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.company_name