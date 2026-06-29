from django.contrib import admin

from .models import (
    Course,
    CourseModule,
    Lesson,
    Enrollment,
    LessonProgress
)


# ==========================================
# LESSON INLINE
# ==========================================

class LessonInline(admin.TabularInline):

    model = Lesson

    extra = 1


# ==========================================
# MODULE INLINE
# ==========================================

class ModuleInline(admin.TabularInline):

    model = CourseModule

    extra = 1


# ==========================================
# COURSE ADMIN
# ==========================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (

        "title",
        "category",
        "level",
        "instructor",
        "is_free",
        "price",
        "is_published",
        "created_at",

    )

    list_filter = (

        "level",
        "category",
        "is_free",
        "is_published",
        "created_at"

    )

    search_fields = (

        "title",
        "category",
        "instructor"

    )

    prepopulated_fields = {

        "slug": ("title",)

    }

    readonly_fields = (

        "created_at",

    )

    ordering = (

        "-created_at",

    )

    inlines = [

        ModuleInline

    ]


# ==========================================
# MODULE ADMIN
# ==========================================

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):

    list_display = (

        "title",
        "course",
        "order"

    )

    list_filter = (

        "course",

    )

    search_fields = (

        "title",
        "course__title"

    )

    ordering = (

        "course",
        "order"

    )

    inlines = [

        LessonInline

    ]


# ==========================================
# LESSON ADMIN
# ==========================================

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (

        "title",
        "module",
        "duration",
        "order"

    )

    list_filter = (

        "module",

    )

    search_fields = (

        "title",
        "module__title",
        "module__course__title"

    )

    ordering = (

        "module",
        "order"

    )


# ==========================================
# ENROLLMENT ADMIN
# ==========================================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (

        "user",
        "course",
        "progress",
        "completed",
        "joined_at"

    )

    list_filter = (

        "completed",
        "joined_at"

    )

    search_fields = (

        "user__username",
        "user__email",
        "course__title"

    )

    readonly_fields = (

        "joined_at",

    )

    ordering = (

        "-joined_at",

    )


# ==========================================
# LESSON PROGRESS ADMIN
# ==========================================

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):

    list_display = (

        "user",
        "lesson",
        "completed",
        "completed_at"

    )

    list_filter = (

        "completed",

    )

    search_fields = (

        "user__username",
        "lesson__title"

    )

    readonly_fields = (

        "completed_at",

    )

    ordering = (

        "-completed_at",

    )