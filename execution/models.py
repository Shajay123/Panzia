from django.db import models
from django.conf import settings
from sprints.models import Sprint
from startups.models import StartupProfile

# Create your models here.
class Project(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        default="Active"
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

class ExecutionTask(models.Model):

    STATUS = (

        ("Todo","Todo"),
        ("Progress","Progress"),
        ("Review","Review"),
        ("Done","Done")

    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS
    )

    priority = models.CharField(
        max_length=20,
        default="Medium"
    )

    deadline = models.DateField()

class ContributorScore(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    tasks_completed = models.IntegerField(
        default=0
    )

    sprint_completed = models.IntegerField(
        default=0
    )

    reliability_score = models.IntegerField(
        default=0
    )

    productivity_score = models.IntegerField(
        default=0
    )

    total_score = models.IntegerField(
        default=0
    )


class CandidateMatch(models.Model):

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE
    )

    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    score = models.IntegerField()

    generated_at = models.DateTimeField(
        auto_now_add=True
    )