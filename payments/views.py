from datetime import timedelta
import razorpay
import json
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count
from django.views.decorators.csrf import csrf_exempt

from .models import SubscriptionPlan, UserSubscription, SubscriptionHistory


# ==========================================
# PAYMENTS DASHBOARD
# ==========================================

@login_required
def payments_dashboard(request):
    """Payments dashboard with subscription overview"""
    
    # Get current subscription
    current_subscription = UserSubscription.objects.filter(
        user=request.user,
        active=True
    ).first()
    
    # Get subscription history
    history = SubscriptionHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    # Calculate stats
    total_payments = SubscriptionHistory.objects.filter(
        user=request.user
    ).count()
    
    total_spent = SubscriptionHistory.objects.filter(
        user=request.user
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    active_subscriptions = UserSubscription.objects.filter(
        user=request.user,
        active=True
    ).count()
    
    # Check if subscription is expiring soon (within 7 days)
    is_expiring_soon = False
    if current_subscription and current_subscription.end_date:
        days_remaining = (current_subscription.end_date - timezone.now()).days
        is_expiring_soon = days_remaining <= 7 and days_remaining > 0
    
    context = {
        'current_subscription': current_subscription,
        'history': history,
        'total_payments': total_payments,
        'total_spent': total_spent,
        'active_subscriptions': active_subscriptions,
        'is_expiring_soon': is_expiring_soon,
        'page_title': 'Payments Dashboard',
        'page_icon': '📊',
        'page_subtitle': 'Overview of your subscriptions and payments',
    }
    
    return render(request, 'payments/dashboard.html', context)


# ==========================================
# CURRENT SUBSCRIPTION
# ==========================================

@login_required
def current_subscription(request):
    """View current subscription details"""
    
    subscription = UserSubscription.objects.filter(
        user=request.user,
        active=True
    ).first()
    
    if not subscription:
        messages.warning(request, "You don't have an active subscription.")
        return redirect('payments:subscription_plans')  # FIXED: Added 'payments:'
    
    # Calculate days remaining
    days_remaining = 0
    if subscription.end_date:
        days_remaining = (subscription.end_date - timezone.now()).days
    
    context = {
        'subscription': subscription,
        'days_remaining': days_remaining,
        'page_title': 'My Subscription',
        'page_icon': '✅',
        'page_subtitle': 'View your current subscription details',
    }
    
    return render(request, 'payments/current_subscription.html', context)


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

    # Get current subscription
    current_sub = UserSubscription.objects.filter(
        user=request.user,
        active=True
    ).first()

    return render(
        request,
        "payments/subscription_plans.html",
        {
            "plans": plans,
            "current_sub": current_sub,
            "page_title": "Subscription Plans",
            "page_icon": "📋",
            "page_subtitle": "Choose the plan that fits your needs",
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
        allowed_plans = ["FREE", "PRO", "ELITE"]
    else:
        allowed_plans = ["STARTER", "GROWTH", "SCALE"]

    if plan.name not in allowed_plans:
        messages.error(request, "This plan is not available for your role.")
        return redirect("payments:subscription_plans")  # FIXED: Added 'payments:'

    # If plan is FREE, activate directly without payment
    if plan.name.upper() == "FREE" or plan.price == 0:
        # Deactivate old subscriptions
        UserSubscription.objects.filter(
            user=request.user,
            active=True
        ).update(active=False)

        # Create new subscription
        UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            end_date=timezone.now() + timedelta(days=plan.duration_days),
            active=True
        )

        # Create subscription history entry for free plan
        SubscriptionHistory.objects.create(
            user=request.user,
            plan=plan,
            subscription=UserSubscription.objects.filter(
                user=request.user,
                active=True
            ).first(),
            amount=0,
            status="success",
            payment_id="FREE_PLAN",
            order_id="FREE_PLAN"
        )

        messages.success(request, f"🎉 Successfully subscribed to {plan.name} plan!")
        return redirect('payments:subscription_plans')  # FIXED: Added 'payments:'

    # Create Razorpay order for paid plans
    try:
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
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect("payments:subscription_plans")  # FIXED: Added 'payments:'

    return render(
        request,
        "payments/payment.html",
        {
            "plan": plan,
            "order": order,
            "key_id": settings.RAZORPAY_KEY_ID,
            "page_title": f"Pay for {plan.name} Plan",
            "page_icon": "💳",
            "page_subtitle": f"Complete your payment for the {plan.name} plan",
        }
    )


# ==========================================
# PAYMENT SUCCESS
# ==========================================

@login_required
def payment_success(request):
    plan_id = request.GET.get("plan_id")
    payment_id = request.GET.get("payment_id")
    order_id = request.GET.get("order_id")

    if not plan_id:
        messages.error(request, "Invalid payment request.")
        return redirect("payments:subscription_plans")  # FIXED: Added 'payments:'

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Deactivate old subscriptions
    UserSubscription.objects.filter(
        user=request.user,
        active=True
    ).update(active=False)

    # Create new subscription
    subscription = UserSubscription.objects.create(
        user=request.user,
        plan=plan,
        end_date=timezone.now() + timedelta(days=plan.duration_days),
        active=True
    )

    # Create subscription history entry
    SubscriptionHistory.objects.create(
        user=request.user,
        plan=plan,
        subscription=subscription,
        amount=plan.price,
        payment_id=payment_id or "",
        order_id=order_id or "",
        status="success"
    )

    messages.success(request, f"🎉 Successfully subscribed to {plan.name} plan!")

    if request.user.role.lower() == "startup":
        return redirect("startup_dashboard")

    return redirect("talent_dashboard")


# ==========================================
# PAYMENT FAILED
# ==========================================

@login_required
def payment_failed(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect("payments:subscription_plans")  # FIXED: Added 'payments:'


# ==========================================
# BILLING HISTORY
# ==========================================

@login_required
def billing_history(request):
    history = SubscriptionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "payments/billing_history.html",
        {
            "history": history,
            "page_title": "Billing History",
            "page_icon": "🧾",
            "page_subtitle": "View your billing history",
        }
    )


# ==========================================
# PAYMENT HISTORY
# ==========================================

@login_required
def payment_history(request):
    payments = SubscriptionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "payments/payment_history.html",
        {
            "payments": payments,
            "page_title": "Payment History",
            "page_icon": "📜",
            "page_subtitle": "View your payment history",
        }
    )


# ==========================================
# INVOICES
# ==========================================

@login_required
def invoices(request):
    invoices = SubscriptionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "payments/invoices.html",
        {
            "invoices": invoices,
            "page_title": "Invoices",
            "page_icon": "📄",
            "page_subtitle": "View your invoices",
        }
    )


# ==========================================
# CANCEL SUBSCRIPTION
# ==========================================

@login_required
def cancel_subscription(request):
    if request.method == "POST":
        subscription = UserSubscription.objects.filter(
            user=request.user,
            active=True
        ).first()
        
        if subscription:
            subscription.active = False
            subscription.save()
            messages.success(request, "Your subscription has been cancelled.")
        else:
            messages.warning(request, "No active subscription found.")
        
        return redirect("payments:subscription_plans")  # FIXED: Added 'payments:'
    
    return redirect("payments:current_subscription")  # FIXED: Added 'payments:'


# ==========================================
# RAZORPAY WEBHOOK
# ==========================================

@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhook events"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            event = data.get('event')
            
            if event == 'payment.captured':
                payload = data.get('payload', {})
                payment = payload.get('payment', {}).get('entity', {})
                order_id = payment.get('order_id')
                payment_id = payment.get('id')
                amount = payment.get('amount', 0) / 100
                
                # Find the pending subscription history
                history = SubscriptionHistory.objects.filter(
                    order_id=order_id,
                    status='pending'
                ).first()
                
                if history:
                    history.payment_id = payment_id
                    history.status = 'success'
                    history.save()
                    
                    # Activate the subscription
                    subscription = history.subscription
                    if subscription:
                        subscription.active = True
                        subscription.save()
                
                return JsonResponse({'status': 'success'})
            
            elif event == 'payment.failed':
                payload = data.get('payload', {})
                payment = payload.get('payment', {}).get('entity', {})
                order_id = payment.get('order_id')
                
                history = SubscriptionHistory.objects.filter(
                    order_id=order_id,
                    status='pending'
                ).first()
                
                if history:
                    history.status = 'failed'
                    history.save()
                
                return JsonResponse({'status': 'success'})
            
            return JsonResponse({'status': 'ignored'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)