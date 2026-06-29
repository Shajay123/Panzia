from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "profile_preview",
        "is_staff",
        "is_active",
        "created_at",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
        "created_at",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "profile_preview",
    )

    fieldsets = UserAdmin.fieldsets + (

        ("Profile Information", {

            "fields": (

                "role",

                "profile_image",

                "profile_preview",

                "bio",

                "created_at",

            )

        }),

    )

    def profile_preview(self, obj):

        if obj.profile_image:

            return format_html(

                '<img src="{}" width="50" height="50" style="border-radius:50%;" />',

                obj.profile_image.url

            )

        return "No Image"

    profile_preview.short_description = "Profile"