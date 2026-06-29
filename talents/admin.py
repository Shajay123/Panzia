from django.contrib import admin

from .models import (
    TalentProfile,
    PortfolioProject
)


# ==========================================
# TALENT PROFILE ADMIN
# ==========================================

@admin.register(TalentProfile)
class TalentProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "headline",
        "github",
        "linkedin",
        "portfolio",
    )

    search_fields = (
        "user__username",
        "user__email",
        "headline",
        "skills",
    )

    fieldsets = (

        ("User Information", {

            "fields": (
                "user",
                "headline",
                "bio",
                "skills",
            )

        }),

        ("Social Profiles", {

            "fields": (
                "github",
                "linkedin",
                "portfolio",
            )

        }),

        ("Profile Image", {

            "fields": (
                "profile_image",
            )

        }),

    )


# ==========================================
# PORTFOLIO PROJECT ADMIN
# ==========================================

@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "project_type",
        "is_verified",
        "created_at",
    )

    list_filter = (
        "project_type",
        "is_verified",
        "created_at",
    )

    search_fields = (
        "title",
        "user__username",
        "skills",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (

        ("Basic Information", {

            "fields": (
                "user",
                "title",
                "project_type",
                "description",
                "skills",
            )

        }),

        ("Links", {

            "fields": (
                "project_url",
                "github_url",
            )

        }),

        ("Media", {

            "fields": (
                "image",
            )

        }),

        ("Verification", {

            "fields": (
                "is_verified",
                "sprint_id",
            )

        }),

        ("Dates", {

            "fields": (
                "created_at",
            )

        }),

    )

    actions = [
        "verify_projects"
    ]

    @admin.action(description="Mark selected projects as verified")
    def verify_projects(self, request, queryset):

        queryset.update(
            is_verified=True
        )