from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Dashboard
    path('', views.payments_dashboard, name='payments_dashboard'),
    
    # Subscription Plans
    path('plans/', views.subscription_plans, name='subscription_plans'),
    path('buy/<int:plan_id>/', views.buy_plan, name='buy_plan'),
    path('current/', views.current_subscription, name='current_subscription'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # Payment
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    
    # History
    path('billing/', views.billing_history, name='billing_history'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('invoices/', views.invoices, name='invoices'),
    
    # Webhook
    path('webhook/', views.razorpay_webhook, name='razorpay_webhook'),
]