from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.response import Response

from api.services.comment import add_comment_to_post
from blog.models import Post


class PostCommentCreateView(generics.GenericAPIView):
    """Add a comment to a post."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    lookup_field = 'slug'

    def post(self, request, *args, **kwargs):
        """Create a new comment for the given post."""
        post = get_object_or_404(self.get_queryset(), slug=kwargs.get('slug'))
        data, status_code = add_comment_to_post(post, request, request.data)
        return Response(data, status=status_code)
