# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    
    list_display = (
        "username",
        "email",
        "role_colored",
        "startup_name",
        "is_staff",
        "is_active",
        "created_at",
    )
    
    list_filter = (
        "role",
        "startup",
        "is_staff",
        "is_active",
    )
    
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "startup__company_name",
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = UserAdmin.fieldsets + (
        ("Role & Startup", {
            "fields": ("role", "startup")
        }),
        ("Profile", {
            "fields": ("profile_image", "bio")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def role_colored(self, obj):
        colors = {
            'super_admin': '#7c3aed',  # Purple
            'startup_admin': '#3b6aff',  # Blue
            'startup_hr': '#22c55e',  # Green
            'startup_manager': '#f59e0b',  # Orange
            'employee': '#94a3b8',  # Gray
            'talent': '#ec4899',  # Pink
        }
        color = colors.get(obj.role, '#94a3b8')
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_colored.short_description = "Role"
    
    def startup_name(self, obj):
        if obj.startup:
            return format_html(
                '<span style="color: #a78bfa;">{}</span>',
                obj.startup.company_name
            )
        return "—"
    startup_name.short_description = "Startup"
    startup_name.admin_order_field = "startup__company_name"