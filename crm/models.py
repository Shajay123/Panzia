# from django.db import models

# from startups.models import StartupProfile

# # Create your models here.
# class Company(models.Model):

#     startup = models.ForeignKey(
#     StartupProfile,
#     on_delete=models.CASCADE,
#     related_name="crm_leads"
# )

#     company_name = models.CharField(
#         max_length=255
#     )

#     website = models.URLField(
#         blank=True,
#         null=True
#     )

#     industry = models.CharField(
#         max_length=100
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

# class Lead(models.Model):

#     STAGES = (

#         ("New","New"),
#         ("Qualified","Qualified"),
#         ("Proposal","Proposal"),
#         ("Won","Won"),
#         ("Lost","Lost")

#     )

#     startup = models.ForeignKey(
#         StartupProfile,
#         on_delete=models.CASCADE
#     )

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE
#     )

#     contact_name = models.CharField(
#         max_length=255
#     )

#     email = models.EmailField()

#     phone = models.CharField(
#         max_length=20
#     )

#     stage = models.CharField(
#         max_length=20,
#         choices=STAGES,
#         default="New"
#     )

#     expected_value = models.DecimalField(
#         max_digits=12,
#         decimal_places=2
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )


# class Deal(models.Model):

#     lead = models.ForeignKey(
#         Lead,
#         on_delete=models.CASCADE
#     )

#     value = models.DecimalField(
#         max_digits=12,
#         decimal_places=2
#     )

#     probability = models.IntegerField(
#         default=50
#     )

#     expected_close_date = models.DateField()

#     won = models.BooleanField(
#         default=False
#     )


# class FollowUp(models.Model):

#     lead = models.ForeignKey(
#         Lead,
#         on_delete=models.CASCADE
#     )

#     reminder_date = models.DateTimeField()

#     note = models.TextField()

#     completed = models.BooleanField(
#         default=False
#     )

# class SalesActivity(models.Model):

#     lead = models.ForeignKey(
#         Lead,
#         on_delete=models.CASCADE
#     )

#     activity_type = models.CharField(
#         max_length=100
#     )

#     notes = models.TextField()

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )


# class ClientHealth(models.Model):

#     company = models.OneToOneField(
#         Company,
#         on_delete=models.CASCADE
#     )

#     score = models.IntegerField(
#         default=100
#     )

#     status = models.CharField(
#         max_length=50,
#         default="Healthy"
#     )