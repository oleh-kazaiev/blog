from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    """Validate search query parameters."""

    q = serializers.CharField(required=True, allow_blank=False, max_length=255)
