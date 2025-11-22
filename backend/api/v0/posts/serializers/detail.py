from rest_framework import serializers

from api.v0.posts.serializers.category import CategorySerializer
from api.v0.posts.serializers.comment import CommentSerializer
from api.v0.users.serializers.user_brief import UserBriefSerializer
from blog.models import Post


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed post view with comments and reactions."""

    author = UserBriefSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    user_has_access = serializers.SerializerMethodField()
    show_purchase_button = serializers.SerializerMethodField()

    class Meta:
        """Meta configuration."""

        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'author', 'featured_image', 'excerpt', 'category',
            'created_at', 'updated_at', 'published_at', 'comments', 'likes_count', 'dislikes_count',
            'user_reaction', 'is_paid', 'price_cents', 'user_has_access', 'show_purchase_button'
        ]

    def get_content(self, obj):
        """Return content only if user has access to paid posts."""
        if not obj.is_paid:
            return obj.content

        request = self.context.get('request')
        user = request.user if request else None

        # Allow author to always see their own content
        if user and user.is_authenticated and obj.author_id == user.id:
            return obj.content

        # Check if user has purchased or has active subscription
        if obj.user_has_access(user):
            return obj.content

        # Return None for paywalled content without access
        return None

    def get_user_has_access(self, obj):
        """Check if current user has access to this post."""
        if not obj.is_paid:
            return True

        request = self.context.get('request')
        user = request.user if request else None

        # Author always has access to their own posts
        if user and user.is_authenticated and obj.author_id == user.id:
            return True

        return obj.user_has_access(user)

    def get_show_purchase_button(self, obj):
        """Determine if purchase button should be shown.

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

    def get_comments(self, obj):
        """Get approved comments for the post."""
        comments = obj.comments.filter(is_approved=True)
        return CommentSerializer(comments, many=True, context=self.context).data

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
