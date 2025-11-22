import uuid
from datetime import datetime, timezone

from . import topics
from .producer import publish_event


def enqueue_payment_completed(
    *,
    payment_id: int,
    status: str,
    stripe_payment_intent_id: str,
    client_secret: str,
    error_message: str = '',
) -> None:
    """
    Enqueue a payment completion event to Kafka.

    Args:
        payment_id: Payment record ID
        status: Payment status (succeeded, failed, requires_action)
        stripe_payment_intent_id: Stripe Payment Intent ID
        client_secret: Stripe Client Secret (for frontend)
        error_message: Error message if failed
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'schema_version': 1,
        'occurred_at': datetime.now(timezone.utc).isoformat(),
        'type': 'PaymentCompleted' if status == 'succeeded' else 'PaymentFailed',
        'payment_id': payment_id,
        'status': status,
        'stripe_payment_intent_id': stripe_payment_intent_id,
        'client_secret': client_secret,
        'error_message': error_message,
    }
    publish_event(topics.PAYMENTS_COMPLETED, event, key=str(payment_id))


def enqueue_subscription_completed(
    *,
    subscription_id: str,
    status: str,
    stripe_subscription_id: str,
    client_secret: str,
    error_message: str = '',
) -> None:
    """
    Enqueue a subscription completion event to Kafka.

    Args:
        subscription_id: Subscription record ID
        status: Subscription status (active, incomplete, error)
        stripe_subscription_id: Stripe Subscription ID
        client_secret: Stripe Client Secret (for frontend)
        error_message: Error message if failed
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'schema_version': 1,
        'occurred_at': datetime.now(timezone.utc).isoformat(),
        'type': 'SubscriptionCompleted' if status == 'active' else 'SubscriptionFailed',
        'subscription_id': str(subscription_id),
        'status': status,
        'stripe_subscription_id': stripe_subscription_id,
        'client_secret': client_secret,
        'error_message': error_message,
    }
    publish_event(topics.SUBSCRIPTIONS_COMPLETED, event, key=str(subscription_id))
