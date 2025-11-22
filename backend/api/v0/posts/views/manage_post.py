from rest_framework import viewsets

from api.permissions import IsAdminOrActiveSubscriber
from api.v0.posts.serializers.detail import PostDetailSerializer
from api.v0.posts.serializers.list import PostListSerializer
from api.v0.posts.serializers.write import PostCreateUpdateSerializer
from blog.models import Post


class PostManageViewSet(viewsets.ModelViewSet):
    """CRUD for posts; allowed for admins or active subscribers."""

    queryset = Post.objects.all().select_related('author', 'category')
    permission_classes = [IsAdminOrActiveSubscriber]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['list', 'retrieve']:
            return PostDetailSerializer if self.action == 'retrieve' else PostListSerializer
        return PostCreateUpdateSerializer

    def perform_create(self, serializer):
        """Create post with current user as author."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Update post."""
        serializer.save()

    def perform_destroy(self, instance):
        """Delete post."""
        instance.delete()
