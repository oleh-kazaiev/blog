from rest_framework import permissions, status, viewsets

from api.v0.users.serializers.user import UserSerializer
from api.v0.users.serializers.user_read import UserReadSerializer
from users.models import NotificationPreferences, User


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user registration and profile management
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Allow unauthenticated access for registration
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Regular users can only see their own profile
        """
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        """Use read serializer for safe methods; write serializer for create/update."""
        if self.action in ['list', 'retrieve']:
            return UserReadSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """Create user and initialize notification preferences."""
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(pk=response.data['id'])
            NotificationPreferences.objects.create(user=user)
        return response
