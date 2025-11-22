from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

from django.test import TestCase

from kafkabus.events import (
    enqueue_payment_cancellation,
    enqueue_payment_request,
    enqueue_subscription_cancellation,
    enqueue_subscription_request
)


class TestMessaging(TestCase):
    """Test messaging business logic for payment/subscription events."""

    @patch('kafkabus.events.publish_event')
    @patch('kafkabus.events.topics')
    def test_enqueue_payment_request(self, mock_topics, mock_publish):
        """Test enqueuing a payment request event."""
        mock_topics.PAYMENTS_REQUEST = 'payments.request'

        enqueue_payment_request(
            payment_id=123,
            user_id=456,
            amount=1500,
            currency='usd',
            idempotency_key='test-key-123',
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args

        # Check topic
        self.assertEqual(call_args[0][0], 'payments.request')

        # Check event payload
        event = call_args[0][1]
        self.assertEqual(event['type'], 'PaymentRequested')
        self.assertEqual(event['payment_id'], 123)
        self.assertEqual(event['user_id'], '456')  # Converted to string for JSON
        self.assertEqual(event['amount'], 1500)
        self.assertEqual(event['currency'], 'usd')
        self.assertEqual(event['idempotency_key'], 'test-key-123')
        self.assertEqual(event['schema_version'], 1)

        # Check UUID is valid
        UUID(event['event_id'])

        # Check timestamp format
        datetime.fromisoformat(event['occurred_at'])

        # Check key
        self.assertEqual(call_args[1]['key'], '123')

    @patch('kafkabus.events.publish_event')
    @patch('kafkabus.events.topics')
    def test_enqueue_subscription_request(self, mock_topics, mock_publish):
        """Test enqueuing a subscription request event."""
        mock_topics.SUBSCRIPTIONS_REQUEST = 'subscriptions.request'

        enqueue_subscription_request(
            subscription_id=789,
            user_id=456,
            price_id='price_123',
            idempotency_key='sub-key-789',
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args

        # Check topic
        self.assertEqual(call_args[0][0], 'subscriptions.request')

        # Check event payload
        event = call_args[0][1]
        self.assertEqual(event['type'], 'SubscriptionRequested')
        self.assertEqual(event['subscription_id'], 789)
        self.assertEqual(event['user_id'], '456')  # Converted to string for JSON
        self.assertEqual(event['price_id'], 'price_123')
        self.assertEqual(event['idempotency_key'], 'sub-key-789')
        self.assertEqual(event['schema_version'], 1)

        # Check UUID is valid
        UUID(event['event_id'])

        # Check timestamp format
        datetime.fromisoformat(event['occurred_at'])

        # Check key
        self.assertEqual(call_args[1]['key'], '789')

    @patch('kafkabus.events.publish_event')
    @patch('kafkabus.events.topics')
    def test_enqueue_payment_cancellation(self, mock_topics, mock_publish):
        """Test enqueuing a payment cancellation event."""
        mock_topics.PAYMENTS_CANCELLED = 'payments.cancelled'

        enqueue_payment_cancellation(
            payment_id=123,
            reason='User requested cancellation',
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args

        # Check topic
        self.assertEqual(call_args[0][0], 'payments.cancelled')

        # Check event payload
        event = call_args[0][1]
        self.assertEqual(event['type'], 'PaymentCancelled')
        self.assertEqual(event['payment_id'], 123)
        self.assertEqual(event['reason'], 'User requested cancellation')
        self.assertEqual(event['schema_version'], 1)

        # Check UUID is valid
        UUID(event['event_id'])

        # Check timestamp format
        datetime.fromisoformat(event['occurred_at'])

        # Check key
        self.assertEqual(call_args[1]['key'], '123')

    @patch('kafkabus.events.publish_event')
    @patch('kafkabus.events.topics')
    def test_enqueue_subscription_cancellation(self, mock_topics, mock_publish):
        """Test enqueuing a subscription cancellation event."""
        mock_topics.SUBSCRIPTIONS_CANCELLED = 'subscriptions.cancelled'

        enqueue_subscription_cancellation(
            subscription_id=789,
            reason='Expired payment method',
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args

        # Check topic
        self.assertEqual(call_args[0][0], 'subscriptions.cancelled')

        # Check event payload
        event = call_args[0][1]
        self.assertEqual(event['type'], 'SubscriptionCancelled')
        self.assertEqual(event['subscription_id'], 789)
        self.assertEqual(event['reason'], 'Expired payment method')
        self.assertEqual(event['schema_version'], 1)

        # Check UUID is valid
        UUID(event['event_id'])

        # Check timestamp format
        datetime.fromisoformat(event['occurred_at'])

        # Check key
        self.assertEqual(call_args[1]['key'], '789')

    @patch('kafkabus.events.publish_event')
    @patch('kafkabus.events.uuid.uuid4')
    @patch('kafkabus.events.datetime')
    def test_event_id_and_timestamp_generation(self, mock_datetime, mock_uuid, mock_publish):
        """Test that event_id and occurred_at are properly generated."""
        # Mock UUID and datetime
        mock_uuid.return_value = 'test-uuid-123'
        mock_now = datetime(2024, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        enqueue_payment_request(
            payment_id=1,
            user_id=2,
            amount=100,
            currency='usd',
            idempotency_key='key',
        )

        event = mock_publish.call_args[0][1]
        self.assertEqual(event['event_id'], 'test-uuid-123')
        self.assertEqual(event['occurred_at'], '2024-01-15T12:30:45+00:00')
