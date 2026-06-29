from django.db import models
from startups.models import StartupProfile

# Create your models here.
class BankAccount(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    bank_name = models.CharField(
        max_length=255
    )

    account_number = models.CharField(
        max_length=50
    )

    ifsc = models.CharField(
        max_length=20
    )

    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    active = models.BooleanField(
        default=True
    )


class Transaction(models.Model):

    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=20
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    description = models.TextField()

    transaction_date = models.DateTimeField()

    reference_number = models.CharField(
        max_length=255
    )

class VendorPayment(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    vendor_name = models.CharField(
        max_length=255
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    due_date = models.DateField()

    paid = models.BooleanField(
        default=False
    )


class ExpenseCard(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    card_holder = models.CharField(
        max_length=255
    )

    spending_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    active = models.BooleanField(
        default=True
    )

class InternationalPayment(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    beneficiary = models.CharField(
        max_length=255
    )

    country = models.CharField(
        max_length=100
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=10
    )

    status = models.CharField(
        max_length=50
    )