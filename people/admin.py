from django.contrib import admin

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
)


# ==========================================
# Department
# ==========================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "startup",
        "code",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "startup",
    )

    ordering = (
        "name",
    )


# ==========================================
# Employee
# ==========================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "user",
        "startup",
        "department",
        "designation",
        "employment_type",
        "status",
        "work_mode",
        "hire_source",
        "salary",
        "joining_date",
        "is_active",
    )

    list_filter = (
        "startup",
        "department",
        "employment_type",
        "status",
        "hire_source",
        "work_mode",
        "is_active",
        "joining_date",
    )

    search_fields = (
        "employee_id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "designation",
        "phone",
    )

    ordering = (
        "user__first_name",
    )

    date_hierarchy = "joining_date"

    autocomplete_fields = (
        "user",
        "department",
        "manager",
    )

    fieldsets = (

        (
            "Basic Information",
            {
                "fields": (
                    "startup",
                    "user",
                    "employee_id",
                    "department",
                    "manager",
                )
            },
        ),

        (
            "Employment",
            {
                "fields": (
                    "designation",
                    "employment_type",
                    "status",
                    "hire_source",
                    "work_mode",
                    "joining_date",
                    "confirmation_date",
                    "probation_end",
                )
            },
        ),

        (
            "Contact",
            {
                "fields": (
                    "phone",
                    "emergency_contact",
                )
            },
        ),

        (
            "Payroll",
            {
                "fields": (
                    "salary",
                    "is_payroll_enabled",
                )
            },
        ),

        (
            "Other",
            {
                "fields": (
                    "profile_image",
                    "notes",
                    "is_active",
                )
            },
        ),

    )


# ==========================================
# Attendance
# ==========================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "date",
        "status",
        "check_in",
        "check_out",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )

    date_hierarchy = "date"

    autocomplete_fields = (
        "employee",
    )


# ==========================================
# Leave Requests
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

    list_filter = (
        "status",
        "leave_type",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )

    autocomplete_fields = (
        "employee",
        "approved_by",
    )


# ==========================================
# Payroll
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

    list_filter = (
        "paid",
        "month",
        "year",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
    )

    autocomplete_fields = (
        "employee",
    )


# ==========================================
# Payslip
# ==========================================

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):

    list_display = (
        "payroll",
        "created_at",
    )

    autocomplete_fields = (
        "payroll",
    )


# ==========================================
# Performance
# ==========================================

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "reviewer",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
    )

    autocomplete_fields = (
        "employee",
        "reviewer",
    )


# ==========================================
# Documents
# ==========================================

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "title",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "employee__employee_id",
    )

    autocomplete_fields = (
        "employee",
    )


# ==========================================
# Holidays
# ==========================================

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "date",
        "holiday_type",
    )

    list_filter = (
        "holiday_type",
    )

    ordering = (
        "date",
    )

    search_fields = (
        "name",
    )