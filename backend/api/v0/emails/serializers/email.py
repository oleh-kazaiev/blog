# noqa: A005 - module name is intentional
from rest_framework import serializers

from users.models import Email


class EmailSerializer(serializers.ModelSerializer):
    """Serializer for Email model."""

    class Meta:
        """Meta options for EmailSerializer."""

        model = Email
        fields = ['id', 'subject', 'body', 'from_email', 'to_email', 'created_at', 'read']
        read_only_fields = ['id', 'subject', 'body', 'from_email', 'to_email', 'created_at']
