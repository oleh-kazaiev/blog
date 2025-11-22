import json
import logging
import threading
import time
from typing import Any, Callable, Dict, Mapping

from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

from .topics import PAYMENTS_REQUEST, SUBSCRIPTIONS_REQUEST

logger = logging.getLogger(__name__)


def create_consumer(
    bootstrap_servers: str,
    group_id: str,
    auto_offset_reset: str = 'earliest',
) -> KafkaConsumer:
    """
    Create Kafka consumer with retry logic for startup resilience.

    Args:
        bootstrap_servers: Kafka broker addresses
        group_id: Consumer group ID
        auto_offset_reset: Where to start consuming if no offset exists

    Returns:
        KafkaConsumer: Configured Kafka consumer instance
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            logger.info(f'Connecting to Kafka {bootstrap_servers} (attempt {attempt})')
            consumer = KafkaConsumer(
                PAYMENTS_REQUEST,
                SUBSCRIPTIONS_REQUEST,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
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
    handlers: Dict[str, Callable[[Dict[str, Any]], None]],
    stop_event: threading.Event,
) -> None:
    """
    Main event loop for consuming and processing Kafka messages.

    Args:
        consumer: KafkaConsumer instance
        handlers: Dict mapping topic names to handler functions
        stop_event: Threading event to signal shutdown
    """
    logger.info('Consumer loop started, entering poll loop')
    try:
        while not stop_event.is_set():
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
                    except Exception:  # noqa: BLE001 - already logged inside handlers
                        logger.exception(
                            f'Unhandled error while processing message from topic={topic}'
                        )
    finally:
        logger.info('Consumer loop exiting, closing consumer')
        try:
            consumer.close()
        except Exception:  # noqa: BLE001 - best effort close
            logger.exception('Error closing Kafka consumer')


def start_consumer_thread(
    consumer: KafkaConsumer,
    handlers: Mapping[str, Callable[[Dict[str, Any]], None]],
    stop_event: threading.Event,
) -> threading.Thread:
    """
    Start Kafka consumer in a background thread.

    Args:
        consumer: KafkaConsumer instance
        handlers: Dict mapping topic names to handler functions
        stop_event: Threading event to signal shutdown

    Returns:
        threading.Thread: Started consumer thread
    """
    consumer_thread = threading.Thread(
        target=consume_loop,
        name='kafka-consumer',
        args=(consumer, handlers, stop_event),
        daemon=True,
    )
    consumer_thread.start()
    logger.info('Kafka consumer thread started')
    return consumer_thread


def shutdown_consumer(
    consumer: KafkaConsumer,
    stop_event: threading.Event,
    consumer_thread: threading.Thread,
    timeout: float = 5.0,
) -> None:
    """
    Gracefully shutdown Kafka consumer.

    Args:
        consumer: KafkaConsumer instance
        stop_event: Threading event to signal shutdown
        consumer_thread: Consumer thread to join
        timeout: Maximum time to wait for thread to finish
    """
    stop_event.set()
    try:
        wakeup = getattr(consumer, 'wakeup', None)
        if callable(wakeup):
            wakeup()
    except Exception:  # noqa: BLE001 - best effort wakeup
        logger.debug('Consumer wakeup failed during shutdown', exc_info=True)

    consumer_thread.join(timeout=timeout)
    logger.info('Kafka consumer shut down')
