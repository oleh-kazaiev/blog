from rest_framework import serializers

from api.v0.users.serializers.user_brief import UserBriefSerializer
from blog.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the Comment model."""

    author_details = UserBriefSerializer(source='author', read_only=True)

    class Meta:
        """Meta configuration."""

        model = Comment
        fields = ['id', 'body', 'created_at', 'author', 'author_details']
        read_only_fields = ['is_approved', 'author', 'author_details']

    def create(self, validated_data):
        """Creation is handled by CommentCreateSerializer."""
        raise NotImplementedError('Use CommentCreateSerializer for creation.')
