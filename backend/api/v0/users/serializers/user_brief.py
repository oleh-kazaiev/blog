from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    """Simplified user serializer for nested relationships."""

    class Meta:
        """Meta configuration."""

        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
