from django.utils import timezone

from .models import UserSubscription


def has_active_subscription(user):

    subscription = UserSubscription.objects.filter(

        user=user,

        active=True,

        end_date__gte=timezone.now()

    ).first()

    return subscription is not None