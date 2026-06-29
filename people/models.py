
from django.db import models
from django.conf import settings
from startups.models import StartupProfile


# ==========================================
# DEPARTMENT
# ==========================================

class Department(models.Model):

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE,
        related_name="departments"
    )

    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=20,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["startup", "name"]

    def __str__(self):
        return self.name


# ==========================================
# EMPLOYEE
# ==========================================

class Employee(models.Model):

    EMPLOYMENT_TYPES = [

        ("Full Time","Full Time"),
        ("Part Time","Part Time"),
        ("Intern","Intern"),
        ("Contract","Contract"),
        ("Freelancer","Freelancer"),

    ]

    EMPLOYEE_STATUS = [

        ("Onboarding","Onboarding"),
        ("Active","Active"),
        ("Probation","Probation"),
        ("Notice Period","Notice Period"),
        ("Exited","Exited"),

    ]

    HIRE_SOURCE = [

        ("Talent Pool","Talent Pool"),
        ("Manual","Manual"),
        ("Transfer","Transfer"),

    ]

    WORK_MODE = [

        ("Office","Office"),
        ("Hybrid","Hybrid"),
        ("Remote","Remote"),

    ]

    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.CASCADE,
        related_name="employees"
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee"
    )

    employee_id = models.CharField(
        max_length=30
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members"
    )

    designation = models.CharField(
        max_length=150
    )

    employment_type = models.CharField(
        max_length=30,
        choices=EMPLOYMENT_TYPES,
        default="Full Time"
    )

    status = models.CharField(
        max_length=30,
        choices=EMPLOYEE_STATUS,
        default="Onboarding"
    )

    hire_source = models.CharField(
        max_length=30,
        choices=HIRE_SOURCE,
        default="Talent Pool"
    )

    work_mode = models.CharField(
        max_length=20,
        choices=WORK_MODE,
        default="Office"
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    emergency_contact = models.CharField(
        max_length=20,
        blank=True
    )

    joining_date = models.DateField()

    confirmation_date = models.DateField(
        null=True,
        blank=True
    )

    probation_end = models.DateField(
        null=True,
        blank=True
    )

    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    profile_image = models.ImageField(
        upload_to="employees/",
        blank=True,
        null=True
    )

    is_payroll_enabled = models.BooleanField(
        default=True
    )

    is_active = models.BooleanField(
        default=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["user__first_name"]
        unique_together = [
            ("startup", "employee_id")
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"




# =====================================

# ATTENDANCE

# =====================================

from datetime import datetime

class Attendance(models.Model):

    STATUS = (

        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Leave", "Leave"),
        ("WFH", "WFH"),

    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    check_out = models.TimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Present"
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        unique_together = ("employee", "date")

    def __str__(self):
        return f"{self.employee} - {self.date}"

    @property
    def working_hours(self):

        if self.check_in and self.check_out:

            start = datetime.combine(
                self.date,
                self.check_in
            )

            end = datetime.combine(
                self.date,
                self.check_out
            )

            diff = end - start

            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60

            return f"{hours}h {minutes}m"

        return "-"
# =====================================

# LEAVE REQUEST

# =====================================

class LeaveRequest(models.Model):


    STATUS = (

        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),

    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    leave_type = models.CharField(
        max_length=100
    )

    from_date = models.DateField()

    to_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"


# =====================================

# PAYROLL

# =====================================

class Payroll(models.Model):


    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    month = models.CharField(
        max_length=20
    )

    year = models.IntegerField()

    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    allowances = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid = models.BooleanField(
        default=False
    )

    paid_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.employee} - {self.month} {self.year}"


# =====================================

# PERFORMANCE REVIEW

# =====================================

class PerformanceReview(models.Model):


    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    rating = models.IntegerField()

    review = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} - {self.rating}"


# =====================================

# EMPLOYEE DOCUMENTS

# =====================================

class EmployeeDocument(models.Model):


    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    file = models.FileField(
        upload_to="employee_documents/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title



class Holiday(models.Model):

    name = models.CharField(
        max_length=200
    )

    date = models.DateField()

    holiday_type = models.CharField(
        max_length=100,
        default="National"
    )

    def __str__(self):
        return self.name
    
class Payslip(models.Model):

    payroll = models.OneToOneField(
        Payroll,
        on_delete=models.CASCADE
    )

    pdf = models.FileField(
        upload_to="payslips/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )