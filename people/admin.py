# people/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import (
    Department,
    Employee,
    Attendance,
    LeaveRequest,
    Payroll,
    PerformanceReview,
    EmployeeDocument,
    Holiday,
    Payslip,
    ExitRequest
)

User = get_user_model()


# ==========================================
# Department Admin
# ==========================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "startup",
        "code",
        "employee_count",
        "created_at",
    )
    list_filter = ("startup",)
    search_fields = ("name", "code", "startup__company_name")
    readonly_fields = ("created_at",)

    def employee_count(self, obj):
        return obj.employee_set.count()
    employee_count.short_description = "Employees"


# ==========================================
# Employee Admin
# ==========================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "user",
        "startup",
        "department",
        "designation",
        "status",
        "is_active",
        "profile_image_preview",
    )
    list_filter = (
        "startup",
        "department",
        "status",
        "employment_type",
        "work_mode",
        "is_active",
    )
    search_fields = (
        "employee_id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "designation",
        "phone",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user", "manager")
    autocomplete_fields = ("department",)

    fieldsets = (
        ("Basic Information", {
            "fields": ("startup", "user", "employee_id", "department", "manager")
        }),
        ("Employment", {
            "fields": ("designation", "employment_type", "status", "hire_source", "work_mode")
        }),
        ("Dates", {
            "fields": ("joining_date", "confirmation_date", "probation_end")
        }),
        ("Contact", {
            "fields": ("phone", "emergency_contact")
        }),
        ("Payroll", {
            "fields": ("salary", "is_payroll_enabled")
        }),
        ("Other", {
            "fields": ("profile_image", "notes", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_image.url
            )
        return "-"
    profile_image_preview.short_description = "Photo"


# ==========================================
# Attendance Admin
# ==========================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "status",
        "check_in",
        "check_out",
        "working_hours_display",
    )
    list_filter = ("status", "date")
    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )
    date_hierarchy = "date"
    raw_id_fields = ("employee",)

    def working_hours_display(self, obj):
        return obj.working_hours
    working_hours_display.short_description = "Working Hours"


# ==========================================
# Leave Request Admin
# ==========================================

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "from_date",
        "to_date",
        "status",
        "approved_by",
    )
    list_filter = ("status", "leave_type")
    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )
    raw_id_fields = ("employee", "approved_by")
    readonly_fields = ("created_at",)

    actions = ["approve_selected", "reject_selected"]

    def approve_selected(self, request, queryset):
        updated = queryset.update(status="Approved")
        self.message_user(request, f"{updated} leave requests approved.")
    approve_selected.short_description = "Approve selected leave requests"

    def reject_selected(self, request, queryset):
        updated = queryset.update(status="Rejected")
        self.message_user(request, f"{updated} leave requests rejected.")
    reject_selected.short_description = "Reject selected leave requests"


# ==========================================
# Payroll Admin
# ==========================================

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "month",
        "year",
        "basic_salary",
        "net_salary",
        "paid",
        "paid_date",
    )
    list_filter = ("paid", "month", "year")
    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
    )
    raw_id_fields = ("employee",)
    readonly_fields = ("created_at", "updated_at")


# ==========================================
# Payslip Admin
# ==========================================

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payroll",
        "employee_name",
        "month_year",
        "net_salary",
        "is_generated",
        "generated_at",
    )
    list_filter = ("is_generated", "generated_at")
    search_fields = (
        "payroll__employee__employee_id",
        "payroll__employee__user__first_name",
        "payroll__employee__user__last_name",
    )
    raw_id_fields = ("payroll",)
    readonly_fields = ("generated_at", "html_content")

    def employee_name(self, obj):
        return obj.get_employee_name()
    employee_name.short_description = "Employee"

    def month_year(self, obj):
        return obj.get_month_year()
    month_year.short_description = "Month/Year"

    def net_salary(self, obj):
        return f"₹{obj.get_net_salary():,.2f}"
    net_salary.short_description = "Net Salary"


# ==========================================
# Performance Review Admin
# ==========================================

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "reviewer",
        "rating",
        "rating_stars",
        "review_period",
        "created_at",
    )
    list_filter = ("rating", "review_period")
    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
    )
    raw_id_fields = ("employee", "reviewer")
    readonly_fields = ("created_at", "updated_at")

    def rating_stars(self, obj):
        return obj.get_rating_stars()
    rating_stars.short_description = "Stars"


# ==========================================
# Employee Document Admin
# ==========================================

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "title",
        "uploaded_at",
        "file_link",
    )
    search_fields = (
        "title",
        "employee__employee_id",
        "employee__user__first_name",
    )
    raw_id_fields = ("employee",)
    readonly_fields = ("uploaded_at",)

    def file_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">📄 View File</a>',
                obj.file.url
            )
        return "-"
    file_link.short_description = "File"


# ==========================================
# Holiday Admin
# ==========================================

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "date",
        "holiday_type",
        "is_company_holiday",
        "status_display",
    )
    list_filter = ("holiday_type", "is_company_holiday")
    search_fields = ("name",)
    ordering = ("date",)

    def status_display(self, obj):
        if obj.is_upcoming():
            return format_html('<span style="color: #34d399;">🟢 Upcoming</span>')
        return format_html('<span style="color: #94a3b8;">🔵 Past</span>')
    status_display.short_description = "Status"


# ==========================================
# Exit Request Admin
# ==========================================

@admin.register(ExitRequest)
class ExitRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "resignation_date",
        "last_working_day",
        "reason",
        "status",
        "approved_by",
    )
    list_filter = ("status", "reason")
    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )
    raw_id_fields = ("employee", "approved_by")
    readonly_fields = ("created_at", "updated_at")

    actions = ["approve_selected", "reject_selected", "complete_selected"]

    def approve_selected(self, request, queryset):
        updated = queryset.update(status="Approved")
        self.message_user(request, f"{updated} exit requests approved.")
    approve_selected.short_description = "Approve selected exit requests"

    def reject_selected(self, request, queryset):
        updated = queryset.update(status="Rejected")
        self.message_user(request, f"{updated} exit requests rejected.")
    reject_selected.short_description = "Reject selected exit requests"

    def complete_selected(self, request, queryset):
        updated = queryset.update(status="Completed")
        self.message_user(request, f"{updated} exit requests marked as completed.")
    complete_selected.short_description = "Mark selected exit requests as completed"