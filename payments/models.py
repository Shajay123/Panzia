from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class SubscriptionPlan(models.Model):

    PLAN_TYPES = (

        ("FREE","FREE"),
        ("PRO","PRO"),
        ("ELITE","ELITE"),

        ("STARTER","STARTER"),
        ("GROWTH","GROWTH"),
        ("SCALE","SCALE"),

    )

    name=models.CharField(
        max_length=50,
        choices=PLAN_TYPES
    )

    price=models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    duration_days=models.IntegerField(
        default=30
    )

    description=models.TextField(
        blank=True
    )

    is_active=models.BooleanField(
        default=True
    )

    features=models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


class UserSubscription(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE
    )

    start_date = models.DateTimeField(
        auto_now_add=True
    )

    end_date = models.DateTimeField()

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.user} - {self.plan}"
    
class SubscriptionHistory(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    plan=models.CharField(
        max_length=50
    )

    amount=models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_id=models.CharField(
        max_length=255
    )

    created_at=models.DateTimeField(
        auto_now_add=True
    )