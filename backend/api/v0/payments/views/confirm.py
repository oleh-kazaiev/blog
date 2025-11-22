import uuid

from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from kafkabus import enqueue_payment_request
from payments.models import Payment


class PaymentConfirmView(APIView):
    """API view for confirming payment (demo only)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        """Confirm payment by enqueuing to payment service (LocalStripe limitation)."""
        payment = get_object_or_404(Payment, pk=pk, user=request.user)

        if payment.status not in ['pending', 'requires_action', 'failed']:
            return Response(
                {'error': f'Payment cannot be confirmed (current status: {payment.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not payment.stripe_payment_intent_id:
            return Response(
                {'error': 'No Payment Intent found. Please create payment first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enqueue to Kafka for payment service to process
        enqueue_payment_request(
            payment_id=payment.id,
            user_id=payment.user.id,
            amount=payment.amount,
            currency=payment.currency,
            idempotency_key=payment.idempotency_key or uuid.uuid4().hex,
            stripe_payment_intent_id=payment.stripe_payment_intent_id,
        )

        # Update status to processing
        payment.status = 'processing'
        payment.save(update_fields=['status', 'updated_at'])

        # Update associated purchase status if exists
        if hasattr(payment, 'post_purchase'):
            purchase = payment.post_purchase
            purchase.status = 'processing'
            purchase.save(update_fields=['status'])

        return Response({'status': 'processing', 'payment_id': payment.id})
