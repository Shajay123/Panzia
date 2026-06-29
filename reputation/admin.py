from django.contrib import admin

from .models import (
    ReputationScore,
    Review,
    MonthlyRanking
)


# ==========================================
# REPUTATION SCORE ADMIN
# ==========================================

@admin.register(ReputationScore)
class ReputationScoreAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "overall_score",
        "rank_tier",
        "execution_score",
        "reliability_score",
        "collaboration_score",
        "completed_sprints",
        "deployment_score",
    )

    list_filter = (
        "rank_tier",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    ordering = (
        "-overall_score",
    )

    fieldsets = (

        ("User", {

            "fields": (
                "user",
                "rank_tier",
                "overall_score",
            )

        }),

        ("Core Scores", {

            "fields": (
                "execution_score",
                "reliability_score",
                "collaboration_score",
                "deployment_score",
            )

        }),

        ("Performance Metrics", {

            "fields": (
                "completed_sprints",
                "applications_accepted",
                "sprint_completion_rate",
                "tasks_completed",
                "reviews_received",
            )

        }),

    )


# ==========================================
# REVIEW ADMIN
# ==========================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "talent",
        "sprint",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "talent__username",
        "talent__email",
        "sprint__title",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# ==========================================
# MONTHLY RANKING ADMIN
# ==========================================

@admin.register(MonthlyRanking)
class MonthlyRankingAdmin(admin.ModelAdmin):

    list_display = (
        "month",
        "year",
        "rank",
        "user",
        "score",
    )

    list_filter = (
        "month",
        "year",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    ordering = (
        "rank",
    )