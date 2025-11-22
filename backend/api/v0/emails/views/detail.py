from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import Email

from ..serializers.email import EmailSerializer


class EmailDetailView(RetrieveDestroyAPIView):
    """View/delete email for authenticated user."""

    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return emails for current user."""
        return Email.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Get email and mark as read."""
        instance = self.get_object()
        if not instance.read:
            instance.read = True
            instance.save(update_fields=['read'])
        return super().retrieve(request, *args, **kwargs)
