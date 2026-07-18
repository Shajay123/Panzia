from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),      # Overall platform admin
        ('startup_admin', 'Startup Admin'),  # Admin of a specific startup
        ('startup_hr', 'Startup HR'),        # HR of a specific startup
        ('startup_manager', 'Startup Manager'), # Manager of a specific startup
        ('employee', 'Employee'),            # Regular employee
        ('talent', 'Talent'),                # Talent pool candidate
        ('pending', 'Pending Approval'),     # Pending approval from admin
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='talent'
    )
    
    # Link user to a specific startup (for employees, HR, managers, admins)
    startup = models.ForeignKey(
        'startups.StartupProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Approval fields
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_users'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_super_admin(self):
        return self.role == 'super_admin' or self.is_superuser
    
    def is_startup_admin(self):
        return self.role == 'startup_admin'
    
    def is_startup_hr(self):
        return self.role == 'startup_hr'
    
    def is_startup_manager(self):
        return self.role == 'startup_manager'
    
    def is_employee(self):
        return self.role == 'employee'
    
    def is_talent(self):
        return self.role == 'talent'
    
    def is_pending(self):
        return self.role == 'pending'
    
    def get_startup(self):
        """Get the startup associated with this user"""
        return self.startup
    
    def get_startup_profile(self):
        """Get the startup profile (OneToOne) associated with this user"""
        if hasattr(self, 'startup_profile'):
            return self.startup_profile
        return None
    
    def has_startup_access(self, startup):
        if self.is_super_admin():
            return True
        if self.startup and self.startup == startup:
            return True
        return False
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def approve(self, admin_user, role='startup_admin'):
        """Approve a pending user"""
        self.is_approved = True
        self.approved_at = timezone.now()
        self.approved_by = admin_user
        self.role = role
        self.is_active = True
        self.save()
    
    def reject(self, reason=None):
        """Reject a pending user"""
        self.is_approved = False
        self.rejection_reason = reason
        self.role = 'talent'  # Reset role
        self.is_active = False
        self.save()
    
    def get_dashboard_url(self):
        """Get the appropriate dashboard URL based on role"""
        if self.is_superuser or self.role == 'super_admin':
            return '/admin-dashboard/'
        elif self.role in ['startup_admin', 'startup_hr', 'startup_manager']:
            return '/people/dashboard/'
        elif self.role == 'employee':
            return '/dashboard/employee/'
        else:
            return '/'
    
    class Meta:
        ordering = ['-created_at']