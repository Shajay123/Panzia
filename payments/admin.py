from django.contrib import admin

from .models import (
    SubscriptionPlan,
    UserSubscription,
    SubscriptionHistory
)


# ==========================================
# SUBSCRIPTION PLAN ADMIN
# ==========================================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "price",
        "duration_days",
        "is_active",
    )

    list_filter = (
        "is_active",
        "name",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "price",
    )


# ==========================================
# USER SUBSCRIPTION ADMIN
# ==========================================

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "plan",
        "start_date",
        "end_date",
        "active",
    )

    list_filter = (
        "active",
        "plan",
    )

    search_fields = (
        "user__username",
        "user__email",
        "plan__name",
    )

    readonly_fields = (
        "start_date",
    )

    ordering = (
        "-start_date",
    )


# ==========================================
# SUBSCRIPTION HISTORY ADMIN
# ==========================================

@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "plan",
        "amount",
        "payment_id",
        "created_at",
    )

    list_filter = (
        "plan",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "payment_id",
        "plan",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )