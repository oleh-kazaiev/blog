import logging
import os
import threading
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

import stripe
from fastapi import FastAPI

from .kafka import consumer as kafka_consumer
from .kafka import events as kafka_events
from .kafka import producer as kafka_producer
from .kafka import topics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('payment')

KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_CONSUMER_GROUP = os.environ.get('KAFKA_CONSUMER_GROUP', 'payment-service')
KAFKA_AUTO_OFFSET_RESET = os.environ.get('KAFKA_AUTO_OFFSET_RESET', 'earliest')

STRIPE_API_BASE = os.getenv('STRIPE_API_BASE')
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
if STRIPE_API_BASE:
    stripe.api_base = STRIPE_API_BASE


def process_payment(payload: Dict[str, Any]) -> None:
    payment_id = int(payload.get('payment_id') or 0)
    amount_raw = payload.get('amount')
    stripe_payment_intent_id = payload.get('stripe_payment_intent_id')

    if amount_raw is None:
        raise ValueError(f'Missing amount in payment payload {payload!r}')
    try:
        amount = int(amount_raw)
    except Exception as exc:  # noqa: BLE001 - malformed payload
        raise ValueError(f'Invalid amount {amount_raw!r} in payment payload {payload!r}') from exc

    currency = payload.get('currency', 'usd')
    idempotency_key = payload.get('idempotency_key') or uuid.uuid4().hex

    try:
        if stripe_payment_intent_id:
            # If ID is provided, retrieve it
            pi = stripe.PaymentIntent.retrieve(stripe_payment_intent_id)

            # For LocalStripe/test mode: attach a test payment method before confirming
            if pi.status != 'succeeded':
                # Check if payment method is already attached
                if not pi.payment_method:
                    logger.info(f'Attaching test payment method to PaymentIntent {stripe_payment_intent_id}')
                    # Create a test payment method for LocalStripe
                    payment_method = stripe.PaymentMethod.create(
                        type='card',
                        card={
                            'number': '4242424242424242',
                            'exp_month': 12,
                            'exp_year': 2030,
                            'cvc': '123',
                        },
                    )
                    # Attach payment method to PaymentIntent
                    pi = stripe.PaymentIntent.modify(
                        stripe_payment_intent_id,
                        payment_method=payment_method.id,
                    )

                # Confirm the PaymentIntent
                logger.info(f'Confirming PaymentIntent {stripe_payment_intent_id}')
                pi = stripe.PaymentIntent.confirm(stripe_payment_intent_id)
        else:
            # Otherwise create and confirm immediately (demo path)
            pi = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                confirm=True,
                automatic_payment_methods={'enabled': True},
                metadata={'payment_id': str(payment_id)},
                idempotency_key=idempotency_key,
            )

        status = pi.status or 'requires_action'
        status_str = (
            'succeeded'
            if status == 'succeeded'
            else ('requires_action' if status == 'requires_action' else 'failed')
        )

        kafka_events.enqueue_payment_completed(
            payment_id=payment_id,
            status=status_str,
            stripe_payment_intent_id=pi.id,
            client_secret=getattr(pi, 'client_secret', ''),
            error_message='',
        )
    except Exception as exc:  # noqa: BLE001 - propagate failure to clients
        logger.exception(f'Payment processing error for payment_id={payment_id}')
        kafka_events.enqueue_payment_completed(
            payment_id=payment_id,
            status='failed',
            stripe_payment_intent_id='',
            client_secret='',
            error_message=str(exc),
        )


def process_subscription(payload: Dict[str, Any]) -> None:
    subscription_id = int(payload.get('subscription_id') or 0)
    price_id = payload.get('price_id')
    if price_id is None:
        raise ValueError(f'Missing price_id in subscription payload {payload!r}')
    user_id = payload.get('user_id')
    idempotency_key = payload.get('idempotency_key') or uuid.uuid4().hex

    try:
        # Create a test token for LocalStripe
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": "12",
                "exp_year": "2030",
                "cvc": "123",
            }
        )
        customer = stripe.Customer.create(
            metadata={'user_id': str(user_id)},
            source=token.id
        )
        # Use 'plan' instead of 'items' for compatibility with LocalStripe
        # Remove unsupported parameters for LocalStripe
        sub = stripe.Subscription.create(
            customer=customer.id,
            plan=price_id,  # type: ignore
            metadata={
                'subscription_id': str(subscription_id),
                'user_id': str(user_id),
            },
            idempotency_key=idempotency_key,
        )

        status = sub.status or 'incomplete'
        latest_invoice = getattr(sub, 'latest_invoice', None)
        intent = getattr(latest_invoice, 'payment_intent', None)
        client_secret = getattr(intent, 'client_secret', '') if intent else ''

        kafka_events.enqueue_subscription_completed(
            subscription_id=subscription_id,
            status=status,
            stripe_subscription_id=sub.id,
            client_secret=client_secret,
            error_message='',
        )
    except Exception as exc:  # noqa: BLE001 - propagate failure events
        logger.exception(
            f'Subscription processing error for subscription_id={subscription_id}. '
            f'Payload: {payload}'
        )
        kafka_events.enqueue_subscription_completed(
            subscription_id=subscription_id,
            status='error',
            stripe_subscription_id='',
            client_secret='',
            error_message=str(exc),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('=== Payment service starting up ===')
    logger.info(f'Kafka bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}')
    logger.info(f'Consumer group: {KAFKA_CONSUMER_GROUP}')

    # Create Kafka producer and consumer
    logger.info('Creating Kafka producer...')
    producer = kafka_producer.get_producer()
    logger.info('Kafka producer created')

    logger.info('Creating Kafka consumer...')
    consumer = kafka_consumer.create_consumer(
        KAFKA_BOOTSTRAP_SERVERS,
        KAFKA_CONSUMER_GROUP,
        KAFKA_AUTO_OFFSET_RESET,
    )
    logger.info('Kafka consumer created')

    # Map topics to their handler functions
    handlers = {
        topics.PAYMENTS_REQUEST: process_payment,
        topics.SUBSCRIPTIONS_REQUEST: process_subscription,
    }
    logger.info(f'Mapped topics: {list(handlers.keys())}')

    # Start consumer thread
    logger.info('Starting consumer thread...')
    stop_event = threading.Event()
    consumer_thread = kafka_consumer.start_consumer_thread(consumer, handlers, stop_event)
    logger.info('Consumer thread started, waiting for messages')

    try:
        yield
    finally:
        logger.info('=== Payment service shutting down ===')
        # Shutdown consumer
        kafka_consumer.shutdown_consumer(consumer, stop_event, consumer_thread)

        # Flush and close producer
        try:
            producer.flush()
        except Exception:  # noqa: BLE001 - best effort flush
            logger.exception('Failed to flush Kafka producer during shutdown')
        kafka_producer.close_producer()
        logger.info('Shutdown complete')


app = FastAPI(title='payment-svc', lifespan=lifespan)


@app.get('/healthz')
async def healthz():
    return {'ok': True}
