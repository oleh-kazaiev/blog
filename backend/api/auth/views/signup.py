from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from api.auth.serializers.signup import UserSignupSerializer
from api.v0.users.serializers.user_read import UserReadSerializer
from users.models import NotificationPreferences


class SignupView(APIView):
    """Standalone sign-up view."""

    authentication_classes: list[type] = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Register a new user and return token + profile."""
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        NotificationPreferences.objects.create(user=user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserReadSerializer(user).data}, status=status.HTTP_201_CREATED)
