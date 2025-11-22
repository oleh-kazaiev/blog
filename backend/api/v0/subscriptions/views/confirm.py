import uuid

from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from kafkabus import enqueue_subscription_request
from payments.models import Subscription


class SubscriptionConfirmView(APIView):
    """API view for confirming subscription payment (demo only)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Confirm subscription payment by simulating successful payment (LocalStripe limitation)."""
        sub = get_object_or_404(Subscription, user=request.user)

        if sub.status != 'pending':
            return Response({'error': 'Subscription is not pending'}, status=status.HTTP_400_BAD_REQUEST)

        if not sub.stripe_subscription_id:
            return Response({'error': 'No Payment Intent found'}, status=status.HTTP_400_BAD_REQUEST)

        enqueue_subscription_request(
            subscription_id=sub.id,
            user_id=sub.user_id,
            price_id=sub.price_id,
            idempotency_key=sub.idempotency_key or uuid.uuid4().hex,
        )

        sub.status = 'processing'
        sub.save(update_fields=['status', 'updated_at'])

        payment = sub.payments.order_by('-created_at').first()
        if payment:
            payment.status = 'processing'
            payment.save(update_fields=['status', 'updated_at'])

        return Response({'status': 'processing'})
