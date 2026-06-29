from django.urls import path
from . import views

urlpatterns = [

    path(
        "plans/",
        views.subscription_plans,
        name="subscription_plans"
    ),

    path(
        "buy/<int:plan_id>/",
        views.buy_plan,
        name="buy_plan"
    ),

    path(
        "success/",
        views.payment_success,
        name="payment_success"
    ),


    path(
    "billing-history/",
    views.billing_history,
    name="billing_history"
    ),

    path(
        "payment-history/",
        views.payment_history,
        name="payment_history"
    ),

    path(
        "invoices/",
        views.invoices,
        name="invoices"
    ),

]