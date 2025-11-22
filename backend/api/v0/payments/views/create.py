import uuid

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v0.payments.serializers.create import PaymentCreateSerializer
from payments.models import Payment


class PaymentCreateView(APIView):
    """API view for creating payment records (legacy endpoint)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Create a new payment record.

        NOTE: This is a minimal payment record creation endpoint.
        For post purchases, use the /posts/{slug}/purchase/ endpoint instead.
        The payment will be processed when PaymentConfirmView is called.
        """
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data.get('currency', 'usd')

        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            currency=currency,
            status='pending',
            idempotency_key=str(uuid.uuid4()).replace('-', ''),
        )

        return Response({
            'payment_id': payment.id,
            'status': payment.status,
        }, status=status.HTTP_201_CREATED)
