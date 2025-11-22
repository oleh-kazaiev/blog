from django.db import DatabaseError

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from api.v0.posts.serializers.list import PostListSerializer
from api.v0.search.serializers.query import SearchQuerySerializer
from blog.documents import PostDocument
from blog.models import Post


class PostSearchView(generics.GenericAPIView):
    """Search published posts using Elasticsearch, with DB fallback."""

    serializer_class = SearchQuerySerializer
    permission_classes = [permissions.AllowAny]

    def search_es(self, query):
        """Search Elasticsearch for posts; return list of IDs or None on failure."""
        try:
            s = (
                PostDocument.search()
                .query(
                    'multi_match',
                    query=query,
                    fields=['title', 'excerpt', 'content'],
                    type='bool_prefix',
                )
                .filter('term', is_published=True)
            )
            response = s.execute()
            return [hit.id for hit in response]
        except Exception:
            return None

    def get_queryset(self, query):
        """Return published posts matching the query."""
        qs = Post.objects.filter(is_published=True).select_related('author', 'category')

        es_ids = self.search_es(query)
        if es_ids:
            return qs.filter(id__in=es_ids)
        # ES responded but found no matches OR failed; return empty queryset
        return qs.none()

    def get(self, request, *args, **kwargs):
        """Validate query params and return matching posts."""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data['q']

        try:
            queryset = self.get_queryset(query)
            page = self.paginate_queryset(queryset)
            context = {'request': request}

            if page is not None:
                results = PostListSerializer(page, many=True, context=context)
                return self.get_paginated_response(results.data)

            results = PostListSerializer(queryset, many=True, context=context)
            return Response(results.data, status=status.HTTP_200_OK)
        except DatabaseError:
            return Response(
                {'detail': 'Search temporarily unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
