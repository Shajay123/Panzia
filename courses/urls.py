from django.urls import path
from . import views

urlpatterns = [


# Browse Courses
path(
    "",
    views.browse_courses,
    name="browse_courses"
),

# My Courses
path(
    "my-courses/",
    views.my_courses,
    name="my_courses"
),

# Enrollment
path(
    "enroll/<int:course_id>/",
    views.enroll_course,
    name="enroll_course"
),

# Lessons
path(
    "lesson/<int:lesson_id>/",
    views.lesson_detail,
    name="lesson_detail"
),

path(
    "complete-lesson/<int:lesson_id>/",
    views.complete_lesson,
    name="complete_lesson"
),

# Certificate
path(
    "certificate/<int:course_id>/",
    views.certificate,
    name="certificate"
),

# Course Detail (KEEP LAST)
path(
    "detail/<slug:slug>/",
    views.course_detail,
    name="course_detail"
),


]
