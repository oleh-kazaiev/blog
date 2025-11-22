from zoneinfo import ZoneInfo

from rest_framework import serializers

from blog.models import Post


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating posts."""

    class Meta:
        """Meta configuration."""

        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'featured_image', 'excerpt', 'category',
            'is_published', 'published_at', 'is_paid', 'price_cents',
        ]
        read_only_fields = ['id', 'slug']

    def validate_published_at(self, value):
        """Ensure published_at is timezone-aware, defaulting to UTC if naive."""
        if value is None:
            return value
        if value.tzinfo:
            return value
        return value.replace(tzinfo=ZoneInfo('UTC'))

    def create(self, validated_data):
        """Create a post with author from request user."""
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('author', request.user)
        return super().create(validated_data)
