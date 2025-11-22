from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Subscription


class SubscriptionCancelView(APIView):
    """API view for cancelling subscription."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Cancel the current user's subscription."""
        sub = get_object_or_404(Subscription, user=request.user)
        sub.status = 'canceled'
        sub.save(update_fields=['status', 'updated_at'])

        payment = sub.payments.order_by('-created_at').first()
        if payment:
            payment.status = 'canceled'
            payment.save(update_fields=['status', 'updated_at'])

        return Response({'status': sub.status})
