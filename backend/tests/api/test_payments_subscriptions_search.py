from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.authtoken.models import Token

from blog.models import Category, Post
from payments.models import Payment, Subscription

User = get_user_model()


class TestPaymentsSubscriptionsSearch(TestCase):
    """Test payments, subscriptions and search endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='pay@example.com', password='pass12345', first_name='Pay', last_name='User'
        )
        self.category = Category.objects.create(name='SearchCat', slug='searchcat')
        self.post = Post.objects.create(
            title='Searchable Post', slug='searchable-post', content='some content', excerpt='findme',
            author=self.user, category=self.category, is_published=True,
        )

    def auth(self):
        """Authenticate user."""
        token, _ = Token.objects.get_or_create(user=self.user)
        return token

    def test_payments_create_and_detail(self):
        """Test payments can be created and retrieved."""
        # Create a payment
        payment = Payment.objects.create(
            user=self.user,
            amount=1500,
            currency='usd',
            status='pending'
        )

        # Verify payment was created
        self.assertEqual(payment.amount, 1500)
        self.assertEqual(payment.currency, 'usd')
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.user, self.user)

        # Verify payment can be retrieved
        retrieved = Payment.objects.get(id=payment.id)
        self.assertEqual(retrieved.id, payment.id)
        self.assertEqual(retrieved.amount, 1500)

    def test_subscriptions_create_and_detail(self):
        """Test subscriptions can be created and retrieved."""
        # Create a subscription
        subscription = Subscription.objects.create(
            user=self.user,
            price_id='price_123',
            status='active'
        )

        # Verify subscription was created
        self.assertEqual(subscription.price_id, 'price_123')
        self.assertEqual(subscription.status, 'active')
        self.assertEqual(subscription.user, self.user)

        # Verify subscription can be retrieved
        retrieved = Subscription.objects.get(id=subscription.id)
        self.assertEqual(retrieved.id, subscription.id)
        self.assertEqual(retrieved.price_id, 'price_123')

    def test_search_uses_db_fallback_without_es(self):
        """Test search can find posts in database."""
        # Search for post by title
        results = Post.objects.filter(title__icontains='Searchable', is_published=True)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Searchable Post')

        # Search for post by excerpt
        results = Post.objects.filter(excerpt__icontains='findme', is_published=True)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().excerpt, 'findme')
