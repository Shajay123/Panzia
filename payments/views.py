from datetime import timedelta

import razorpay

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import SubscriptionPlan, UserSubscription


# ==========================================
# SUBSCRIPTION PLANS
# ==========================================

@login_required
def subscription_plans(request):

    role = request.user.role.lower()

    if role == "talent":

        plans = SubscriptionPlan.objects.filter(
            name__in=["FREE", "PRO", "ELITE"],
            is_active=True
        )

    else:

        plans = SubscriptionPlan.objects.filter(
            name__in=["STARTER", "GROWTH", "SCALE"],
            is_active=True
        )

    return render(
        request,
        "payments/subscription_plans.html",
        {
            "plans": plans
        }
    )


# ==========================================
# BUY PLAN
# ==========================================

@login_required
def buy_plan(request, plan_id):

    plan = get_object_or_404(
        SubscriptionPlan,
        id=plan_id,
        is_active=True
    )

    role = request.user.role.lower()

    if role == "talent":

        allowed_plans = [
            "FREE",
            "PRO",
            "ELITE"
        ]

    else:

        allowed_plans = [
            "STARTER",
            "GROWTH",
            "SCALE"
        ]

    if plan.name not in allowed_plans:

        return redirect("subscription_plans")

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    order = client.order.create({

        "amount": int(plan.price * 100),

        "currency": "INR",

        "payment_capture": 1

    })

    return render(

        request,

        "payments/payment.html",

        {

            "plan": plan,

            "order": order,

            "key_id": settings.RAZORPAY_KEY_ID

        }

    )


# ==========================================
# PAYMENT SUCCESS
# ==========================================

@login_required
def payment_success(request):

    plan_id = request.GET.get("plan_id")

    if not plan_id:

        return redirect("subscription_plans")

    plan = get_object_or_404(
        SubscriptionPlan,
        id=plan_id
    )

    # deactivate old subscriptions
    UserSubscription.objects.filter(
        user=request.user,
        active=True
    ).update(active=False)

    UserSubscription.objects.create(

        user=request.user,

        plan=plan,

        end_date=timezone.now() +
                 timedelta(days=plan.duration_days),

        active=True

    )

    if request.user.role.lower() == "startup":

        return redirect(
            "startup_dashboard"
        )

    return redirect(
        "talent_dashboard"
    )



from .models import SubscriptionHistory
from django.contrib.auth.decorators import login_required


@login_required
def billing_history(request):

    history = SubscriptionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "payments/billing_history.html",
        {
            "history": history
        }
    )


@login_required
def payment_history(request):

    payments = SubscriptionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "payments/payment_history.html",
        {
            "payments": payments
        }
    )


@login_required
def invoices(request):

    invoices = SubscriptionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "payments/invoices.html",
        {
            "invoices": invoices
        }
    )