from rest_framework import serializers

from blog.models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments from authenticated users only."""

    class Meta:
        """Meta configuration."""

        model = Comment
        fields = ['body']

    def validate(self, attrs):
        """Ensure an authenticated user provides the body."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            raise serializers.ValidationError({'detail': 'Authentication required to comment.'})
        return attrs

    def create(self, validated_data):
        """Create the comment for the provided post context."""
        post_id = self.context['post_id']
        request = self.context.get('request')
        user = request.user
        return Comment.objects.create(
            post_id=post_id,
            author=user,
            name=user.get_full_name() or user.email or 'Anonymous',
            email=user.email or None,
            **validated_data,
        )
