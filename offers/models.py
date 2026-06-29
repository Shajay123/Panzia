from django.db import models

# Create your models here.
from django.db import models
from placements.models import PlacementApplication


class OfferLetter(models.Model):

    application = models.OneToOneField(
        PlacementApplication,
        on_delete=models.CASCADE
    )

    designation = models.CharField(
        max_length=200
    )

    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    joining_date = models.DateField()

    pdf_file = models.FileField(
        upload_to="offer_letters/",
        blank=True,
        null=True
    )

    accepted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.application.talent.username