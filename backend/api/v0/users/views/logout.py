from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class UserLogoutView(APIView):
    """Logout by deleting the user's token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Delete the user's auth token."""
        if request.user.is_authenticated:
            request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
