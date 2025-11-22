from rest_framework import serializers

from blog.models import PostReaction


class PostReactionSerializer(serializers.ModelSerializer):
    """Serializer for the PostReaction model."""

    class Meta:
        """Meta configuration."""

        model = PostReaction
        fields = ['id', 'post', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['created_at']
