# startups/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import StartupProfile, StartupApplication

User = get_user_model()


@admin.register(StartupProfile)
class StartupProfileAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "user",
        "industry",
        "employee_count",
        "is_active",
        "is_verified",
        "logo_preview",
    )
    list_filter = ("is_active", "is_verified", "industry")
    search_fields = ("company_name", "user__username", "user__email", "industry")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Company Information", {
            "fields": ("company_name", "tagline", "description", "logo")
        }),
        ("Contact & Location", {
            "fields": ("website", "address", "city", "state", "country")
        }),
        ("Industry & Size", {
            "fields": ("industry",)
        }),
        ("Status", {
            "fields": ("is_active", "is_verified")
        }),
        ("Owner", {
            "fields": ("user",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 0.5rem;" />',
                obj.logo.url
            )
        return "-"
    logo_preview.short_description = "Logo"

    def employee_count(self, obj):
        from people.models import Employee
        return Employee.objects.filter(startup=obj).count()
    employee_count.short_description = "Employees"

    def get_employees(self, obj):
        from people.models import Employee
        employees = Employee.objects.filter(startup=obj)
        if employees.exists():
            return format_html(
                '<ul style="margin: 0; padding-left: 1rem;">' +
                ''.join([f'<li>{emp.user.get_full_name()} ({emp.employee_id})</li>' for emp in employees[:5]]) +
                ('<li>...</li>' if employees.count() > 5 else '') +
                '</ul>'
            )
        return "No employees"
    get_employees.short_description = "Employees List"


@admin.register(StartupApplication)
class StartupApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for Startup Application"""
    
    list_display = (
        "company_name",
        "applicant_name",
        "applicant_email",
        "industry",
        "status",
        "created_at",
    )
    list_filter = ("status", "industry", "created_at", "country")
    search_fields = (
        "company_name", 
        "applicant_name", 
        "applicant_email", 
        "industry",
        "description"
    )
    readonly_fields = (
        "created_at", 
        "updated_at", 
        "reviewed_at",
    )
    
    fieldsets = (
        ("Company Information", {
            "fields": ("company_name", "tagline", "industry", "description", "logo")
        }),
        ("Contact & Location", {
            "fields": ("website", "address", "city", "state", "country")
        }),
        ("Applicant Details", {
            "fields": ("applicant_name", "applicant_email", "applicant_phone")
        }),
        ("Application Status", {
            "fields": ("status", "rejection_reason", "reviewed_at", "reviewed_by")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly after approval/rejection"""
        if obj and obj.status != 'pending':
            return self.readonly_fields + ('status', 'rejection_reason')
        return self.readonly_fields

    def approve_application(self, request, queryset):
        """Bulk approve selected applications"""
        approved_count = 0
        error_count = 0
        
        for application in queryset:
            if application.status == 'pending':
                try:
                    user, startup = application.approve(request.user)
                    approved_count += 1
                except Exception as e:
                    error_count += 1
                    self.message_user(
                        request, 
                        f"Error approving {application.company_name}: {str(e)}", 
                        level='ERROR'
                    )
        
        if approved_count > 0:
            self.message_user(
                request, 
                f"✅ Successfully approved {approved_count} application(s)."
            )
        if error_count > 0:
            self.message_user(
                request, 
                f"❌ Failed to approve {error_count} application(s).", 
                level='WARNING'
            )
    approve_application.short_description = "✅ Approve selected applications"

    def reject_application(self, request, queryset):
        """Bulk reject selected applications"""
        for application in queryset:
            if application.status == 'pending':
                application.reject(request.user, "Rejected by admin")
        self.message_user(
            request, 
            f"Successfully rejected {queryset.count()} application(s)."
        )
    reject_application.short_description = "❌ Reject selected applications"

    actions = ['approve_application', 'reject_application']

    def get_actions(self, request):
        """Customize actions based on user permissions"""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop('approve_application', None)
            actions.pop('reject_application', None)
        return actions

    def save_model(self, request, obj, form, change):
        """Override save to track review status"""
        if obj.status != 'pending' and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)