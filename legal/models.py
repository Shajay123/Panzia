from django.db import models

from startups.models import StartupProfile

# Create your models here.
class FounderAgreement(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    document = models.FileField(
        upload_to="legal/founders/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class EmploymentContract(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    employee_name = models.CharField(
        max_length=255
    )

    designation = models.CharField(
        max_length=100
    )

    contract_file = models.FileField(
        upload_to="legal/employees/"
    )

    active = models.BooleanField(
        default=True
    )

class NDA(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    party_name = models.CharField(
        max_length=255
    )

    file = models.FileField(
        upload_to="legal/nda/"
    )

    signed = models.BooleanField(
        default=False
    )

class VendorAgreement(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    vendor_name = models.CharField(
        max_length=255
    )

    file = models.FileField(
        upload_to="legal/vendors/"
    )

    active = models.BooleanField(
        default=True
    )

class ClientAgreement(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    client_name = models.CharField(
        max_length=255
    )

    value = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    file = models.FileField(
        upload_to="legal/clients/"
    )

class Trademark(models.Model):

    STATUS = (

        ("Applied","Applied"),
        ("Objection","Objection"),
        ("Registered","Registered")

    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    trademark_name = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS
    )

    application_number = models.CharField(
        max_length=100
    )


class IPAssignment(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    contributor = models.CharField(
        max_length=255
    )

    document = models.FileField(
        upload_to="legal/ip/"
    )

class ShareholderAgreement(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    document = models.FileField(
        upload_to="legal/shareholders/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )