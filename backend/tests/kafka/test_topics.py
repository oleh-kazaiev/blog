from unittest.mock import patch

from django.test import TestCase

from kafkabus import topics


class TestKafkaTopics(TestCase):
    """Test Kafka topic constants."""

    @patch.dict('os.environ', {}, clear=False)
    def test_default_payment_topics(self):
        """Test default payment topic values."""
        # Reload module to pick up environment changes
        import importlib
        importlib.reload(topics)

        self.assertEqual(topics.PAYMENTS_REQUEST, 'payments.request')
        self.assertEqual(topics.PAYMENTS_COMPLETED, 'payments.completed')
        self.assertEqual(topics.PAYMENTS_CANCELLED, 'payments.cancelled')

    @patch.dict('os.environ', {}, clear=False)
    def test_default_subscription_topics(self):
        """Test default subscription topic values."""
        import importlib
        importlib.reload(topics)

        self.assertEqual(topics.SUBSCRIPTIONS_REQUEST, 'subscriptions.request')
        self.assertEqual(topics.SUBSCRIPTIONS_COMPLETED, 'subscriptions.completed')
        self.assertEqual(topics.SUBSCRIPTIONS_CANCELLED, 'subscriptions.cancelled')

    @patch.dict('os.environ', {
        'KAFKA_TOPIC_PAYMENTS_REQUEST': 'custom.payments.request',
        'KAFKA_TOPIC_PAYMENTS_COMPLETED': 'custom.payments.completed',
        'KAFKA_TOPIC_PAYMENTS_CANCELLED': 'custom.payments.cancelled',
    }, clear=False)
    def test_custom_payment_topics_from_env(self):
        """Test that payment topics can be overridden via environment variables."""
        import importlib
        importlib.reload(topics)

        self.assertEqual(topics.PAYMENTS_REQUEST, 'custom.payments.request')
        self.assertEqual(topics.PAYMENTS_COMPLETED, 'custom.payments.completed')
        self.assertEqual(topics.PAYMENTS_CANCELLED, 'custom.payments.cancelled')

    @patch.dict('os.environ', {
        'KAFKA_TOPIC_SUBSCRIPTIONS_REQUEST': 'custom.subs.request',
        'KAFKA_TOPIC_SUBSCRIPTIONS_COMPLETED': 'custom.subs.completed',
        'KAFKA_TOPIC_SUBSCRIPTIONS_CANCELLED': 'custom.subs.cancelled',
    }, clear=False)
    def test_custom_subscription_topics_from_env(self):
        """Test that subscription topics can be overridden via environment variables."""
        import importlib
        importlib.reload(topics)

        self.assertEqual(topics.SUBSCRIPTIONS_REQUEST, 'custom.subs.request')
        self.assertEqual(topics.SUBSCRIPTIONS_COMPLETED, 'custom.subs.completed')
        self.assertEqual(topics.SUBSCRIPTIONS_CANCELLED, 'custom.subs.cancelled')

    def test_all_topics_are_strings(self):
        """Test that all topic constants are strings."""
        self.assertIsInstance(topics.PAYMENTS_REQUEST, str)
        self.assertIsInstance(topics.PAYMENTS_COMPLETED, str)
        self.assertIsInstance(topics.PAYMENTS_CANCELLED, str)
        self.assertIsInstance(topics.SUBSCRIPTIONS_REQUEST, str)
        self.assertIsInstance(topics.SUBSCRIPTIONS_COMPLETED, str)
        self.assertIsInstance(topics.SUBSCRIPTIONS_CANCELLED, str)

    def test_all_topics_are_non_empty(self):
        """Test that all topic constants are non-empty."""
        self.assertTrue(topics.PAYMENTS_REQUEST)
        self.assertTrue(topics.PAYMENTS_COMPLETED)
        self.assertTrue(topics.PAYMENTS_CANCELLED)
        self.assertTrue(topics.SUBSCRIPTIONS_REQUEST)
        self.assertTrue(topics.SUBSCRIPTIONS_COMPLETED)
        self.assertTrue(topics.SUBSCRIPTIONS_CANCELLED)
