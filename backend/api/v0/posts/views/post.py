from django.db.models import Count, Q

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.v0.posts.serializers.detail import PostDetailSerializer
from api.v0.posts.serializers.list import PostListSerializer
from blog.models import Post


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading posts with reactions and comments."""

    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Get published posts with reaction counts."""
        queryset = Post.objects.filter(is_published=True)
        queryset = queryset.select_related('author', 'category')

        queryset = queryset.annotate(
            _likes_count=Count('reactions', filter=Q(reactions__reaction_type='like')),
            _dislikes_count=Count('reactions', filter=Q(reactions__reaction_type='dislike')),
        )

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('comments__author', 'reactions')

        return queryset

    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
