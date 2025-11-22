import json
import logging
import os
import signal
import sys
import threading
import time
from typing import Any, Callable, Dict, Iterable, Mapping

from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

# Configure Django before importing project modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.db import close_old_connections  # noqa: E402

from kafkabus import topics  # noqa: E402
from payments.payment_event import handle_payment_event, handle_subscription_event  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
)


def create_consumer(
    bootstrap_servers: str,
    group_id: str,
    topics: Iterable[str],
) -> KafkaConsumer:
    """
    Create Kafka consumer with retry logic for startup resilience.

    Args:
        bootstrap_servers: Kafka broker addresses
        group_id: Consumer group ID
        topics: List of Kafka topics to subscribe to

    Returns:
        KafkaConsumer instance

    Raises:
        NoBrokersAvailable: If unable to connect after max retries
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            logger.info(f'Connecting to Kafka {bootstrap_servers} (attempt {attempt})')
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=False,  # Manual commit for better error handling
                value_deserializer=lambda value: json.loads(value.decode('utf-8')) if value else {},
                consumer_timeout_ms=1000,
            )
            logger.info('Connected to Kafka')
            return consumer
        except NoBrokersAvailable:
            wait_time = min(attempt * 2, 30)
            logger.warning(f'Kafka unavailable; retrying in {wait_time}s')
            time.sleep(wait_time)


def consume_loop(
    consumer: KafkaConsumer,
    handlers: Mapping[str, Callable[[Dict[str, Any]], None]],
    stop_event: threading.Event,
) -> None:
    """
    Consume and process Kafka messages in a loop.

    Args:
        consumer: KafkaConsumer instance
        handlers: Mapping mapping topic names to handler functions
        stop_event: Threading event to signal shutdown
    """
    logger.info('Payment event consumer started')

    while not stop_event.is_set():
        close_old_connections()
        try:
            records = consumer.poll(timeout_ms=1000)
        except KafkaError:
            logger.exception('Kafka poll error; retrying shortly')
            time.sleep(1)
            continue

        if not records:
            continue

        for messages in records.values():
            for message in messages:
                topic = message.topic
                payload = message.value if isinstance(message.value, dict) else {}

                if not payload:
                    logger.warning(f'Skipping empty payload from topic={topic}')
                    consumer.commit()
                    continue

                handler = handlers.get(topic)
                if not handler:
                    logger.warning(f'Received message for unexpected topic={topic}')
                    consumer.commit()
                    continue

                try:
                    logger.info(f'Processing message from topic={topic}')
                    handler(payload)
                    consumer.commit()
                    logger.info(f'Handler completed for topic={topic}')
                except Exception:
                    logger.exception(
                        f'Error handling message from {message.topic} (offset: {message.offset}). '
                        'Message will be reprocessed on restart.'
                    )

    logger.info('Stopping consumer...')
    consumer.close()


def main() -> None:
    """Start the Kafka consumer for payment events."""
    handlers = {
        topics.PAYMENTS_COMPLETED: handle_payment_event,
        topics.SUBSCRIPTIONS_COMPLETED: handle_subscription_event,
    }
    group_id = os.environ['PAYMENT_EVENTS_CONSUMER_GROUP']
    bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS

    consumer = create_consumer(
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        topics=list(handlers.keys()),
    )

    stop_event = threading.Event()

    def _handle_shutdown(signum, frame):  # noqa: ANN001
        logger.info(f'Signal {signum} received, shutting down...')
        stop_event.set()

    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    try:
        consume_loop(consumer, handlers, stop_event)
    finally:
        logger.info('Payment event consumer exited')


if __name__ == '__main__':
    try:
        main()
    except Exception:  # pragma: no cover
        logger.exception('Fatal error in payment event consumer')
        sys.exit(1)
