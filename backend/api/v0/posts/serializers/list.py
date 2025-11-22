from rest_framework import serializers

from api.v0.posts.serializers.category import CategorySerializer
from api.v0.users.serializers.user_brief import UserBriefSerializer
from blog.models import Post


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list view with summary information."""

    author = UserBriefSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    show_purchase_button = serializers.SerializerMethodField()

    class Meta:
        """Meta configuration."""

        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'featured_image', 'category',
            'created_at', 'published_at', 'likes_count', 'dislikes_count', 'user_reaction',
            'is_paid', 'price_cents', 'show_purchase_button'
        ]

    def get_likes_count(self, obj):
        """Get the number of likes for the post."""
        return getattr(obj, '_likes_count', obj.likes_count)

    def get_dislikes_count(self, obj):
        """Get the number of dislikes for the post."""
        return getattr(obj, '_dislikes_count', obj.dislikes_count)

    def get_user_reaction(self, obj):
        """Get the current user's reaction to the post."""
        request = self.context.get('request')
        return obj.get_user_reaction(request.user if request else None)

    def get_show_purchase_button(self, obj):
        """Determine if purchase button should be shown in list view.

        True if: post is paid AND user is authenticated AND user is not the author AND user doesn't have access
        """
        if not obj.is_paid:
            return False

        request = self.context.get('request')
        user = request.user if request else None

        # No button if user is not authenticated
        if not user or not user.is_authenticated:
            return False

        # No button if user is the author
        if obj.author_id == user.id:
            return False

        # Show button only if user doesn't have access
        return not obj.user_has_access(user)
