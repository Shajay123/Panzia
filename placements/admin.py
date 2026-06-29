from django.contrib import admin

from .models import (
    PlacementJob,
    PlacementApplication
)


# ==========================================
# JOB ADMIN
# ==========================================

@admin.register(PlacementJob)
class PlacementJobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "startup",
        "job_type",
        "location",
        "salary",
        "status",
        "created_at",
    )

    list_filter = (
        "job_type",
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "startup__company_name",
        "skills",
        "location",
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
                "startup",
                "title",
                "description",
                "skills",
            )

        }),

        ("Job Details", {

            "fields": (
                "job_type",
                "location",
                "salary",
                "experience_required",
                "status",
            )

        }),

        ("Dates", {

            "fields": (
                "created_at",
            )

        }),

    )


# ==========================================
# APPLICATION ADMIN
# ==========================================

@admin.register(PlacementApplication)
class PlacementApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "talent",
        "job",
        "startup_name",
        "status",
        "applied_at",
    )

    list_filter = (
        "status",
        "applied_at",
    )

    search_fields = (
        "talent__username",
        "talent__email",
        "job__title",
    )

    readonly_fields = (
        "applied_at",
    )

    ordering = (
        "-applied_at",
    )

    actions = [
        "mark_shortlisted",
        "mark_interview",
        "mark_hired",
        "mark_rejected",
    ]

    def startup_name(self, obj):

        return obj.job.startup

    startup_name.short_description = "Startup"

    # Bulk actions

    @admin.action(description="Mark selected applications as Shortlisted")
    def mark_shortlisted(self, request, queryset):

        queryset.update(
            status="Shortlisted"
        )

    @admin.action(description="Mark selected applications as Interview")
    def mark_interview(self, request, queryset):

        queryset.update(
            status="Interview"
        )

    @admin.action(description="Mark selected applications as Hired")
    def mark_hired(self, request, queryset):

        queryset.update(
            status="Hired"
        )

    @admin.action(description="Mark selected applications as Rejected")
    def mark_rejected(self, request, queryset):

        queryset.update(
            status="Rejected"
        )