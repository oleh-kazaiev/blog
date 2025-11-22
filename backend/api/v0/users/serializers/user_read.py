from django.db import models
from django.utils import timezone

from rest_framework import serializers

from payments.models import Subscription
from users.models import User

from ...emails.serializers.email import EmailSerializer


class UserReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for returning user data without password fields."""

    has_active_subscription = serializers.SerializerMethodField()
    emails = EmailSerializer(many=True, read_only=True)

    class Meta:
        """Meta configuration."""

        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'bio',
            'profile_picture',
            'website',
            'is_admin',
            'has_active_subscription',
            'emails',
        ]
        read_only_fields = fields

    def get_has_active_subscription(self, obj: User) -> bool:
        """Return True if user has an active subscription."""
        now = timezone.now()
        return Subscription.objects.filter(
            user=obj,
            status='active',
        ).filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now)
        ).exists()
