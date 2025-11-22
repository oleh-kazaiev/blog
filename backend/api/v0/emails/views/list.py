from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import Email

from ..serializers.email import EmailSerializer


class EmailListView(ListAPIView):
    """List emails for authenticated user."""

    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return emails for current user."""
        return Email.objects.filter(user=self.request.user)
