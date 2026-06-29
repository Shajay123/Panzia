from django.shortcuts import render
import uuid
from certificates.models import Certificate
# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Course
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import (
    Course,
    Enrollment
)

def browse_courses(request):

    courses = Course.objects.filter(
        is_published=True
    )

    return render(
        request,
        "courses/browse_courses.html",
        {
            "courses": courses
        }
    )


def course_detail(request, slug):

    course = get_object_or_404(
        Course,
        slug=slug
    )

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course
        }
    )


@login_required
def enroll_course(
    request,
    course_id
):

    course = Course.objects.get(
        id=course_id
    )

    Enrollment.objects.get_or_create(

        user=request.user,

        course=course

    )

    return redirect(
        "my_courses"
    )


@login_required
def my_courses(request):

    enrollments = Enrollment.objects.filter(
        user=request.user
    )

    for enrollment in enrollments:

        lessons = Lesson.objects.filter(
            module__course=enrollment.course
        ).order_by(
            "module__order",
            "order"
        )

        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=enrollment.course,
            completed=True
        ).values_list(
            "lesson_id",
            flat=True
        )

        enrollment.next_lesson = None

        for lesson in lessons:

            if lesson.id not in completed_lessons:

                enrollment.next_lesson = lesson
                break

    completed_count = enrollments.filter(
        completed=True
    ).count()

    active_count = enrollments.filter(
        completed=False
    ).count()

    return render(
        request,
        "courses/my_courses.html",
        {
            "enrollments": enrollments,
            "completed_count": completed_count,
            "active_count": active_count,
        }
    )



from .models import Lesson
from .models import LessonProgress

@login_required
def lesson_detail(request, lesson_id):


    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    completed = LessonProgress.objects.filter(
        user=request.user,
        lesson=lesson,
        completed=True
    ).exists()

    course = lesson.module.course

    all_lessons = Lesson.objects.filter(
        module__course=course
    ).order_by(
        "module__order",
        "order"
    )

    lesson_list = list(all_lessons)

    current_index = lesson_list.index(lesson)

    previous_lesson = None
    next_lesson = None

    if current_index > 0:
        previous_lesson = lesson_list[current_index - 1]

    if current_index < len(lesson_list) - 1:
        next_lesson = lesson_list[current_index + 1]

    return render(
        request,
        "courses/lesson_detail.html",
        {
            "lesson": lesson,
            "completed": completed,
            "previous_lesson": previous_lesson,
            "next_lesson": next_lesson,
        }
    )




@login_required
def complete_lesson(
    request,
    lesson_id
):

    lesson = Lesson.objects.get(
        id=lesson_id
    )

    LessonProgress.objects.get_or_create(

        user=request.user,

        lesson=lesson,

        completed=True

    )

    enrollment = Enrollment.objects.get(

        user=request.user,

        course=lesson.module.course

    )

    total_lessons = Lesson.objects.filter(

        module__course=lesson.module.course

    ).count()

    completed_lessons = LessonProgress.objects.filter(

        user=request.user,

        lesson__module__course=lesson.module.course,

        completed=True

    ).count()

    progress = int(

        (completed_lessons / total_lessons)

        * 100

    )

    enrollment.progress = progress

    if progress == 100:

        enrollment.completed = True

        enrollment.save()

        Certificate.objects.get_or_create(

            user=request.user,

            course=lesson.module.course,

            defaults={

                "certificate_id":

                f"PANZIA-{uuid.uuid4().hex[:8].upper()}"

            }

        )

        from reputation.models import ReputationScore

        rep, created = ReputationScore.objects.get_or_create(

            user=request.user

        )

        rep.overall_score += 10

        rep.completed_sprints += 1

        rep.save()

    else:

        enrollment.save()

    return redirect(

        "lesson_detail",

        lesson.id

    )


from django.shortcuts import render,get_object_or_404
from certificates.models import Certificate
from django.contrib.auth.decorators import login_required
from courses.utils import get_recommended_sprints
from certificates.models import Certificate
from courses.models import Course
from accounts.models import User
import uuid

@login_required
def certificate(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            "title": course.title,
            "certificate_id": f"PANZIA-{uuid.uuid4().hex[:8].upper()}"
        }
    )

    sprints = get_recommended_sprints(course)

    return render(
        request,
        "courses/certificate.html",
        {
            "certificate": certificate,
            "recommended_sprints": sprints
        }
    )