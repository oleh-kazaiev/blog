from django.contrib.auth import authenticate

from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from api.auth.serializers.login import UserLoginSerializer
from api.v0.users.serializers.user_read import UserReadSerializer


class LoginView(APIView):
    """Standalone login view."""

    authentication_classes: list[type] = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Token-based login endpoint without session auth."""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(username=email, password=password)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserReadSerializer(user).data})
