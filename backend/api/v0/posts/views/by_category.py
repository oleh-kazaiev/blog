from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from api.v0.posts.serializers.list import PostListSerializer
from blog.models import Category, Post


class PostsByCategoryView(generics.GenericAPIView):
    """Filter posts by category slug."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PostListSerializer

    def get_queryset(self):
        """Return published posts with related author/category."""
        queryset = Post.objects.filter(is_published=True).select_related('author', 'category')
        return queryset

    def get(self, request, *args, **kwargs):
        """Return posts for the requested category."""
        category_slug = request.query_params.get('slug')
        if not category_slug:
            return Response({'error': 'Category slug is required'}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(Category, slug=category_slug)
        posts = self.get_queryset().filter(category=category)

        page = self.paginate_queryset(posts)
        context = {'request': request}
        if page is not None:
            serializer = PostListSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context=context)
        return Response(serializer.data)
