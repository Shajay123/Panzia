# payments/subscription_checker.py

from datetime import date
from django.utils import timezone
from .models import UserSubscription


def get_plan(user):
    """Get the current subscription plan for a user"""
    try:
        subscription = UserSubscription.objects.filter(
            user=user,
            active=True
        ).first()
        if subscription:
            return subscription.plan.name
        return "FREE"
    except:
        return "FREE"


def get_subscription(user):
    """Get the current subscription object for a user"""
    try:
        return UserSubscription.objects.filter(
            user=user,
            active=True
        ).first()
    except:
        return None


def can_create_sprint(user):
    """Check if a user can create a new sprint based on their plan"""
    try:
        subscription = UserSubscription.objects.filter(
            user=user,
            active=True
        ).first()
        
        if not subscription:
            # FREE plan - limited to 1 sprint
            from sprints.models import Sprint
            sprint_count = Sprint.objects.filter(startup__user=user).count()
            return sprint_count < 1
        
        plan_name = subscription.plan.name.upper()
        
        # Different plans have different limits
        if plan_name == "FREE":
            from sprints.models import Sprint
            sprint_count = Sprint.objects.filter(startup__user=user).count()
            return sprint_count < 1
        elif plan_name == "STARTER":
            from sprints.models import Sprint
            sprint_count = Sprint.objects.filter(startup__user=user).count()
            return sprint_count < 3
        elif plan_name == "GROWTH":
            from sprints.models import Sprint
            sprint_count = Sprint.objects.filter(startup__user=user).count()
            return sprint_count < 10
        elif plan_name == "SCALE":
            return True  # Unlimited
        elif plan_name == "PRO":
            from sprints.models import Sprint
            sprint_count = Sprint.objects.filter(startup__user=user).count()
            return sprint_count < 5
        elif plan_name == "ELITE":
            from sprints.models import Sprint
            sprint_count = Sprint.objects.filter(startup__user=user).count()
            return sprint_count < 20
        else:
            return True
    except:
        return True


def get_sprint_limit(user):
    """Get the maximum number of sprints allowed for a user's plan"""
    try:
        subscription = UserSubscription.objects.filter(
            user=user,
            active=True
        ).first()
        
        if not subscription:
            return 1  # FREE plan
        
        plan_name = subscription.plan.name.upper()
        
        if plan_name == "FREE":
            return 1
        elif plan_name == "STARTER":
            return 3
        elif plan_name == "GROWTH":
            return 10
        elif plan_name == "SCALE":
            return 999  # Unlimited
        elif plan_name == "PRO":
            return 5
        elif plan_name == "ELITE":
            return 20
        else:
            return 999
    except:
        return 999


def get_remaining_sprints(user):
    """Get the number of sprints remaining for a user"""
    try:
        from sprints.models import Sprint
        limit = get_sprint_limit(user)
        current = Sprint.objects.filter(startup__user=user).count()
        return max(0, limit - current)
    except:
        return 0


def is_subscription_expiring_soon(user, days=7):
    """Check if the user's subscription is expiring soon"""
    try:
        subscription = UserSubscription.objects.filter(
            user=user,
            active=True
        ).first()
        
        if not subscription or not subscription.end_date:
            return False
        
        today = timezone.now().date()
        days_remaining = (subscription.end_date - today).days
        
        return 0 < days_remaining <= days
    except:
        return False


def get_subscription_status(user):
    """Get detailed subscription status for a user"""
    try:
        subscription = UserSubscription.objects.filter(
            user=user,
            active=True
        ).first()
        
        if not subscription:
            return {
                'has_subscription': False,
                'plan_name': 'FREE',
                'is_active': False,
                'days_remaining': 0,
                'is_expiring_soon': False,
            }
        
        today = timezone.now().date()
        days_remaining = (subscription.end_date - today).days if subscription.end_date else 0
        
        return {
            'has_subscription': True,
            'plan_name': subscription.plan.name,
            'plan': subscription.plan,
            'is_active': subscription.active,
            'start_date': subscription.start_date,
            'end_date': subscription.end_date,
            'days_remaining': days_remaining,
            'is_expiring_soon': 0 < days_remaining <= 7,
            'is_expired': days_remaining <= 0,
        }
    except:
        return {
            'has_subscription': False,
            'plan_name': 'FREE',
            'is_active': False,
            'days_remaining': 0,
            'is_expiring_soon': False,
        }