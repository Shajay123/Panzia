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
import logging

from .models import SubscriptionPlan, UserSubscription, SubscriptionHistory

logger = logging.getLogger(__name__)


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
        days_remaining = (current_subscription.end_date - timezone.now().date()).days
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
        return redirect('payments:subscription_plans')
    
    # Calculate days remaining
    days_remaining = 0
    if subscription.end_date:
        days_remaining = (subscription.end_date - timezone.now().date()).days
    
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
    role = request.user.role.lower() if request.user.role else "talent"

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
# BUY PLAN - FIXED
# ==========================================

@login_required
def buy_plan(request, plan_id):
    plan = get_object_or_404(
        SubscriptionPlan,
        id=plan_id,
        is_active=True
    )

    role = request.user.role.lower() if request.user.role else "talent"

    if role == "talent":
        allowed_plans = ["FREE", "PRO", "ELITE"]
    else:
        allowed_plans = ["STARTER", "GROWTH", "SCALE"]

    if plan.name not in allowed_plans:
        messages.error(request, "This plan is not available for your role.")
        return redirect("payments:subscription_plans")

    # If plan is FREE, activate directly without payment
    if plan.name.upper() == "FREE" or plan.price == 0:
        # Deactivate old subscriptions
        UserSubscription.objects.filter(
            user=request.user,
            active=True
        ).update(active=False)

        # Create new subscription
        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            end_date=timezone.now().date() + timedelta(days=plan.duration_days),
            active=True
        )

        # Create subscription history entry for free plan
        SubscriptionHistory.objects.create(
            user=request.user,
            plan=plan,
            subscription=subscription,
            amount=0,
            status="success",
            payment_id="FREE_PLAN",
            order_id="FREE_PLAN"
        )

        messages.success(request, f"🎉 Successfully subscribed to {plan.name} plan!")
        return redirect('payments:subscription_plans')

    # Create Razorpay order for paid plans
    try:
        # Check if Razorpay keys are configured
        if not hasattr(settings, 'RAZORPAY_KEY_ID') or not settings.RAZORPAY_KEY_ID:
            logger.error("RAZORPAY_KEY_ID is not configured")
            messages.error(request, "Payment system is not configured. Please contact support.")
            return redirect("payments:subscription_plans")
            
        if not hasattr(settings, 'RAZORPAY_KEY_SECRET') or not settings.RAZORPAY_KEY_SECRET:
            logger.error("RAZORPAY_KEY_SECRET is not configured")
            messages.error(request, "Payment system is not configured. Please contact support.")
            return redirect("payments:subscription_plans")

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        # Create order
        order_data = {
            "amount": int(plan.price * 100),
            "currency": "INR",
            "payment_capture": 1,
            "notes": {
                "plan_id": plan.id,
                "plan_name": plan.name,
                "user_id": request.user.id,
                "user_email": request.user.email,
            }
        }
        
        order = client.order.create(order_data)
        
        # Store order details in session for verification
        request.session['razorpay_order_id'] = order['id']
        request.session['plan_id'] = plan.id
        
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
        
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Razorpay BadRequestError: {str(e)}")
        messages.error(request, f"Payment initialization failed: {str(e)}")
        return redirect("payments:subscription_plans")
        
    except razorpay.errors.ServerError as e:
        logger.error(f"Razorpay ServerError: {str(e)}")
        messages.error(request, "Payment server is currently unavailable. Please try again later.")
        return redirect("payments:subscription_plans")
        
    except Exception as e:
        logger.error(f"Payment error: {str(e)}")
        messages.error(request, f"Payment error: {str(e)}")
        return redirect("payments:subscription_plans")


# ==========================================
# PAYMENT SUCCESS
# ==========================================

@login_required
def payment_success(request):
    # Get payment details from GET parameters
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')
    
    # Also check for our custom parameters
    plan_id = request.GET.get("plan_id")
    payment_id = request.GET.get("payment_id") or razorpay_payment_id
    order_id = request.GET.get("order_id") or razorpay_order_id

    # If we have Razorpay signature, verify it
    if razorpay_order_id and razorpay_payment_id and razorpay_signature:
        try:
            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)
            
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect("payments:payment_failed")
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect("payments:payment_failed")
    
    # Get plan from session or URL
    plan_id = plan_id or request.session.get('plan_id')
    
    if not plan_id:
        messages.error(request, "Invalid payment request. Plan not found.")
        return redirect("payments:subscription_plans")

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
        end_date=timezone.now().date() + timedelta(days=plan.duration_days),
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

    # Clear session
    request.session.pop('razorpay_order_id', None)
    request.session.pop('plan_id', None)

    messages.success(request, f"🎉 Successfully subscribed to {plan.name} plan!")

    if request.user.role and request.user.role.lower() == "startup":
        return redirect("startup_dashboard")

    return redirect("talent_dashboard")


# ==========================================
# PAYMENT FAILED
# ==========================================

@login_required
def payment_failed(request):
    # Clear session
    request.session.pop('razorpay_order_id', None)
    request.session.pop('plan_id', None)
    
    messages.error(request, "Payment failed. Please try again.")
    return redirect("payments:subscription_plans")


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
            "page_subtitle": "View your billing history and invoices",
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
            "page_subtitle": "View your complete payment history",
        }
    )


# ==========================================
# INVOICES
# ==========================================

@login_required
def invoices(request):
    invoices = SubscriptionHistory.objects.filter(
        user=request.user,
        status='success'
    ).order_by("-created_at")

    return render(
        request,
        "payments/invoices.html",
        {
            "invoices": invoices,
            "page_title": "Invoices",
            "page_icon": "📄",
            "page_subtitle": "View and download your invoices",
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
        
        return redirect("payments:subscription_plans")
    
    return redirect("payments:current_subscription")


# ==========================================
# RAZORPAY WEBHOOK
# ==========================================

@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhook events"""
    if request.method != "POST":
        return JsonResponse({'status': 'error'}, status=405)
    
    try:
        # Verify webhook signature (optional but recommended)
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        
        data = json.loads(request.body)
        event = data.get('event')
        
        logger.info(f"Webhook received: {event}")
        
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
                    
                logger.info(f"Payment captured for order: {order_id}")
            
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
                logger.info(f"Payment failed for order: {order_id}")
            
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'ignored'})
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)