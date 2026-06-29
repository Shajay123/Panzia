from django.contrib import admin

from .models import (
    Skill,
    Sprint,
    SprintApplication,
    SprintMember,
    Task,
    Submission,
    SprintRole,
    Activity,
    SprintProject
)


# ==========================================
# INLINE MODELS
# ==========================================

class SprintRoleInline(admin.TabularInline):
    model = SprintRole
    extra = 1


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


# ==========================================
# SKILL ADMIN
# ==========================================

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


# ==========================================
# SPRINT ADMIN
# ==========================================

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "startup",
        "category",
        "status",
        "deadline",
        "max_contributors",
        "created_at",
    )

    list_filter = (
        "category",
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "domain",
        "startup__company_name",
    )

    readonly_fields = (
        "created_at",
    )

    filter_horizontal = (
        "required_skills",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        SprintRoleInline,
        TaskInline
    ]


# ==========================================
# APPLICATION ADMIN
# ==========================================

@admin.register(SprintApplication)
class SprintApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "talent",
        "sprint",
        "status",
        "applied_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "talent__username",
        "sprint__title",
    )

    ordering = (
        "-applied_at",
    )


# ==========================================
# MEMBER ADMIN
# ==========================================

@admin.register(SprintMember)
class SprintMemberAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "sprint",
        "joined_at",
    )

    search_fields = (
        "user__username",
        "sprint__title",
    )

    ordering = (
        "-joined_at",
    )


# ==========================================
# TASK ADMIN
# ==========================================

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "sprint",
        "assigned_to",
        "status",
        "deadline",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "title",
        "assigned_to__username",
        "sprint__title",
    )

    ordering = (
        "-created_at",
    )


# ==========================================
# SUBMISSION ADMIN
# ==========================================

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "task",
        "reviewed",
        "submitted_at",
    )

    list_filter = (
        "reviewed",
    )

    search_fields = (
        "user__username",
        "task__title",
    )

    ordering = (
        "-submitted_at",
    )


# ==========================================
# SPRINT ROLE ADMIN
# ==========================================

@admin.register(SprintRole)
class SprintRoleAdmin(admin.ModelAdmin):

    list_display = (
        "role_name",
        "sprint",
        "openings",
    )

    search_fields = (
        "role_name",
        "sprint__title",
    )


# ==========================================
# ACTIVITY ADMIN
# ==========================================

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "action",
        "created_at",
    )

    search_fields = (
        "user__username",
        "action",
    )

    ordering = (
        "-created_at",
    )


# ==========================================
# SPRINT PROJECT ADMIN
# ==========================================

@admin.register(SprintProject)
class SprintProjectAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "sprint",
        "startup_rating",
        "added_to_portfolio",
        "created_at",
    )

    list_filter = (
        "added_to_portfolio",
    )

    search_fields = (
        "title",
        "user__username",
        "sprint__title",
    )

    ordering = (
        "-created_at",
    )