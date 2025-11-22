import uuid

import stripe
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v0.subscriptions.serializers.create import SubscriptionCreateSerializer
from payments.models import Payment, Subscription
from payments.plans import get_plan_config


class SubscriptionCreateView(APIView):
    """API view for creating subscription records."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Create a new subscription and create Stripe Payment Intent."""
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan_key = serializer.validated_data.get('plan') or 'month'
        plan_config = get_plan_config(plan_key)
        if not plan_config:
            return Response({'error': 'Invalid subscription plan'}, status=status.HTTP_400_BAD_REQUEST)

        price_id = plan_config['stripe_price_id'] or f'plan_{plan_key}'
        price_cents = plan_config['price_cents']
        idempotency_key = uuid.uuid4().hex

        sub, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={
                'price_id': price_id,
                'plan': plan_key,
                'status': 'pending',
                'idempotency_key': idempotency_key,
            },
        )

        if not created:
            # Reset state for a new billing cycle
            sub.price_id = price_id
            sub.plan = plan_key
            sub.status = 'pending'
            sub.idempotency_key = idempotency_key
            sub.error_message = ''
            sub.save(update_fields=['price_id', 'plan', 'status', 'idempotency_key', 'error_message', 'updated_at'])

        payment = Payment.objects.create(
            user=request.user,
            subscription=sub,
            amount=price_cents,
            currency='usd',
            status='pending',
            payment_type='subscription',
            idempotency_key=idempotency_key,
        )

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=price_cents,
                currency='usd',
                metadata={
                    'subscription_id': str(sub.id),
                    'user_id': str(request.user.id),
                    'user_email': request.user.email,
                    'plan': plan_key,
                    'payment_id': str(payment.id),
                },
                idempotency_key=idempotency_key,
            )

            sub.stripe_subscription_id = payment_intent.id
            sub.client_secret = payment_intent.client_secret
            sub.save(update_fields=['stripe_subscription_id', 'client_secret'])

            payment.stripe_payment_intent_id = payment_intent.id
            payment.client_secret = payment_intent.client_secret
            payment.save(update_fields=['stripe_payment_intent_id', 'client_secret'])

        except Exception as e:
            sub.status = 'error'
            sub.error_message = str(e)
            sub.save(update_fields=['status', 'error_message'])
            return Response(
                {'error': f'Failed to create payment intent: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({
            'status': sub.status,
            'plan': sub.plan,
            'client_secret': sub.client_secret,
            'amount': price_cents,
            'currency': 'usd',
            'payment_id': payment.id,
        }, status=status.HTTP_201_CREATED)
