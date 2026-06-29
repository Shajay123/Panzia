from django.db import models
from startups.models import StartupProfile

class GSTFiling(models.Model):


    RETURN_TYPE = (
        ("GSTR1", "GSTR1"),
        ("GSTR3B", "GSTR3B"),
    )

    STATUS = (
        ("Pending", "Pending"),
        ("Filed", "Filed"),
        ("Overdue", "Overdue"),
    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    month = models.CharField(max_length=20)

    year = models.IntegerField()

    return_type = models.CharField(
        max_length=20,
        choices=RETURN_TYPE
    )

    turnover = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    tax_payable = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    due_date = models.DateField()

    filed = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    filing_document = models.FileField(
        upload_to="compliance/gst/",
        blank=True,
        null=True
    )

    filed_date = models.DateField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.return_type} - {self.month} {self.year}"

class TDSFiling(models.Model):

  
    STATUS = (
        ("Pending", "Pending"),
        ("Filed", "Filed"),
        ("Overdue", "Overdue"),
    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    quarter = models.CharField(
        max_length=20
    )

    year = models.IntegerField()

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    filed = models.BooleanField(
        default=False
    )

    filing_document = models.FileField(
        upload_to="compliance/tds/",
        blank=True,
        null=True
    )

    filed_date = models.DateField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"TDS {self.quarter}-{self.year}"


class PFContribution(models.Model):


    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    month = models.CharField(
        max_length=20
    )

    employee_count = models.IntegerField(
        default=0
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    due_date = models.DateField()

    paid = models.BooleanField(
        default=False
    )

    payment_date = models.DateField(
        blank=True,
        null=True
    )

    challan = models.FileField(
        upload_to="compliance/pf/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"PF {self.month}"


class ESICContribution(models.Model):


    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    month = models.CharField(
        max_length=20
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    due_date = models.DateField()

    paid = models.BooleanField(
        default=False
    )

    payment_date = models.DateField(
        blank=True,
        null=True
    )

    challan = models.FileField(
        upload_to="compliance/esic/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"ESIC {self.month}"


class MCAFiling(models.Model):


    STATUS = (
        ("Pending", "Pending"),
        ("Filed", "Filed"),
    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    filing_name = models.CharField(
        max_length=255
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    filing_document = models.FileField(
        upload_to="compliance/mca/",
        blank=True,
        null=True
    )

    filed = models.BooleanField(
        default=False
    )

    filed_date = models.DateField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.filing_name


class IncomeTaxFiling(models.Model):


    STATUS = (
        ("Pending", "Pending"),
        ("Filed", "Filed"),
    )

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    assessment_year = models.CharField(
        max_length=20
    )

    taxable_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    filed = models.BooleanField(
        default=False
    )

    filing_document = models.FileField(
        upload_to="compliance/income_tax/",
        blank=True,
        null=True
    )

    filed_date = models.DateField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.assessment_year


class ComplianceReminder(models.Model):


    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    due_date = models.DateField()

    completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

