# payments/subscription_checker.py

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