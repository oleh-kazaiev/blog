import logging
from typing import Any, Dict

from django.db import transaction
from django.utils import timezone

from blog.models import PostPurchase
from payments.models import Payment, Subscription
from payments.plans import get_plan_config
from users.notifications import (
    send_payment_failed_notification,
    send_payment_success_notification,
    send_subscription_activated_notification,
    send_subscription_cancelled_notification
)

logger = logging.getLogger(__name__)


def _as_str(d: Dict[str, Any], key: str) -> str:
    """Convert dict value to string, handling None."""
    val = d.get(key)
    return val if isinstance(val, str) else ('' if val is None else str(val))


def handle_payment_event(payload: Dict[str, Any]) -> None:
    """
    Apply a payment completion/failed/requires_action event to the database.

    Args:
        payload: Kafka event payload containing payment status update
    """
    payment_id = payload.get('payment_id')
    if not payment_id:
        logger.warning(f'Payment event missing payment_id: {payload}')
        return

    try:
        payment = Payment.objects.get(id=int(payment_id))
    except Payment.DoesNotExist:
        logger.warning(f'Payment {payment_id} not found for event')
        return

    event_type = payload.get('type')
    status = payload.get('status')

    # Track old status for logging
    old_status = payment.status

    # Determine new status based on event
    new_status = payment.status
    if event_type == 'PaymentCompleted' or status == 'succeeded':
        new_status = 'succeeded'
    elif event_type == 'PaymentRequiresAction' or status == 'requires_action':
        new_status = 'requires_action'
    elif event_type == 'PaymentFailed' or status == 'failed':
        new_status = 'failed'

    # Update payment record
    payment.status = new_status
    payment.stripe_payment_intent_id = _as_str(payload, 'stripe_payment_intent_id')
    payment.client_secret = _as_str(payload, 'client_secret')
    payment.error_message = _as_str(payload, 'error_message')

    with transaction.atomic():
        payment.save(update_fields=[
            'status',
            'stripe_payment_intent_id',
            'client_secret',
            'error_message',
            'updated_at',
        ])

        # Update associated purchase if exists
        try:
            purchase = payment.post_purchase
            old_purchase_status = purchase.status
        except PostPurchase.DoesNotExist:
            purchase = None
            old_purchase_status = None

        if purchase:
            if new_status == 'succeeded':
                purchase.status = 'succeeded'
                purchase.access_granted_at = timezone.now()
            elif new_status == 'failed':
                purchase.status = 'failed'
            else:
                purchase.status = 'pending'
            purchase.save(update_fields=['status', 'access_granted_at', 'updated_at'])

            # Log purchase state change
            if old_purchase_status != purchase.status:
                logger.info(
                    f'Purchase {purchase.id} status changed: {old_purchase_status} '
                    f'-> {purchase.status} (payment_id={payment.id})'
                )

    # Log payment state change
    if old_status != new_status:
        logger.info(
            f'Payment {payment.id} status changed: {old_status} -> {new_status} '
            f'(event_type={event_type})'
        )

        # Send email notification
        if new_status == 'succeeded':
            send_payment_success_notification(payment)
        elif new_status == 'failed':
            send_payment_failed_notification(payment)
    else:
        logger.debug(f'Payment {payment.id} status unchanged: {payment.status}')


def handle_subscription_event(payload: Dict[str, Any]) -> None:
    """
    Apply a subscription completion/failed/cancelled event to the database.

    Args:
        payload: Kafka event payload containing subscription status update
    """
    subscription_id = payload.get('subscription_id')
    if not subscription_id:
        logger.warning(f'Subscription event missing subscription_id: {payload}')
        return

    try:
        sub = Subscription.objects.get(id=int(subscription_id))
    except Subscription.DoesNotExist:
        logger.warning(f'Subscription {subscription_id} not found for event')
        return

    event_type = payload.get('type') or ''
    status = _as_str(payload, 'status') or sub.status

    # Track old state for logging
    old_status = sub.status
    old_valid_until = sub.valid_until

    # Determine new status based on event
    if event_type == 'SubscriptionCompleted':
        status = status or 'active'
        plan_config = get_plan_config(sub.plan)
        if plan_config:
            sub.valid_until = timezone.now() + plan_config['duration']
        if status not in ['active', 'trialing']:
            status = 'active'
    elif event_type == 'SubscriptionFailed':
        status = 'error'
    elif event_type == 'SubscriptionCancelled':
        status = 'canceled'

    # Update subscription record
    sub.status = status
    sub.stripe_subscription_id = _as_str(payload, 'stripe_subscription_id') or sub.stripe_subscription_id
    sub.error_message = _as_str(payload, 'error_message')

    payment = sub.payments.order_by('-created_at').first()
    payment_status = None
    if payment:
        if event_type == 'SubscriptionCompleted':
            payment_status = 'succeeded'
        elif event_type == 'SubscriptionFailed':
            payment_status = 'failed'
        elif event_type == 'SubscriptionCancelled':
            payment_status = 'canceled'

    with transaction.atomic():
        sub.save(update_fields=[
            'status',
            'stripe_subscription_id',
            'error_message',
            'valid_until',
            'updated_at',
        ])

        if payment and payment_status:
            payment.status = payment_status
            payment.save(update_fields=['status', 'updated_at'])

    # Log subscription state change
    if old_status != sub.status:
        logger.info(
            f'Subscription {sub.id} status changed: {old_status} -> {sub.status} '
            f'(event_type={event_type}, plan={sub.plan})'
        )

        # Send email notification
        if sub.status == 'active':
            send_subscription_activated_notification(sub)
        elif sub.status == 'canceled':
            send_subscription_cancelled_notification(sub)
    else:
        logger.debug(f'Subscription {sub.id} status unchanged: {sub.status}')

    # Log expiry changes
    if old_valid_until != sub.valid_until:
        logger.info(
            f'Subscription {sub.id} valid_until updated: {old_valid_until} -> {sub.valid_until}'
        )
