from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login credentials."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
