from django.utils import timezone

from payments.models import UserSubscription


def get_plan(user):

    subscription = UserSubscription.objects.filter(

        user=user,

        active=True,

        end_date__gte=timezone.now()

    ).first()

    if subscription:

        return subscription.plan.name

    return "FREE"