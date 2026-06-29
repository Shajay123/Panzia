from django.db import models
from django.conf import settings

from sprints.models import Skill




class TalentProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    headline = models.CharField(
        max_length=255
    )

    bio = models.TextField()

    # skills = models.ManyToManyField(
    #     Skill,
    #     blank=True
    # )

    skills = models.CharField(
        max_length=300,
        blank=True
    )
    
    github = models.URLField(
        blank=True,
        null=True
    )

    linkedin = models.URLField(
        blank=True,
        null=True
    )

    portfolio = models.URLField(
        blank=True,
        null=True
    )

    profile_image = models.ImageField(
        upload_to='talents/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username
    


from django.db import models
from django.conf import settings


class PortfolioProject(models.Model):

    PROJECT_TYPES = (
        ("Sprint", "Sprint"),
        ("Personal", "Personal"),
        ("Freelance", "Freelance"),
        ("Startup", "Startup"),
        ("OpenSource", "Open Source"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    title = models.CharField(max_length=200)

    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPES,
        blank=True,
        null=True
    )

    description = models.TextField()

    skills = models.CharField(
        max_length=300,
        blank=True
    )

    project_url = models.URLField(
    blank=True,
    null=True
    )

    github_url = models.URLField(
    blank=True,
    null=True
    )

    image = models.ImageField(
        upload_to="portfolio/",
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    sprint_id = models.IntegerField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title