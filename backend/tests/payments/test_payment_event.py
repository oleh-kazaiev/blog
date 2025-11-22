from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from blog.models import Category, Post, PostPurchase
from payments.models import Payment, Subscription
from payments.payment_event import _as_str, handle_payment_event, handle_subscription_event

User = get_user_model()


class TestAsStrHelper(TestCase):
    """Test _as_str helper function."""

    def test_as_str_with_string_value(self):
        """Test _as_str returns string value as-is."""
        result = _as_str({'key': 'value'}, 'key')
        self.assertEqual(result, 'value')

    def test_as_str_with_none_value(self):
        """Test _as_str returns empty string for None."""
        result = _as_str({'key': None}, 'key')
        self.assertEqual(result, '')

    def test_as_str_with_missing_key(self):
        """Test _as_str returns empty string for missing key."""
        result = _as_str({}, 'key')
        self.assertEqual(result, '')

    def test_as_str_with_non_string_value(self):
        """Test _as_str converts non-string values to string."""
        result = _as_str({'key': 123}, 'key')
        self.assertEqual(result, '123')


class TestHandlePaymentEvent(TestCase):
    """Test payment event handler."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.payment = Payment.objects.create(
            user=self.user,
            amount=1000,
            currency='usd',
            status='pending',
        )

    def test_handle_payment_event_missing_payment_id(self):
        """Test handler with missing payment_id logs warning and returns."""
        payload = {'type': 'PaymentCompleted'}

        with patch('payments.payment_event.logger') as mock_logger:
            handle_payment_event(payload)
            mock_logger.warning.assert_called_once()

    def test_handle_payment_event_nonexistent_payment(self):
        """Test handler with non-existent payment_id logs warning and returns."""
        payload = {'payment_id': 99999, 'type': 'PaymentCompleted'}

        with patch('payments.payment_event.logger') as mock_logger:
            handle_payment_event(payload)
            mock_logger.warning.assert_called_once()

    def test_handle_payment_completed_event(self):
        """Test handling payment completion event."""
        payload = {
            'payment_id': self.payment.id,
            'type': 'PaymentCompleted',
            'status': 'succeeded',
            'stripe_payment_intent_id': 'pi_123',
            'client_secret': 'secret_123',
            'error_message': '',
        }

        handle_payment_event(payload)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'succeeded')
        self.assertEqual(self.payment.stripe_payment_intent_id, 'pi_123')
        self.assertEqual(self.payment.client_secret, 'secret_123')
        self.assertEqual(self.payment.error_message, '')

    def test_handle_payment_failed_event(self):
        """Test handling payment failure event."""
        payload = {
            'payment_id': self.payment.id,
            'type': 'PaymentFailed',
            'status': 'failed',
            'error_message': 'Card declined',
        }

        handle_payment_event(payload)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
        self.assertEqual(self.payment.error_message, 'Card declined')

    def test_handle_payment_requires_action_event(self):
        """Test handling payment requires action event."""
        payload = {
            'payment_id': self.payment.id,
            'type': 'PaymentRequiresAction',
            'status': 'requires_action',
            'client_secret': 'secret_456',
        }

        handle_payment_event(payload)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'requires_action')
        self.assertEqual(self.payment.client_secret, 'secret_456')

    def test_handle_payment_event_with_purchase_success(self):
        """Test payment event updates associated purchase on success."""
        category = Category.objects.create(name='Test Category')
        post = Post.objects.create(
            title='Test Post',
            content='Content',
            author=self.user,
            category=category,
            is_paid=True,
            price_cents=1000,
        )
        purchase = PostPurchase.objects.create(
            user=self.user,
            post=post,
            payment=self.payment,
            status='pending',
        )

        payload = {
            'payment_id': self.payment.id,
            'type': 'PaymentCompleted',
            'status': 'succeeded',
        }

        handle_payment_event(payload)

        purchase.refresh_from_db()
        self.assertEqual(purchase.status, 'succeeded')
        self.assertIsNotNone(purchase.access_granted_at)

    def test_handle_payment_event_with_purchase_failure(self):
        """Test payment event updates associated purchase on failure."""
        category = Category.objects.create(name='Test Category')
        post = Post.objects.create(
            title='Test Post',
            content='Content',
            author=self.user,
            category=category,
            is_paid=True,
            price_cents=1000,
        )
        purchase = PostPurchase.objects.create(
            user=self.user,
            post=post,
            payment=self.payment,
            status='pending',
        )

        payload = {
            'payment_id': self.payment.id,
            'type': 'PaymentFailed',
            'status': 'failed',
        }

        handle_payment_event(payload)

        purchase.refresh_from_db()
        self.assertEqual(purchase.status, 'failed')

    def test_handle_payment_event_status_logging(self):
        """Test that status changes are logged."""
        payload = {
            'payment_id': self.payment.id,
            'type': 'PaymentCompleted',
            'status': 'succeeded',
        }

        with patch('payments.payment_event.logger') as mock_logger:
            handle_payment_event(payload)
            mock_logger.info.assert_called()


class TestHandleSubscriptionEvent(TestCase):
    """Test subscription event handler."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='sub@example.com',
            password='testpass123',
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan='monthly',
            status='incomplete',
        )

    def test_handle_subscription_event_missing_subscription_id(self):
        """Test handler with missing subscription_id logs warning and returns."""
        payload = {'type': 'SubscriptionCompleted'}

        with patch('payments.payment_event.logger') as mock_logger:
            handle_subscription_event(payload)
            mock_logger.warning.assert_called_once()

    def test_handle_subscription_event_nonexistent_subscription(self):
        """Test handler with non-existent subscription_id logs warning and returns."""
        payload = {'subscription_id': 99999, 'type': 'SubscriptionCompleted'}

        with patch('payments.payment_event.logger') as mock_logger:
            handle_subscription_event(payload)
            mock_logger.warning.assert_called_once()

    @patch('payments.payment_event.get_plan_config')
    def test_handle_subscription_completed_event(self, mock_get_plan):
        """Test handling subscription completion event."""
        mock_get_plan.return_value = {'duration': timedelta(days=30)}

        payload = {
            'subscription_id': self.subscription.id,
            'type': 'SubscriptionCompleted',
            'status': 'active',
            'stripe_subscription_id': 'sub_123',
        }

        before_time = timezone.now()
        handle_subscription_event(payload)
        after_time = timezone.now()

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'active')
        self.assertEqual(self.subscription.stripe_subscription_id, 'sub_123')
        self.assertIsNotNone(self.subscription.valid_until)

        # Check that valid_until is approximately 30 days from now
        expected_expiry = before_time + timedelta(days=30)
        self.assertGreater(self.subscription.valid_until, expected_expiry - timedelta(seconds=5))
        self.assertLess(self.subscription.valid_until, after_time + timedelta(days=30, seconds=5))

    def test_handle_subscription_failed_event(self):
        """Test handling subscription failure event."""
        payload = {
            'subscription_id': self.subscription.id,
            'type': 'SubscriptionFailed',
            'error_message': 'Payment method declined',
        }

        handle_subscription_event(payload)

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'error')
        self.assertEqual(self.subscription.error_message, 'Payment method declined')

    def test_handle_subscription_cancelled_event(self):
        """Test handling subscription cancellation event."""
        payload = {
            'subscription_id': self.subscription.id,
            'type': 'SubscriptionCancelled',
        }

        handle_subscription_event(payload)

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'canceled')

    def test_handle_subscription_event_status_logging(self):
        """Test that status changes are logged."""
        payload = {
            'subscription_id': self.subscription.id,
            'type': 'SubscriptionCompleted',
            'status': 'active',
        }

        with patch('payments.payment_event.logger') as mock_logger:
            handle_subscription_event(payload)
            mock_logger.info.assert_called()

    @patch('payments.payment_event.get_plan_config')
    def test_handle_subscription_event_with_none_plan_config(self, mock_get_plan):
        """Test handling subscription event when plan config is None."""
        mock_get_plan.return_value = None

        payload = {
            'subscription_id': self.subscription.id,
            'type': 'SubscriptionCompleted',
            'status': 'active',
        }

        old_valid_until = self.subscription.valid_until
        handle_subscription_event(payload)

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'active')
        # valid_until should not be set if plan_config is None
        self.assertEqual(self.subscription.valid_until, old_valid_until)
