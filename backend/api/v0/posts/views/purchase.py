from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.response import Response

from api.services.purchase import initiate_post_purchase
from blog.models import Post


class PostPurchaseView(generics.GenericAPIView):
    """Create a payment intent for a post purchase."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    lookup_field = 'slug'

    def post(self, request, *args, **kwargs):
        """Initiate purchase for the given post."""
        post = get_object_or_404(self.get_queryset(), slug=kwargs.get('slug'))
        data, status_code = initiate_post_purchase(request.user, post)
        return Response(data, status=status_code)
