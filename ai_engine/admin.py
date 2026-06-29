from django.contrib import admin
from .models import Resume, CareerGoal


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "has_pdf",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "title",
        "user__username",
        "user__email",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )

    def has_pdf(self, obj):
        return bool(obj.pdf_file)

    has_pdf.boolean = True
    has_pdf.short_description = "PDF"


@admin.register(CareerGoal)
class CareerGoalAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "goal",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "goal",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )