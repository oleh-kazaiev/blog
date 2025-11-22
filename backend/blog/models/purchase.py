from django.conf import settings
from django.db import models
from django.utils import timezone


class PostPurchase(models.Model):
    """Model for tracking post purchases."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_purchases',
    )
    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        related_name='purchases',
    )
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='post_purchase',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    access_granted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta configuration."""

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=models.Q(status='succeeded'),
                name='unique_successful_purchase_per_post',
            ),
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='purchase_user_status_idx'),
            models.Index(fields=['user', 'post'], name='purchase_user_post_idx'),
            models.Index(fields=['post', 'status'], name='purchase_post_status_idx'),
            models.Index(fields=['payment'], name='purchase_payment_idx'),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f'Purchase<{self.id}> user={self.user_id} post={self.post_id} status={self.status}'

    def mark_succeeded(self) -> None:
        """Mark purchase as succeeded and grant access."""
        self.status = 'succeeded'
        self.access_granted_at = timezone.now()
        self.save(update_fields=['status', 'access_granted_at', 'updated_at'])

    def mark_failed(self, error: str | None = None) -> None:
        """Mark purchase as failed."""
        self.status = 'failed'
        self.save(update_fields=['status', 'updated_at'])
