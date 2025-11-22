from django.core.cache import cache

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.v0.posts.serializers.category import CategorySerializer
from blog.models import Category


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading categories."""

    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Get all categories."""
        return Category.objects.all()

    def list(self, request, *args, **kwargs):  # noqa: A003
        """List all categories with caching."""
        cache_key = 'all_categories_response'
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated = self.get_paginated_response(serializer.data)
            cache.set(cache_key, paginated.data, 60 * 60 * 24)
            return paginated

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, 60 * 60 * 24)
        return Response(data)
