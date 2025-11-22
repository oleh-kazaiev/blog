from rest_framework import serializers

from users.models import NotificationPreferences


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreferences model."""

    class Meta:
        """Meta options for NotificationPreferencesSerializer."""

        model = NotificationPreferences
        fields = [
            'comment_on_post',
            'post_reaction',
            'payment_successful',
            'payment_failed',
            'subscription_activated',
            'subscription_expiring',
            'subscription_cancelled',
        ]
