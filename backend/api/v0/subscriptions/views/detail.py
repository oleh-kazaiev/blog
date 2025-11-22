import logging
import uuid

from django.shortcuts import get_object_or_404

import stripe
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from kafkabus import enqueue_subscription_request
from payments.models import Subscription

logger = logging.getLogger(__name__)


class SubscriptionDetailView(APIView):
    """API view for retrieving subscription details."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get subscription details for the current user."""
        sub = get_object_or_404(Subscription, user=request.user)

        if sub.status == 'pending' and sub.stripe_subscription_id and sub.client_secret:
            try:
                payment_intent = stripe.PaymentIntent.retrieve(sub.stripe_subscription_id)
                logger.info(f'Subscription {sub.id} Payment Intent status: {payment_intent.status}')

                if payment_intent.status == 'succeeded':
                    logger.info(
                        f'Payment succeeded for subscription {sub.id}, enqueueing Kafka event'
                    )
                    enqueue_subscription_request(
                        subscription_id=sub.id,
                        user_id=sub.user_id,
                        price_id=sub.price_id,
                        idempotency_key=sub.idempotency_key or uuid.uuid4().hex,
                    )
                    sub.status = 'processing'
                    sub.save(update_fields=['status', 'updated_at'])
                else:
                    logger.debug(
                        f'Payment Intent for subscription {sub.id} '
                        f'not yet succeeded: {payment_intent.status}',
                    )
            except Exception:  # pragma: no cover - log only
                logger.exception(
                    f'Failed to retrieve Payment Intent for subscription {sub.id}'
                )

        response_data = {
            'status': sub.status,
            'plan': sub.plan,
            'price_id': sub.price_id,
            'valid_until': sub.valid_until,
            'error_message': sub.error_message,
        }

        if sub.status in ['error', 'incomplete_expired', 'canceled']:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data)
