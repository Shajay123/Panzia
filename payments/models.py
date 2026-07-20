from django.db import models
from django.conf import settings
from django.utils import timezone


class SubscriptionPlan(models.Model):
    PLAN_TYPES = (
        ("FREE", "FREE"),
        ("PRO", "PRO"),
        ("ELITE", "ELITE"),
        ("STARTER", "STARTER"),
        ("GROWTH", "GROWTH"),
        ("SCALE", "SCALE"),
    )

    name = models.CharField(
        max_length=50,
        choices=PLAN_TYPES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    duration_days = models.IntegerField(
        default=30
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    features = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated list of features"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['price']
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

    def get_features_list(self):
        """Return features as a list"""
        if self.features:
            return [f.strip() for f in self.features.split(',') if f.strip()]
        return []


class UserSubscription(models.Model):
    SUBSCRIPTION_STATUS = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    start_date = models.DateTimeField(
        auto_now_add=True
    )

    end_date = models.DateTimeField()

    active = models.BooleanField(
        default=True
    )

    status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS,
        default='active'
    )

    # Razorpay payment details
    razorpay_order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Razorpay order ID"
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Razorpay payment ID"
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    def is_active(self):
        """Check if subscription is currently active"""
        if not self.active:
            return False
        if self.end_date and self.end_date < timezone.now():
            return False
        return True

    def days_remaining(self):
        """Get days remaining in subscription"""
        if not self.end_date:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    def is_expiring_soon(self, days=7):
        """Check if subscription is expiring soon"""
        remaining = self.days_remaining()
        return 0 < remaining <= days


class SubscriptionHistory(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_history'
    )

    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_history'
    )

    plan = models.CharField(
        max_length=50
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Razorpay order ID"
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    payment_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Full payment response data"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Subscription History'
        verbose_name_plural = 'Subscription Histories'

    def __str__(self):
        return f"{self.user.email} - {self.plan} - {self.status}"

    def is_success(self):
        return self.status == 'success'

    def is_pending(self):
        return self.status == 'pending'

    def get_amount_display(self):
        return f"₹{self.amount:.2f}"