# startups/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import random
import string

User = get_user_model()


class StartupApplication(models.Model):
    """Model for startup registration applications"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    # Company Information
    company_name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True, default="")
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='startup_applications/', blank=True, null=True)
    
    # Contact Information
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Location
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.applicant_email}"
    
    def approve(self, admin_user):
        """Approve this application and create startup profile and user account"""
        from accounts.models import User
        from django.core.mail import send_mail
        from django.conf import settings
        
        print(f"🔄 [DEBUG] Starting approval process for: {self.company_name}")
        
        # Update application status
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        print(f"✅ [DEBUG] Application status updated to 'approved'")
        
        # Check if user already exists with this email FIRST
        existing_user = User.objects.filter(email=self.applicant_email).first()
        
        if existing_user:
            print(f"⚠️ [DEBUG] User already exists: {existing_user.email}")
            
            # Check if startup exists
            existing_startup = StartupProfile.objects.filter(
                company_name__iexact=self.company_name
            ).first()
            
            if existing_startup:
                # Both exist - link them
                existing_user.startup = existing_startup
                existing_user.role = 'startup_admin'
                existing_user.is_approved = True
                existing_user.is_active = True
                existing_user.save()
                print(f"✅ [DEBUG] Linked existing user to existing startup")
                return existing_user, existing_startup
            else:
                # User exists, but startup doesn't - create startup with user
                startup = StartupProfile.objects.create(
                    user=existing_user,  # ✅ Set user immediately
                    company_name=self.company_name,
                    tagline=self.tagline,
                    website=self.website,
                    industry=self.industry,
                    description=self.description,
                    logo=self.logo,
                    address=self.address,
                    city=self.city,
                    state=self.state,
                    country=self.country,
                    is_active=True,
                    is_verified=True,
                )
                existing_user.startup = startup
                existing_user.role = 'startup_admin'
                existing_user.is_approved = True
                existing_user.is_active = True
                existing_user.save()
                print(f"✅ [DEBUG] Created new startup for existing user")
                return existing_user, startup
        
        # Generate a random password
        def generate_password(length=12):
            characters = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(random.choice(characters) for _ in range(length))
        
        # Generate username from email
        username = self.applicant_email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        print(f"👤 [DEBUG] Generated username: {username}")
        
        # Generate a secure password
        raw_password = generate_password()
        print(f"🔐 [DEBUG] Generated password for user")
        
        # Split name into first and last
        name_parts = self.applicant_name.split()
        first_name = name_parts[0] if name_parts else self.applicant_name
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # ============================================
        # CREATE USER FIRST
        # ============================================
        print(f"🔄 [DEBUG] Creating user account...")
        user = User.objects.create(
            username=username,
            email=self.applicant_email,
            password=make_password(raw_password),
            first_name=first_name,
            last_name=last_name,
            role='startup_admin',
            is_approved=True,
            is_active=True
        )
        print(f"✅ [DEBUG] User created: {user.email} (ID: {user.id})")
        
        # ============================================
        # CREATE STARTUP PROFILE WITH USER (FIXED)
        # ============================================
        print(f"🔄 [DEBUG] Creating startup profile with user...")
        startup = StartupProfile.objects.create(
            user=user,  # ✅ Set user immediately - NOT NULL constraint satisfied
            company_name=self.company_name,
            tagline=self.tagline,
            website=self.website,
            industry=self.industry,
            description=self.description,
            logo=self.logo,
            address=self.address,
            city=self.city,
            state=self.state,
            country=self.country,
            is_active=True,
            is_verified=True,
        )
        print(f"✅ [DEBUG] Startup created: {startup.company_name} (ID: {startup.id})")
        
        # Update user's startup field
        user.startup = startup
        user.save()
        print(f"✅ [DEBUG] User linked to startup")
        
        # ============================================
        # SEND APPROVAL EMAIL
        # ============================================
        try:
            print(f"📧 [DEBUG] Sending approval email to {self.applicant_email}")
            send_mail(
                subject=f"🎉 Welcome to PANZIA - {startup.company_name}",
                message=f"""
Dear {self.applicant_name},

🎉 Congratulations! Your startup application has been approved.

Your PANZIA account has been created with the following credentials:

🔑 Username: {username}
🔐 Password: {raw_password}

📌 Please login and change your password immediately.

🔗 Login URL: {settings.SITE_URL}/accounts/login/

🏢 Startup: {startup.company_name}
🏭 Industry: {startup.industry}

If you have any questions, please contact our support team.

Best regards,
🚀 PANZIA Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.applicant_email],
                fail_silently=False,
            )
            print(f"✅ [DEBUG] Approval email sent successfully")
        except Exception as e:
            print(f"❌ [DEBUG] Email sending failed: {e}")
        
        return user, startup
    
    def reject(self, admin_user, reason=None):
        """Reject this application"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        print(f"❌ [DEBUG] Rejecting application: {self.company_name}")
        
        self.status = 'rejected'
        self.rejection_reason = reason
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        print(f"✅ [DEBUG] Application status updated to 'rejected'")
        
        # Send rejection email
        try:
            print(f"📧 [DEBUG] Sending rejection email to {self.applicant_email}")
            send_mail(
                subject=f"PANZIA Startup Application - Update",
                message=f"""
Dear {self.applicant_name},

Thank you for applying to PANZIA. After careful review, we regret to inform you that your application has not been approved at this time.

Reason: {reason or 'Not specified'}

We encourage you to address the feedback and reapply in the future.

If you have any questions, please contact our support team.

Best regards,
PANZIA Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.applicant_email],
                fail_silently=False,
            )
            print(f"✅ [DEBUG] Rejection email sent successfully")
        except Exception as e:
            print(f"❌ [DEBUG] Email sending failed: {e}")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Startup Application'
        verbose_name_plural = 'Startup Applications'


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