from payments.models import UserSubscription
from django.utils import timezone


def has_active_subscription(user):

    return UserSubscription.objects.filter(

        user=user,

        active=True,

        end_date__gte=timezone.now()

    ).exists()