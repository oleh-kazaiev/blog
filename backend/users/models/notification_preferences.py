from django.conf import settings
from django.db import models


class NotificationPreferences(models.Model):
    """User notification preferences for email notifications."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )

    # Blog interactions
    comment_on_post = models.BooleanField(default=True)
    post_reaction = models.BooleanField(default=True)

    # Payments
    payment_successful = models.BooleanField(default=True)
    payment_failed = models.BooleanField(default=True)

    # Subscriptions
    subscription_activated = models.BooleanField(default=True)
    subscription_expiring = models.BooleanField(default=True)
    subscription_cancelled = models.BooleanField(default=True)

    class Meta:
        """Meta options for NotificationPreferences model."""

        verbose_name = 'notification preferences'
        verbose_name_plural = 'notification preferences'

    def __str__(self) -> str:
        """Return string representation."""
        return f'Notification preferences for {self.user.email}'
