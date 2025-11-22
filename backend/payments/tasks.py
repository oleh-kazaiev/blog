from datetime import timedelta
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from celery import shared_task

from kafkabus import enqueue_payment_cancellation, enqueue_subscription_cancellation

from .models import Payment, Subscription


def _cancel_payments(payments: Iterable[Payment], reason: str) -> None:
    for payment in payments:
        if payment.status == 'canceled':
            continue
        payment.status = 'canceled'
        payment.error_message = reason
        payment.save(update_fields=['status', 'error_message', 'updated_at'])
        enqueue_payment_cancellation(payment_id=payment.id, reason=reason)


def _cancel_subscriptions(subscriptions: Iterable[Subscription], reason: str) -> None:
    for subscription in subscriptions:
        if subscription.status == 'canceled':
            continue
        subscription.status = 'canceled'
        subscription.error_message = reason
        subscription.save(update_fields=['status', 'error_message', 'updated_at'])
        enqueue_subscription_cancellation(subscription_id=subscription.id, reason=reason)


@shared_task()
def cancel_stale_payments(hours: int = 24) -> None:
    """Mark pending or in-progress payments older than the given hours as canceled."""
    cutoff = timezone.now() - timedelta(hours=hours)
    stale_qs = Payment.objects.filter(
        status__in=['pending', 'processing', 'requires_action'],
        created_at__lte=cutoff,
    )
    with transaction.atomic():
        stale = list(stale_qs.select_for_update())
    reason = f'Cancelled after exceeding {hours} hour window.'
    _cancel_payments(stale, reason=reason)


@shared_task()
def cancel_stale_subscriptions(hours: int = 24) -> None:
    """Mark pending subscriptions older than the given hours as canceled."""
    cutoff = timezone.now() - timedelta(hours=hours)
    stale_qs = Subscription.objects.filter(
        status__in=['pending', 'incomplete', 'trialing'],
        created_at__lte=cutoff,
    )
    with transaction.atomic():
        stale = list(stale_qs.select_for_update())
    reason = f'Cancelled after exceeding {hours} hour window.'
    _cancel_subscriptions(stale, reason=reason)
