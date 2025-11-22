from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import NotificationPreferences

from ..serializers.preferences import NotificationPreferencesSerializer


class NotificationPreferencesView(RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's notification preferences."""

    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return or create preferences for the current user."""
        prefs, _ = NotificationPreferences.objects.get_or_create(user=self.request.user)
        return prefs
