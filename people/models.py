
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


    # Attendance Timing Configuration
    default_check_in = models.TimeField(null=True, blank=True, help_text="Default check-in time")
    default_check_out = models.TimeField(null=True, blank=True, help_text="Default check-out time")
    work_start_time = models.TimeField(null=True, blank=True, help_text="Work start time")
    work_end_time = models.TimeField(null=True, blank=True, help_text="Work end time")
    grace_period_minutes = models.IntegerField(default=15, help_text="Grace period in minutes")
    half_day_hours = models.DecimalField(max_digits=4, decimal_places=2, default=4.00, help_text="Hours for half day")
    full_day_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.00, help_text="Hours for full day")
    
    # Overtime Settings
    overtime_enabled = models.BooleanField(default=False)
    overtime_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.5, help_text="Overtime rate multiplier")
    
    # Shift Information
    shift = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('morning', 'Morning Shift (9:30 AM - 6:30 PM)'),
        ('evening', 'Evening Shift (2:00 PM - 11:00 PM)'),
        ('night', 'Night Shift (10:00 PM - 7:00 AM)'),
        ('flexible', 'Flexible Hours'),
        ('remote', 'Remote Work'),
    ])

    class Meta:
        ordering = ["user__first_name"]
        unique_together = [
            ("startup", "employee_id")
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"



# people/models.py - Add Department Timing Config

class DepartmentTimingConfig(models.Model):
    """Department-level attendance timing configuration"""
    
    department = models.OneToOneField(
        Department,
        on_delete=models.CASCADE,
        related_name='timing_config'
    )
    
    # Timing Settings
    work_start_time = models.TimeField(default='09:30')
    work_end_time = models.TimeField(default='18:30')
    grace_period_minutes = models.IntegerField(default=15)
    half_day_hours = models.DecimalField(max_digits=4, decimal_places=2, default=4.00)
    full_day_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.00)
    
    # Shift Settings
    shift = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('morning', 'Morning Shift (9:30 AM - 6:30 PM)'),
        ('evening', 'Evening Shift (2:00 PM - 11:00 PM)'),
        ('night', 'Night Shift (10:00 PM - 7:00 AM)'),
        ('flexible', 'Flexible Hours'),
        ('remote', 'Remote Work'),
    ])
    
    # Holiday Settings
    weekly_off_days = models.JSONField(default=list, blank=True, help_text="List of weekly off days (0=Monday, 6=Sunday)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.department.name} Timing Config"
# =====================================

# ATTENDANCE

# =====================================

from datetime import datetime

from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

class Attendance(models.Model):

    STATUS = (
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Leave", "Leave"),
        ("WFH", "WFH"),
    )

    CHECK_IN_STATUS = (
        ("early", "Early"),
        ("on_time", "On Time"),
        ("slightly_late", "Slightly Late"),
        ("late", "Late"),
        ("very_late", "Very Late"),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    date = models.DateField(default=timezone.now)

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
        blank=True,
        null=True
    )

    # ============================================
    # NEW FIELDS FOR ENHANCED ATTENDANCE
    # ============================================
    
    photo = models.ImageField(
        upload_to='attendance_photos/',
        blank=True,
        null=True,
        help_text="Attendance verification photo"
    )
    
    location_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Latitude of attendance location"
    )
    
    location_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Longitude of attendance location"
    )
    
    location_address = models.TextField(
        blank=True,
        null=True,
        help_text="Address of attendance location"
    )
    
    check_in_status = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=CHECK_IN_STATUS,
        help_text="Status based on check-in time (Early, On Time, Late, etc.)"
    )
    
    device_info = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Device used to mark attendance"
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the device"
    )
    
    # ============================================
    # TIMING CONFIGURATION (can be overridden)
    # ============================================
    
    work_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Work start time for this specific attendance"
    )
    
    work_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Work end time for this specific attendance"
    )
    
    grace_period_minutes = models.IntegerField(
        default=15,
        help_text="Grace period in minutes"
    )
    
    overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text="Overtime hours worked"
    )
    
    is_overtime = models.BooleanField(
        default=False,
        help_text="Whether this attendance has overtime"
    )
    
    # ============================================
    # META
    # ============================================

    class Meta:
        unique_together = ("employee", "date")
        ordering = ['-date', '-check_in']
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"

    # ============================================
    # PROPERTIES
    # ============================================

    @property
    def working_hours(self):
        """Get working hours as formatted string."""
        if self.check_in and self.check_out:
            start = datetime.combine(self.date, self.check_in)
            end = datetime.combine(self.date, self.check_out)
            
            # Handle overnight shifts (if check_out is earlier than check_in)
            if end < start:
                end += timedelta(days=1)
            
            diff = end - start
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "-"

    # people/models.py - Update working_hours_decimal property

    @property
    def working_hours_decimal(self):
        """Get working hours as decimal (e.g., 8.5 for 8h 30m)."""
        from datetime import datetime
        
        if self.check_in and self.check_out:
            # Convert to time objects if they are strings
            check_in_time = self.check_in
            check_out_time = self.check_out
            
            if isinstance(check_in_time, str):
                try:
                    check_in_time = datetime.strptime(check_in_time, '%H:%M').time()
                except ValueError:
                    try:
                        check_in_time = datetime.strptime(check_in_time, '%H:%M:%S').time()
                    except ValueError:
                        return 0
            
            if isinstance(check_out_time, str):
                try:
                    check_out_time = datetime.strptime(check_out_time, '%H:%M').time()
                except ValueError:
                    try:
                        check_out_time = datetime.strptime(check_out_time, '%H:%M:%S').time()
                    except ValueError:
                        return 0
            
            start = datetime.combine(self.date, check_in_time)
            end = datetime.combine(self.date, check_out_time)
            
            if end < start:
                end += timedelta(days=1)
            
            diff = end - start
            return round(diff.total_seconds() / 3600, 2)
        return 0

    @property
    def is_late(self):
        """Check if employee was late."""
        if not self.check_in:
            return False
        
        work_start = self.work_start_time or datetime.strptime('09:30', '%H:%M').time()
        check_in_time = datetime.combine(self.date, self.check_in)
        work_start_dt = datetime.combine(self.date, work_start)
        
        diff_minutes = (check_in_time - work_start_dt).total_seconds() / 60
        grace = self.grace_period_minutes or 15
        
        return diff_minutes > grace

    @property
    def is_early_checkout(self):
        """Check if employee checked out early."""
        if not self.check_out:
            return False
        
        work_end = self.work_end_time or datetime.strptime('18:30', '%H:%M').time()
        check_out_time = datetime.combine(self.date, self.check_out)
        work_end_dt = datetime.combine(self.date, work_end)
        
        diff_minutes = (work_end_dt - check_out_time).total_seconds() / 60
        return diff_minutes > 0

    @property
    def check_in_status_display(self):
        """Get human-readable check-in status."""
        status_map = {
            'early': '✅ Early',
            'on_time': '✓ On Time',
            'slightly_late': '⚠️ Slightly Late',
            'late': '⚠️ Late',
            'very_late': '❌ Very Late',
        }
        return status_map.get(self.check_in_status, 'Unknown')

    @property
    def has_photo(self):
        """Check if attendance has a photo."""
        return bool(self.photo)

    @property
    def has_location(self):
        """Check if attendance has location data."""
        return bool(self.location_lat and self.location_lng)

    @property
    def duration_minutes(self):
        """Get total duration in minutes."""
        if self.check_in and self.check_out:
            start = datetime.combine(self.date, self.check_in)
            end = datetime.combine(self.date, self.check_out)
            
            if end < start:
                end += timedelta(days=1)
            
            return int((end - start).total_seconds() / 60)
        return 0

    # ============================================
    # METHODS
    # ============================================

    def get_check_in_status(self, work_start=None):
        """
        Determine check-in status based on time.
        Returns: early, on_time, slightly_late, late, very_late
        """
        if not self.check_in:
            return None
        
        work_start_time = work_start or self.work_start_time or datetime.strptime('09:30', '%H:%M').time()
        
        check_in_time = datetime.combine(self.date, self.check_in)
        work_start_dt = datetime.combine(self.date, work_start_time)
        
        diff_minutes = (check_in_time - work_start_dt).total_seconds() / 60
        
        if diff_minutes < -15:  # More than 15 minutes early
            return 'early'
        elif diff_minutes <= 0:  # On time or early within 15 minutes
            return 'on_time'
        elif diff_minutes <= 15:  # 1-15 minutes late
            return 'slightly_late'
        elif diff_minutes <= 30:  # 16-30 minutes late
            return 'late'
        else:  # More than 30 minutes late
            return 'very_late'

    def calculate_overtime(self, work_end=None):
        """Calculate overtime hours if any."""
        if not self.check_in or not self.check_out:
            return 0
        
        work_end_time = work_end or self.work_end_time or datetime.strptime('18:30', '%H:%M').time()
        
        check_out_time = datetime.combine(self.date, self.check_out)
        work_end_dt = datetime.combine(self.date, work_end_time)
        
        # If check_out is after work_end, calculate overtime
        if check_out_time > work_end_dt:
            diff = check_out_time - work_end_dt
            overtime = diff.total_seconds() / 3600
            return round(overtime, 2)
        
        return 0

    def save(self, *args, **kwargs):
        """Override save to auto-calculate fields."""
        
        # Auto-detect check_in_status if check_in is set
        if self.check_in and not self.check_in_status:
            self.check_in_status = self.get_check_in_status()
        
        # Calculate overtime if check_out is set
        if self.check_in and self.check_out:
            overtime = self.calculate_overtime()
            if overtime > 0:
                self.is_overtime = True
                self.overtime_hours = overtime
            else:
                self.is_overtime = False
                self.overtime_hours = 0
        
        super().save(*args, **kwargs)

    def get_working_hours_display(self, format_type='short'):
        """
        Get working hours in different formats.
        
        Args:
            format_type: 'short' (8h 30m), 'long' (8 hours 30 minutes), 
                         'decimal' (8.5), 'minutes' (510)
        """
        if not self.check_in or not self.check_out:
            return '-'
        
        start = datetime.combine(self.date, self.check_in)
        end = datetime.combine(self.date, self.check_out)
        
        if end < start:
            end += timedelta(days=1)
        
        diff = end - start
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if format_type == 'short':
            return f"{hours}h {minutes}m"
        elif format_type == 'long':
            if hours > 0 and minutes > 0:
                return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
            elif hours > 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{minutes} minute{'s' if minutes > 1 else ''}"
        elif format_type == 'decimal':
            return round(hours + minutes / 60, 2)
        elif format_type == 'minutes':
            return hours * 60 + minutes
        else:
            return f"{hours}h {minutes}m"

    def get_location_display(self):
        """Get formatted location display."""
        if self.location_address:
            return self.location_address
        elif self.location_lat and self.location_lng:
            return f"{self.location_lat:.6f}, {self.location_lng:.6f}"
        return "No location"

    def get_photo_url(self):
        """Get photo URL or placeholder."""
        if self.photo:
            return self.photo.url
        return None

    def get_status_color(self):
        """Get color code for status."""
        colors = {
            'Present': '#22c55e',
            'Absent': '#ef4444',
            'WFH': '#3b82f6',
            'Leave': '#f59e0b',
        }
        return colors.get(self.status, '#94a3b8')

    def get_check_in_status_color(self):
        """Get color for check-in status."""
        colors = {
            'early': '#22c55e',
            'on_time': '#3b82f6',
            'slightly_late': '#f59e0b',
            'late': '#f87171',
            'very_late': '#ef4444',
        }
        return colors.get(self.check_in_status, '#94a3b8')

    def is_working_day(self):
        """Check if this is a working day."""
        # Monday=0, Sunday=6
        weekday = self.date.weekday()
        # Saturday (5) and Sunday (6) are weekends
        return weekday < 5

    def get_weekday(self):
        """Get weekday name."""
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return weekdays[self.date.weekday()]
    

# people/models.py - Fix the calculate_overtime method

def calculate_overtime(self, work_end=None):
    """Calculate overtime hours if any."""
    if not self.check_in or not self.check_out:
        return 0
    
    # Convert string to time if needed
    from datetime import datetime, time
    
    check_in_time = self.check_in
    check_out_time = self.check_out
    
    # If they are strings, convert to time objects
    if isinstance(check_in_time, str):
        try:
            check_in_time = datetime.strptime(check_in_time, '%H:%M').time()
        except ValueError:
            try:
                check_in_time = datetime.strptime(check_in_time, '%H:%M:%S').time()
            except ValueError:
                return 0
    
    if isinstance(check_out_time, str):
        try:
            check_out_time = datetime.strptime(check_out_time, '%H:%M').time()
        except ValueError:
            try:
                check_out_time = datetime.strptime(check_out_time, '%H:%M:%S').time()
            except ValueError:
                return 0
    
    # Get work end time
    if work_end:
        if isinstance(work_end, str):
            try:
                work_end = datetime.strptime(work_end, '%H:%M').time()
            except ValueError:
                try:
                    work_end = datetime.strptime(work_end, '%H:%M:%S').time()
                except ValueError:
                    work_end = datetime.strptime('18:30', '%H:%M').time()
    else:
        work_end = self.work_end_time or datetime.strptime('18:30', '%H:%M').time()
        if isinstance(work_end, str):
            try:
                work_end = datetime.strptime(work_end, '%H:%M').time()
            except ValueError:
                try:
                    work_end = datetime.strptime(work_end, '%H:%M:%S').time()
                except ValueError:
                    work_end = datetime.strptime('18:30', '%H:%M').time()
    
    # Calculate overtime
    check_out_dt = datetime.combine(self.date, check_out_time)
    work_end_dt = datetime.combine(self.date, work_end)
    
    if check_out_dt > work_end_dt:
        diff = check_out_dt - work_end_dt
        overtime = diff.total_seconds() / 3600
        return round(overtime, 2)
    
    return 0
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

# models.py - Final version

from django.db import models
from django.utils import timezone


class Payroll(models.Model):
    
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='payrolls'
    )
    month = models.CharField(
        max_length=20,
        choices=MONTH_CHOICES
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
    created_at = models.DateTimeField(
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee} - {self.month} {self.year}"


# =====================================

# PERFORMANCE REVIEW

# =====================================

# models.py - PerformanceReview Model

class PerformanceReview(models.Model):
    RATING_CHOICES = [
        (1, '⭐ 1 - Poor'),
        (2, '⭐⭐ 2 - Below Average'),
        (3, '⭐⭐⭐ 3 - Average'),
        (4, '⭐⭐⭐⭐ 4 - Good'),
        (5, '⭐⭐⭐⭐⭐ 5 - Excellent'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviewed_performances'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES
    )
    review = models.TextField(
        help_text='Detailed performance review'
    )
    strengths = models.TextField(
        blank=True,
        null=True,
        help_text='Key strengths of the employee'
    )
    areas_for_improvement = models.TextField(
        blank=True,
        null=True,
        help_text='Areas where the employee can improve'
    )
    goals = models.TextField(
        blank=True,
        null=True,
        help_text='Goals for the next review period'
    )
    review_period = models.CharField(
        max_length=50,
        choices=[
            ('quarterly', 'Quarterly'),
            ('half_yearly', 'Half Yearly'),
            ('annual', 'Annual'),
            ('project_based', 'Project Based'),
        ],
        default='quarterly'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Performance Review'
        verbose_name_plural = 'Performance Reviews'

    def __str__(self):
        return f"{self.employee} - {self.rating}/5"

    def get_rating_stars(self):
        return '⭐' * self.rating + ('☆' * (5 - self.rating))

    def get_rating_label(self):
        labels = {
            1: 'Poor',
            2: 'Below Average',
            3: 'Average',
            4: 'Good',
            5: 'Excellent'
        }
        return labels.get(self.rating, 'Unknown')

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




# models.py - Simple Holiday model without auto_now_add

class Holiday(models.Model):
    HOLIDAY_TYPES = [
        ('National', '🇮🇳 National Holiday'),
        ('Public', '🏛️ Public Holiday'),
        ('Company', '🏢 Company Holiday'),
        ('Festival', '🎉 Festival'),
        ('Optional', '📅 Optional Holiday'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Name of the holiday'
    )
    date = models.DateField(
        help_text='Date of the holiday'
    )
    holiday_type = models.CharField(
        max_length=100,
        choices=HOLIDAY_TYPES,
        default='National'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Additional details about the holiday'
    )
    is_company_holiday = models.BooleanField(
        default=True,
        help_text='Whether this is a company-wide holiday'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['date']
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%d %b %Y')})"
    
    def is_upcoming(self):
        from django.utils import timezone
        return self.date >= timezone.now().date()
    
    def is_past(self):
        from django.utils import timezone
        return self.date < timezone.now().date()
    
    def get_day_name(self):
        return self.date.strftime('%A')
    
    def get_date_formatted(self):
        return self.date.strftime('%d %B %Y')

# models.py - Complete Payslip Model

class Payslip(models.Model):
    payroll = models.OneToOneField(
        Payroll,
        on_delete=models.CASCADE,
        related_name='payslip'
    )
    pdf = models.FileField(
        upload_to='payslips/',
        blank=True,
        null=True,
        help_text='Generated PDF file'
    )
    html_content = models.TextField(
        blank=True,
        null=True,
        help_text='HTML content for the payslip'
    )
    generated_at = models.DateTimeField(
        auto_now_add=True
    )
    is_generated = models.BooleanField(
        default=False,
        help_text='Whether the payslip has been generated'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the payslip record was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the payslip was last updated'
    )

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Payslip'
        verbose_name_plural = 'Payslips'
        indexes = [
            models.Index(fields=['generated_at']),
            models.Index(fields=['is_generated']),
            models.Index(fields=['payroll']),
        ]

    def __str__(self):
        return f"{self.payroll.employee} - {self.payroll.month} {self.payroll.year}"

    def get_employee_name(self):
        """Get the full name of the employee"""
        return self.payroll.employee.user.get_full_name()

    def get_month_year(self):
        """Get the month and year of the payslip"""
        return f"{self.payroll.month} {self.payroll.year}"

    def get_net_salary(self):
        """Get the net salary amount"""
        return self.payroll.net_salary

    def get_employee_id(self):
        """Get the employee ID"""
        return self.payroll.employee.employee_id

    def get_designation(self):
        """Get the employee's designation"""
        return self.payroll.employee.designation

    def get_department(self):
        """Get the employee's department"""
        return self.payroll.employee.department.name if self.payroll.employee.department else "-"

    def get_basic_salary(self):
        """Get the basic salary"""
        return self.payroll.basic_salary

    def get_allowances(self):
        """Get the allowances"""
        return self.payroll.allowances

    def get_deductions(self):
        """Get the deductions"""
        return self.payroll.deductions

    def get_paid_date(self):
        """Get the paid date"""
        return self.payroll.paid_date

    def is_paid(self):
        """Check if the payroll is paid"""
        return self.payroll.paid

    def get_company_name(self):
        """Get the startup/company name"""
        return self.payroll.employee.startup.company_name if self.payroll.employee.startup else "Company"

    def get_payslip_id(self):
        """Get formatted payslip ID"""
        return f"PS-{self.id:06d}"

    def get_pdf_filename(self):
        """Get the PDF filename"""
        if self.pdf:
            return self.pdf.name.split('/')[-1]
        return None

    def get_pdf_size(self):
        """Get the PDF file size in human readable format"""
        if self.pdf and self.pdf.file:
            size = self.pdf.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
        return None

    def get_generated_time_ago(self):
        """Get time ago for generated_at"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(self.generated_at, timezone.now())

    def get_payslip_data(self):
        """Get all payslip data as a dictionary"""
        return {
            'id': self.id,
            'payslip_id': self.get_payslip_id(),
            'employee_name': self.get_employee_name(),
            'employee_id': self.get_employee_id(),
            'designation': self.get_designation(),
            'department': self.get_department(),
            'month': self.payroll.month,
            'year': self.payroll.year,
            'basic_salary': float(self.get_basic_salary()),
            'allowances': float(self.get_allowances()),
            'deductions': float(self.get_deductions()),
            'net_salary': float(self.get_net_salary()),
            'paid_date': self.get_paid_date(),
            'is_paid': self.is_paid(),
            'is_generated': self.is_generated,
            'generated_at': self.generated_at,
            'company_name': self.get_company_name(),
            'pdf_filename': self.get_pdf_filename(),
            'pdf_size': self.get_pdf_size(),
        }

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Payslip'
        verbose_name_plural = 'Payslips'
        indexes = [
            models.Index(fields=['generated_at']),
            models.Index(fields=['is_generated']),
            models.Index(fields=['payroll']),
        ]




# models.py - Add these models

class ExitRequest(models.Model):
    EXIT_STATUS = [
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    EXIT_REASONS = [
        ('better_opportunity', 'Better Opportunity'),
        ('career_growth', 'Career Growth'),
        ('salary', 'Salary/Package'),
        ('relocation', 'Relocation'),
        ('personal', 'Personal Reasons'),
        ('health', 'Health Issues'),
        ('retirement', 'Retirement'),
        ('other', 'Other'),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='exit_requests'
    )
    resignation_date = models.DateField(
        help_text='Date when resignation was submitted'
    )
    last_working_day = models.DateField(
        help_text='Last working day of the employee'
    )
    reason = models.CharField(
        max_length=50,
        choices=EXIT_REASONS,
        default='other'
    )
    reason_description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed reason for exit'
    )
    status = models.CharField(
        max_length=20,
        choices=EXIT_STATUS,
        default='Pending'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_exits'
    )
    approved_date = models.DateField(
        null=True,
        blank=True
    )
    exit_interview_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date of exit interview'
    )
    exit_interview_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notes from exit interview'
    )
    is_eligible_for_rehire = models.BooleanField(
        default=True,
        help_text='Whether the employee is eligible for rehire'
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        help_text='Employee feedback during exit'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exit Request'
        verbose_name_plural = 'Exit Requests'

    def __str__(self):
        return f"{self.employee} - {self.status}"

    def get_exit_reason_display(self):
        return dict(self.EXIT_REASONS).get(self.reason, self.reason)

    def get_days_remaining(self):
        from django.utils import timezone
        if self.last_working_day >= timezone.now().date():
            return (self.last_working_day - timezone.now().date()).days
        return 0

    def get_notice_period_days(self):
        return (self.last_working_day - self.resignation_date).days