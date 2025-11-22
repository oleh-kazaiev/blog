import atexit
import json
import logging
import os
import threading
import time
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable

logger = logging.getLogger(__name__)

DEFAULT_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
PRODUCER_TIMEOUT = float(os.getenv('KAFKA_PRODUCER_TIMEOUT', '10'))


def create_producer(bootstrap_servers: str, max_retries: int = 30) -> KafkaProducer:
    """
    Create Kafka producer with retry logic for startup resilience.

    Args:
        bootstrap_servers: Kafka bootstrap servers (e.g., 'kafka:9092')
        max_retries: Maximum number of connection attempts

    Returns:
        KafkaProducer: Configured Kafka producer instance

    Raises:
        NoBrokersAvailable: If unable to connect after max_retries
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f'Attempting to connect to Kafka at {bootstrap_servers} '
                f'(attempt {attempt}/{max_retries})'
            )
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda value: json.dumps(value).encode('utf-8'),
                key_serializer=lambda key: key.encode('utf-8') if key is not None else None,
                linger_ms=10,
                retries=3,
                max_in_flight_requests_per_connection=1,
                acks='all',
            )
            logger.info('Successfully connected to Kafka!')
            return producer
        except NoBrokersAvailable:
            if attempt < max_retries:
                wait_time = min(attempt * 2, 10)  # Exponential backoff, max 10s
                logger.warning(f'Kafka not available yet. Retrying in {wait_time}s...')
                time.sleep(wait_time)
            else:
                logger.error('Failed to connect to Kafka after maximum retries')
                raise
    raise NoBrokersAvailable('Kafka connection failed')


class _ProducerSingleton:
    """Thread-safe singleton wrapper for KafkaProducer."""

    _lock = threading.Lock()
    _instance: Optional[KafkaProducer] = None

    @classmethod
    def instance(cls) -> KafkaProducer:
        """Return a shared KafkaProducer instance, creating it once."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = create_producer(DEFAULT_BOOTSTRAP)
                    atexit.register(lambda: cls._instance and cls._instance.close())
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Close the shared producer (used during graceful shutdown)."""
        with cls._lock:
            if cls._instance is not None:
                try:
                    cls._instance.close()
                finally:
                    cls._instance = None


def get_producer() -> KafkaProducer:
    """Public helper to retrieve the shared Kafka producer."""
    return _ProducerSingleton.instance()


def close_producer() -> None:
    """Close the shared producer (used during graceful shutdown)."""
    _ProducerSingleton.close()


def _on_send_success(record_metadata):
    """
    Log successful message delivery.

    Args:
        record_metadata: Kafka record metadata containing topic, partition, offset
    """
    logger.debug(
        f'Message delivered to topic={record_metadata.topic} '
        f'partition={record_metadata.partition} offset={record_metadata.offset}'
    )


def _on_send_error(exception):
    """
    Log failed message delivery.

    Args:
        exception: Exception that occurred during message delivery
    """
    logger.exception(f'Failed to deliver message: {exception}')


def _send(
    topic: str,
    payload: Dict[str, Any],
    *,
    key: Optional[str] = None,
    wait_for_completion: bool = True,
) -> None:
    """Send an event to Kafka, optionally waiting for confirmation."""
    producer = get_producer()
    future = producer.send(topic, value=payload, key=key)

    # Add async callbacks for monitoring
    future.add_callback(_on_send_success)
    future.add_errback(_on_send_error)

    # For critical events (payments), wait for confirmation with timeout
    if wait_for_completion:
        try:
            future.get(timeout=PRODUCER_TIMEOUT)
        except KafkaError:
            logger.exception(f'Failed to publish event to topic {topic}')
            raise


def publish_event(
    topic: str,
    payload: Dict[str, Any],
    *,
    key: Optional[str] = None,
    wait_for_completion: bool = True,
) -> None:
    """
    Publish a JSON event to the given Kafka topic.

    Args:
        topic: Kafka topic name
        payload: Event payload dictionary (will be JSON serialized)
        key: Optional partition key for message ordering
        wait_for_completion: If True, blocks until message is sent (default for critical events).
                           If False, uses async callbacks only (for non-critical events).

    Raises:
        KafkaError: If message delivery fails and wait_for_completion=True
    """
    _send(topic, payload, key=key, wait_for_completion=wait_for_completion)
