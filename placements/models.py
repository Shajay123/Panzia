from django.db import models
from django.conf import settings
from startups.models import StartupProfile


class PlacementJob(models.Model):

    JOB_TYPES = (
        ("Internship", "Internship"),
        ("Part Time", "Part Time"),
        ("Full Time", "Full Time"),
        ("Freelance", "Freelance"),
    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    skills = models.TextField()

    location = models.CharField(
        max_length=100,
        blank=True
    )

    salary = models.CharField(
        max_length=100,
        blank=True
    )

    experience_required = models.CharField(
        max_length=100,
        blank=True
    )

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPES
    )

    status = models.CharField(
        max_length=20,
        default="Open"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

class PlacementApplication(models.Model):

    STATUS = (

        ("Applied", "Applied"),
        ("Shortlisted", "Shortlisted"),
        ("Interview", "Interview"),
        ("Hired", "Hired"),
        ("Rejected", "Rejected"),

    )

    job = models.ForeignKey(
        PlacementJob,
        on_delete=models.CASCADE
    )

    talent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    message = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Applied"
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )