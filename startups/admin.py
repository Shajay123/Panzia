# startups/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import StartupProfile

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