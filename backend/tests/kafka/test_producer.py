from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from kafka.errors import KafkaError
from kafkabus.producer import _on_send_error, _on_send_success, get_producer, publish_event


class TestKafkaProducer(TestCase):
    """Test Kafka producer infrastructure."""

    @patch('kafkabus.producer.KafkaProducer')
    def test_get_producer_creates_singleton(self, mock_kafka_producer):
        """Test that producer is created as singleton."""
        import kafkabus.producer as producer_module
        producer_module._ProducerSingleton._instance = None

        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # First call creates producer
        producer1 = get_producer()
        self.assertEqual(mock_kafka_producer.call_count, 1)
        self.assertEqual(producer1, mock_producer_instance)

        # Second call returns same instance
        producer2 = get_producer()
        self.assertEqual(mock_kafka_producer.call_count, 1)  # Not called again
        self.assertEqual(producer2, mock_producer_instance)
        self.assertEqual(producer1, producer2)

        # Cleanup
        producer_module._ProducerSingleton._instance = None

    @patch('kafkabus.producer.KafkaProducer')
    @override_settings(
        KAFKA_BOOTSTRAP_SERVERS='localhost:9092',
        KAFKA_PRODUCER_TIMEOUT=10,
    )
    def test_get_producer_configuration(self, mock_kafka_producer):
        """Test that producer is configured correctly."""
        import kafkabus.producer as producer_module
        producer_module._ProducerSingleton._instance = None

        get_producer()

        mock_kafka_producer.assert_called_once()
        call_kwargs = mock_kafka_producer.call_args[1]

        self.assertEqual(call_kwargs['bootstrap_servers'], 'localhost:9092')
        self.assertEqual(call_kwargs['linger_ms'], 10)
        self.assertEqual(call_kwargs['retries'], 3)
        self.assertEqual(call_kwargs['max_in_flight_requests_per_connection'], 1)
        self.assertEqual(call_kwargs['acks'], 'all')
        self.assertIsNotNone(call_kwargs['value_serializer'])
        self.assertIsNotNone(call_kwargs['key_serializer'])

        # Cleanup
        producer_module._ProducerSingleton._instance = None

    def test_on_send_success_logs_metadata(self):
        """Test success callback logs record metadata."""
        mock_metadata = MagicMock()
        mock_metadata.topic = 'test.topic'
        mock_metadata.partition = 0
        mock_metadata.offset = 123

        # Should not raise any exceptions
        _on_send_success(mock_metadata)

    def test_on_send_error_logs_exception(self):
        """Test error callback logs exception."""
        mock_exception = Exception('Test error')

        # Should not raise any exceptions
        _on_send_error(mock_exception)

    @patch('kafkabus.producer.get_producer')
    @override_settings(KAFKA_PRODUCER_TIMEOUT=10)
    def test_publish_event_success(self, mock_get_producer):
        """Test successful event publication."""
        mock_producer = MagicMock()
        mock_future = MagicMock()
        mock_future.get.return_value = None
        mock_producer.send.return_value = mock_future
        mock_get_producer.return_value = mock_producer

        payload = {'event_id': '123', 'type': 'TestEvent'}
        publish_event('test.topic', payload, key='123', wait_for_completion=True)

        mock_producer.send.assert_called_once_with(
            'test.topic',
            value=payload,
            key='123',
        )
        mock_future.add_callback.assert_called_once()
        mock_future.add_errback.assert_called_once()
        mock_future.get.assert_called_once_with(timeout=10)

    @patch('kafkabus.producer.get_producer')
    def test_publish_event_async_mode(self, mock_get_producer):
        """Test event publication in async mode (no wait)."""
        mock_producer = MagicMock()
        mock_future = MagicMock()
        mock_producer.send.return_value = mock_future
        mock_get_producer.return_value = mock_producer

        payload = {'event_id': '456', 'type': 'AsyncEvent'}
        publish_event('test.topic', payload, wait_for_completion=False)

        mock_producer.send.assert_called_once()
        mock_future.add_callback.assert_called_once()
        mock_future.add_errback.assert_called_once()
        mock_future.get.assert_not_called()  # Should not block in async mode

    @patch('kafkabus.producer.get_producer')
    @override_settings(KAFKA_PRODUCER_TIMEOUT=10)
    def test_publish_event_failure(self, mock_get_producer):
        """Test event publication failure handling."""
        mock_producer = MagicMock()
        mock_future = MagicMock()
        mock_future.get.side_effect = KafkaError('Connection failed')
        mock_producer.send.return_value = mock_future
        mock_get_producer.return_value = mock_producer

        payload = {'event_id': '789', 'type': 'FailEvent'}

        with self.assertRaises(KafkaError):
            publish_event('test.topic', payload, wait_for_completion=True)

    @patch('kafkabus.producer.get_producer')
    def test_publish_event_without_key(self, mock_get_producer):
        """Test event publication without partition key."""
        mock_producer = MagicMock()
        mock_future = MagicMock()
        mock_producer.send.return_value = mock_future
        mock_get_producer.return_value = mock_producer

        payload = {'event_id': '999'}
        publish_event('test.topic', payload, wait_for_completion=False)

        mock_producer.send.assert_called_once_with(
            'test.topic',
            value=payload,
            key=None,
        )

    @patch('kafkabus.producer.KafkaProducer')
    def test_value_serializer(self, mock_kafka_producer):
        """Test that value serializer converts dict to JSON bytes."""
        import kafkabus.producer as producer_module
        producer_module._ProducerSingleton._instance = None

        get_producer()

        call_kwargs = mock_kafka_producer.call_args[1]
        serializer = call_kwargs['value_serializer']

        # Test serialization
        test_value = {'key': 'value', 'number': 123}
        result = serializer(test_value)
        self.assertEqual(result, b'{"key": "value", "number": 123}')

        # Cleanup
        producer_module._ProducerSingleton._instance = None

    @patch('kafkabus.producer.KafkaProducer')
    def test_key_serializer(self, mock_kafka_producer):
        """Test that key serializer converts string to bytes."""
        import kafkabus.producer as producer_module
        producer_module._ProducerSingleton._instance = None

        get_producer()

        call_kwargs = mock_kafka_producer.call_args[1]
        serializer = call_kwargs['key_serializer']

        # Test with string key
        result = serializer('test-key')
        self.assertEqual(result, b'test-key')

        # Test with None key
        result_none = serializer(None)
        self.assertIsNone(result_none)

        # Cleanup
        producer_module._ProducerSingleton._instance = None
