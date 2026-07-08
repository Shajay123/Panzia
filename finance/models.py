from django.db import models
from django.conf import settings

from startups.models import StartupProfile


class Income(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    client = models.CharField(
        max_length=255
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    received_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Expense(models.Model):

    CATEGORY = (

        ("Salary", "Salary"),
        ("Software", "Software"),
        ("Marketing", "Marketing"),
        ("Office", "Office"),
        ("Travel", "Travel"),
        ("Other", "Other")

    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    expense_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Invoice(models.Model):

    STATUS = (

        ("Draft", "Draft"),
        ("Sent", "Sent"),
        ("Paid", "Paid"),
        ("Overdue", "Overdue")

    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    invoice_number = models.CharField(
        max_length=100,
        unique=True
    )

    client_name = models.CharField(
        max_length=255
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.invoice_number


class Receivable(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )

    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.invoice.invoice_number


class Vendor(models.Model):

    startup = models.ForeignKey(
    StartupProfile,
    on_delete=models.CASCADE,
    related_name="vendors"
)

    vendor_name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField()

    def __str__(self):
        return self.vendor_name


class AccountsPayable(models.Model):

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    due_date = models.DateField()

    paid = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.vendor.vendor_name} - ₹{self.amount}"


class Reimbursement(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reason = models.CharField(
        max_length=255
    )

    approved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee.username} - ₹{self.amount}"