from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment


class PaymentDetailView(APIView):
    """API view for retrieving payment details."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        """Get payment details for a specific payment."""
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        data = {
            'payment_id': payment.id,
            'status': payment.status,
            'amount': payment.amount,
            'currency': payment.currency,
            'client_secret': payment.client_secret,
            'stripe_payment_intent_id': payment.stripe_payment_intent_id,
            'error_message': payment.error_message,
        }
        return Response(data)
