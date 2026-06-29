from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('startup', 'Startup'),
        ('talent', 'Talent'),
    )

    role = models.CharField(
    max_length=20,
    choices=ROLE_CHOICES,
    blank=True,
    null=True
)

    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    bio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username