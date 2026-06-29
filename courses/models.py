from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):

    LEVEL_CHOICES = (

        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),

    )

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    thumbnail = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True
    )

    short_description = models.CharField(
        max_length=300
    )

    description = models.TextField()

    category = models.CharField(
        max_length=100
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )

    duration = models.CharField(
        max_length=50
    )

    instructor = models.CharField(
        max_length=100
    )

    is_free = models.BooleanField(
        default=True
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    is_published = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title


class CourseModule(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )

    skill_tags = models.CharField(
    max_length=300,
    blank=True,
    help_text="python,django,ai,react"
    )

    title = models.CharField(
        max_length=200
    )

    order = models.IntegerField(
        default=1
    )

    def __str__(self):

        return self.title


class Lesson(models.Model):

    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(
        max_length=200
    )

    video = models.FileField(
        upload_to="course_videos/",
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True
    )

    duration = models.CharField(
        max_length=50
    )

    order = models.IntegerField(
        default=1
    )

    def __str__(self):
        return self.title

from django.conf import settings
from django.db import models

class Enrollment(models.Model):

    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    progress = models.IntegerField(
        default=0
    )

    completed = models.BooleanField(
        default=False
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "user",
            "course"
        )

    def __str__(self):

        return f"{self.user.username} - {self.course.title}"
    
    @property
    def progress_percentage(self):
        total_lessons = Lesson.objects.filter(
            module__course=self.course
        ).count()

        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            lesson__module__course=self.course,
            completed=True
        ).count()

        if total_lessons == 0:
            return 0

        return int(
            (completed_lessons / total_lessons) * 100
        )

from django.contrib.auth.models import User

class LessonProgress(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    completed = models.BooleanField(
        default=False
    )

    completed_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = (
            "user",
            "lesson"
        )

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
    

