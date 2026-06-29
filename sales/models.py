from django.db import models
from startups.models import StartupProfile

# Create your models here.
class Lead(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20
    )

    company = models.CharField(
        max_length=255,
        blank=True
    )

    source = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=50,
        default="New"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

class Client(models.Model):

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

    active = models.BooleanField(
        default=True
    )

class Deal(models.Model):

    STAGES = (

        ("Lead","Lead"),
        ("Qualified","Qualified"),
        ("Proposal","Proposal"),
        ("Negotiation","Negotiation"),
        ("Won","Won"),
        ("Lost","Lost")

    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    value = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    stage = models.CharField(
        max_length=50,
        choices=STAGES
    )

    expected_close_date = models.DateField()

class Invoice(models.Model):

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )

    invoice_number = models.CharField(
        max_length=100
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    due_date = models.DateField()

    paid = models.BooleanField(
        default=False
    )

class ClientSubscription(models.Model):

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )

    plan_name = models.CharField(
        max_length=255
    )

    monthly_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    renewal_date = models.DateField()

    active = models.BooleanField(
        default=True
    )