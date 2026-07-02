from django.db import models
from django.conf import settings





class StartupProfile(models.Model):
    """Startup profile model - Updated with user management"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='startup_profile'
    )

    company_name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True, default="")
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='startup_logos/', blank=True, null=True)
    
    # New fields for user management
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
    
    def get_owner(self):
        """Get the user who owns this startup profile"""
        return self.user
    
    # ... rest of your methods remain the same ...
    
    # ============================================
    # EMPLOYEE MANAGEMENT METHODS
    # ============================================
    
    def get_employees(self):
        """Get all employees of this startup"""
        from people.models import Employee
        return Employee.objects.filter(startup=self)
    
    def get_active_employees(self):
        """Get active employees of this startup"""
        from people.models import Employee
        return Employee.objects.filter(startup=self, is_active=True)
    
    def get_employee_count(self):
        """Get total number of employees"""
        return self.get_employees().count()
    
    def get_active_employee_count(self):
        """Get total number of active employees"""
        return self.get_active_employees().count()
    
    # ============================================
    # USER MANAGEMENT METHODS
    # ============================================
    
    def get_users(self):
        """Get all users associated with this startup"""
        from accounts.models import User
        # Users directly linked to startup
        return User.objects.filter(startup=self)
    
    def get_staff_users(self):
        """Get staff users (admins, HR, managers)"""
        from accounts.models import User
        return User.objects.filter(
            startup=self,
            role__in=['startup_admin', 'startup_hr', 'startup_manager']
        )
    
    def get_admins(self):
        """Get admin users of this startup"""
        from accounts.models import User
        return User.objects.filter(startup=self, role='startup_admin')
    
    def get_hr_users(self):
        """Get HR users of this startup"""
        from accounts.models import User
        return User.objects.filter(startup=self, role='startup_hr')
    
    def get_managers(self):
        """Get manager users of this startup"""
        from accounts.models import User
        return User.objects.filter(startup=self, role='startup_manager')
    
    def get_regular_employees(self):
        """Get regular employees (non-staff) of this startup"""
        from people.models import Employee
        return Employee.objects.filter(startup=self).exclude(
            user__role__in=['startup_admin', 'startup_hr', 'startup_manager']
        )
    
    def has_user(self, user):
        """Check if a user belongs to this startup"""
        return user.startup == self
    
    def is_staff_user(self, user):
        """Check if a user is a staff member of this startup"""
        return user.startup == self and user.role in ['startup_admin', 'startup_hr', 'startup_manager']
    
    def is_admin_user(self, user):
        """Check if a user is an admin of this startup"""
        return user.startup == self and user.role == 'startup_admin'
    
    def is_hr_user(self, user):
        """Check if a user is an HR of this startup"""
        return user.startup == self and user.role == 'startup_hr'
    
    def is_manager_user(self, user):
        """Check if a user is a manager of this startup"""
        return user.startup == self and user.role == 'startup_manager'
    
    # ============================================
    # DEPARTMENT MANAGEMENT
    # ============================================
    
    def get_departments(self):
        """Get all departments of this startup"""
        from people.models import Department
        return Department.objects.filter(startup=self)
    
    def get_department_count(self):
        """Get total number of departments"""
        return self.get_departments().count()
    
    # ============================================
    # LEAVE MANAGEMENT
    # ============================================
    
    def get_leave_requests(self):
        """Get all leave requests of this startup"""
        from people.models import LeaveRequest
        return LeaveRequest.objects.filter(employee__startup=self)
    
    def get_pending_leaves(self):
        """Get pending leave requests"""
        return self.get_leave_requests().filter(status='Pending')
    
    def get_approved_leaves(self):
        """Get approved leave requests"""
        return self.get_leave_requests().filter(status='Approved')
    
    def get_rejected_leaves(self):
        """Get rejected leave requests"""
        return self.get_leave_requests().filter(status='Rejected')
    
    # ============================================
    # PAYROLL MANAGEMENT
    # ============================================
    
    def get_payrolls(self):
        """Get all payroll records of this startup"""
        from people.models import Payroll
        return Payroll.objects.filter(employee__startup=self)
    
    def get_paid_payrolls(self):
        """Get paid payroll records"""
        return self.get_payrolls().filter(paid=True)
    
    def get_pending_payrolls(self):
        """Get pending payroll records"""
        return self.get_payrolls().filter(paid=False)
    
    # ============================================
    # ATTENDANCE MANAGEMENT
    # ============================================
    
    def get_attendance_today(self):
        """Get today's attendance records"""
        from django.utils import timezone
        from people.models import Attendance
        today = timezone.now().date()
        return Attendance.objects.filter(
            employee__startup=self,
            date=today
        )
    
    def get_present_today(self):
        """Get present employees today"""
        return self.get_attendance_today().filter(status='Present').count()
    
    def get_absent_today(self):
        """Get absent employees today"""
        return self.get_attendance_today().filter(status='Absent').count()
    
    def get_wfh_today(self):
        """Get WFH employees today"""
        return self.get_attendance_today().filter(status='WFH').count()
    
    def get_leave_today(self):
        """Get employees on leave today"""
        return self.get_attendance_today().filter(status='Leave').count()
    
    # ============================================
    # DOCUMENT MANAGEMENT
    # ============================================
    
    def get_documents(self):
        """Get all documents of this startup"""
        from people.models import EmployeeDocument
        return EmployeeDocument.objects.filter(employee__startup=self)
    
    def get_document_count(self):
        """Get total number of documents"""
        return self.get_documents().count()
    
    # ============================================
    # PERFORMANCE REVIEWS
    # ============================================
    
    def get_performance_reviews(self):
        """Get all performance reviews of this startup"""
        from people.models import PerformanceReview
        return PerformanceReview.objects.filter(employee__startup=self)
    
    # ============================================
    # EXIT REQUESTS
    # ============================================
    
    def get_exit_requests(self):
        """Get all exit requests of this startup"""
        from people.models import ExitRequest
        return ExitRequest.objects.filter(employee__startup=self)
    
    def get_pending_exits(self):
        """Get pending exit requests"""
        return self.get_exit_requests().filter(status='Pending')
    
    def get_approved_exits(self):
        """Get approved exit requests"""
        return self.get_exit_requests().filter(status='Approved')
    
    def get_completed_exits(self):
        """Get completed exit requests"""
        return self.get_exit_requests().filter(status='Completed')
    
    class Meta:
        ordering = ['company_name']
        verbose_name = 'Startup Profile'
        verbose_name_plural = 'Startup Profiles'