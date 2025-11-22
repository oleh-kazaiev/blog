from rest_framework import permissions
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v0.users.serializers.user_me import UserMeSerializer
from api.v0.users.serializers.user_update import UserUpdateSerializer


class UserMeView(APIView):
    """Return and update the current authenticated user's profile."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """Return the current user's profile."""
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Update the current user's profile (partial update)."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return updated user data
        response_serializer = UserMeSerializer(request.user)
        return Response(response_serializer.data)
