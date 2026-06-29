from django.db import models
from django.conf import settings
from startups.models import StartupProfile

# Create your models here.
class Asset(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    asset_name = models.CharField(
        max_length=255
    )

    asset_type = models.CharField(
        max_length=100
    )

    serial_number = models.CharField(
        max_length=255
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    purchase_date = models.DateField()

    status = models.CharField(
        max_length=50,
        default="Active"
    )

class Vendor(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    company_name = models.CharField(
        max_length=255
    )

    contact_person = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20
    )

    category = models.CharField(
        max_length=100
    )


class SOP(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    department = models.CharField(
        max_length=100
    )

    content = models.TextField()

    version = models.CharField(
        max_length=20,
        default="1.0"
    )


class Meeting(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    meeting_date = models.DateTimeField()

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL
    )

    notes = models.TextField()

class WikiPage(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

class CompanyDocument(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    file = models.FileField(
        upload_to="documents/"
    )

    category = models.CharField(
        max_length=100
    )


class Approval(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    status = models.CharField(
        max_length=50,
        default="Pending"
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )