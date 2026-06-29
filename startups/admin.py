from django.contrib import admin

from .models import StartupProfile


# ==========================================
# STARTUP PROFILE ADMIN
# ==========================================

@admin.register(StartupProfile)
class StartupProfileAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "user",
        "industry",
        "website",
        "created_at",
    )

    list_filter = (
        "industry",
        "created_at",
    )

    search_fields = (
        "company_name",
        "user__username",
        "user__email",
        "industry",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (

        ("Account", {

            "fields": (
                "user",
            )

        }),

        ("Company Information", {

            "fields": (
                "company_name",
                "tagline",
                "industry",
                "website",
                "description",
                "logo",
            )

        }),

        ("Dates", {

            "fields": (
                "created_at",
            )

        }),

    )