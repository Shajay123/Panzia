from django.conf import settings
from django.db import models

class Certificate(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    course = models.ForeignKey(
    'courses.Course',
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )

    certificate_id = models.CharField(
        max_length=100,
        unique=True
    )

    pdf = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True
    )

    issued_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title