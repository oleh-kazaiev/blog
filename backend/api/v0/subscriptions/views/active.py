from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Subscription


class SubscriptionActiveView(APIView):
    """API view for retrieving user's active subscription."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's active subscription."""
        try:
            sub = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            return Response({'detail': 'No active subscription found'}, status=404)

        if sub.status != 'active':
            return Response({'detail': 'No active subscription found'}, status=404)

        return Response({
            'status': sub.status,
            'plan': sub.plan,
            'price_id': sub.price_id,
            'valid_until': sub.valid_until,
        })
