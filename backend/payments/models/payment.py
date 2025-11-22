from django.conf import settings
from django.db import models


class Payment(models.Model):
    """Payment model for tracking transactions."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('requires_action', 'Requires Action'),
        ('canceled', 'Canceled'),
    ]

    PURPOSE_CHOICES = [
        ('post', 'Post Purchase'),
        ('subscription', 'Subscription'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    subscription = models.ForeignKey(
        'payments.Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
        default='post',
        db_index=True,
        help_text='Differentiates subscription vs post payments',
    )
    amount = models.PositiveIntegerField(help_text='Amount in cents')
    currency = models.CharField(max_length=10, default='usd')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    stripe_payment_intent_id = models.CharField(max_length=128, blank=True, default='')
    stripe_session_id = models.CharField(max_length=128, blank=True, default='', help_text='Stripe Checkout Session ID')
    client_secret = models.CharField(max_length=255, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    idempotency_key = models.CharField(max_length=64, blank=True, null=True, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta configuration."""

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at'], name='payment_user_status_idx'),
            models.Index(fields=['post', 'status'], name='payment_post_status_idx'),
            models.Index(fields=['payment_type', 'status'], name='payment_type_status_idx'),
            models.Index(fields=['subscription', 'status'], name='pay_sub_status_idx'),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f'Payment<{self.id}> {self.status} {self.amount}{self.currency}'
