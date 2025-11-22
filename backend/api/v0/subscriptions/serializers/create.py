from rest_framework import serializers

from payments.plans import get_subscription_plans


class SubscriptionCreateSerializer(serializers.Serializer):
    """Validate subscription creation payload."""

    plan = serializers.ChoiceField(choices=list(get_subscription_plans().keys()), required=False, default='month')
