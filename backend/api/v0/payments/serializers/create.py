from rest_framework import serializers


class PaymentCreateSerializer(serializers.Serializer):
    """Validate payment creation payload."""

    amount = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(default='usd')
