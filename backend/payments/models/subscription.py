from django.conf import settings
from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    """Subscription model for recurring access."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('active', 'Active'),
        ('incomplete', 'Incomplete'),
        ('canceled', 'Canceled'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('trialing', 'Trialing'),
        ('paused', 'Paused'),
        ('error', 'Error'),
    ]

    PLAN_CHOICES = [
        ('day', 'Day Pass'),
        ('week', 'Weekly'),
        ('month', 'Monthly'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    price_id = models.CharField(max_length=128)
    plan = models.CharField(max_length=16, choices=PLAN_CHOICES, default='month')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='pending', db_index=True)
    stripe_subscription_id = models.CharField(max_length=128, blank=True, default='', db_index=True)
    client_secret = models.CharField(max_length=255, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    idempotency_key = models.CharField(max_length=64, blank=True, null=True, unique=True, db_index=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta configuration."""

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'valid_until'], name='sub_user_status_valid_idx'),
            models.Index(fields=['status', 'valid_until'], name='sub_status_valid_idx'),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f'Subscription<{self.id}> {self.status} {self.price_id}'

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status != 'active':
            return False
        if not self.valid_until:
            return True
        return self.valid_until >= timezone.now()
