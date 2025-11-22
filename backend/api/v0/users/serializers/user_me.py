from django.db import models
from django.utils import timezone

from rest_framework import serializers

from payments.models import Subscription
from users.models import User


class UserMeSerializer(serializers.ModelSerializer):
    """Serializer for returning the current user's profile."""

    has_active_subscription = serializers.SerializerMethodField()

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
