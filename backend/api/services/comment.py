from rest_framework import status

from api.v0.posts.serializers.comment import CommentSerializer
from api.v0.posts.serializers.comment_create import CommentCreateSerializer
from users.notifications import send_comment_notification


def add_comment_to_post(post, request, data):
    """
    Add a comment to a post.

    Args:
        post: The Post object.
        request: The request object (can be None).
        data: The request data (dict).

    Returns:
        tuple: (response_data, status_code)
    """
    data = data.copy()

    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        default_name = (
            user.get_full_name()
            or getattr(user, 'username', None)
            or user.email
            or 'Anonymous'
        )
        data.setdefault('name', default_name)
        data.setdefault('email', user.email or '')

    context = {'post_id': post.id, 'request': request}

    serializer = CommentCreateSerializer(data=data, context=context)
    if serializer.is_valid():
        comment = serializer.save()
        send_comment_notification(comment)
        response_data = CommentSerializer(comment).data
        return response_data, status.HTTP_201_CREATED

    return serializer.errors, status.HTTP_400_BAD_REQUEST
