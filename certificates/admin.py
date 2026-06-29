from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "course",
        "certificate_id",
        "has_pdf",
        "issued_date",
    )

    list_filter = (
        "course",
        "issued_date",
    )

    search_fields = (
        "title",
        "certificate_id",
        "user__username",
        "user__email",
        "course__title",
    )

    ordering = (
        "-issued_date",
    )

    readonly_fields = (
        "issued_date",
    )

    def has_pdf(self, obj):
        return bool(obj.pdf)

    has_pdf.boolean = True
    has_pdf.short_description = "PDF Available"