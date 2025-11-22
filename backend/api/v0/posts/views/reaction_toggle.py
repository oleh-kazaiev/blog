from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from api.services.reaction import toggle_reaction
from api.v0.posts.serializers.reaction_toggle import ReactionToggleSerializer
from blog.models import Post


class PostReactionToggleView(generics.GenericAPIView):
    """Handle post reaction toggles with validated payloads."""

    serializer_class = ReactionToggleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    lookup_field = 'slug'

    def post(self, request, *args, **kwargs):
        """Add, change, or remove a reaction (like/dislike) from a post."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reaction_type = serializer.validated_data['reaction_type']

        post = get_object_or_404(self.get_queryset(), slug=kwargs.get('slug'))
        result = toggle_reaction(post, request.user, reaction_type)
        counts = result.get('counts', {})

        user_reaction = reaction_type if result['action'] in ['added', 'changed'] else None

        return Response(
            {
                'status': 'success',
                'action': result['action'],
                'likes_count': counts.get('like', 0),
                'dislikes_count': counts.get('dislike', 0),
                'user_reaction': user_reaction,
            },
            status=status.HTTP_200_OK,
        )
