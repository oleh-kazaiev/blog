import uuid
from datetime import datetime, timezone
from typing import Optional

from . import topics
from .producer import publish_event


def enqueue_payment_request(
    *, payment_id: int, user_id, amount: int, currency: str, idempotency_key: str,
    stripe_payment_intent_id: Optional[str] = None,
) -> None:
    """
    Enqueue a payment request event to Kafka.

    Args:
        payment_id: Payment record ID
        user_id: User ID who initiated the payment (int or UUID)
        amount: Payment amount in cents
        currency: Currency code (e.g., 'usd')
        idempotency_key: Unique key to prevent duplicate processing
        stripe_payment_intent_id: Optional Stripe Payment Intent ID if already created
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'schema_version': 1,
        'occurred_at': datetime.now(timezone.utc).isoformat(),
        'type': 'PaymentRequested',
        'payment_id': payment_id,
        'user_id': str(user_id),
        'amount': amount,
        'currency': currency,
        'idempotency_key': idempotency_key,
    }
    if stripe_payment_intent_id:
        event['stripe_payment_intent_id'] = stripe_payment_intent_id
    publish_event(topics.PAYMENTS_REQUEST, event, key=str(payment_id))


def enqueue_subscription_request(
    *, subscription_id, user_id, price_id: str, idempotency_key: str,
) -> None:
    """
    Enqueue a subscription request event to Kafka.

    Args:
        subscription_id: Subscription record ID
        user_id: User ID who initiated the subscription
        price_id: Stripe price ID for the subscription plan
        idempotency_key: Unique key to prevent duplicate processing
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'schema_version': 1,
        'occurred_at': datetime.now(timezone.utc).isoformat(),
        'type': 'SubscriptionRequested',
        'subscription_id': subscription_id,
        'user_id': str(user_id),
        'price_id': price_id,
        'idempotency_key': idempotency_key,
    }
    publish_event(topics.SUBSCRIPTIONS_REQUEST, event, key=str(subscription_id))


def enqueue_payment_cancellation(*, payment_id: int, reason: str) -> None:
    """
    Enqueue a payment cancellation event to Kafka.

    Args:
        payment_id: Payment record ID to cancel
        reason: Reason for cancellation
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'schema_version': 1,
        'occurred_at': datetime.now(timezone.utc).isoformat(),
        'type': 'PaymentCancelled',
        'payment_id': payment_id,
        'reason': reason,
    }
    publish_event(topics.PAYMENTS_CANCELLED, event, key=str(payment_id))


def enqueue_subscription_cancellation(*, subscription_id: int, reason: str) -> None:
    """
    Enqueue a subscription cancellation event to Kafka.

    Args:
        subscription_id: Subscription record ID to cancel
        reason: Reason for cancellation
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'schema_version': 1,
        'occurred_at': datetime.now(timezone.utc).isoformat(),
        'type': 'SubscriptionCancelled',
        'subscription_id': subscription_id,
        'reason': reason,
    }
    publish_event(topics.SUBSCRIPTIONS_CANCELLED, event, key=str(subscription_id))
