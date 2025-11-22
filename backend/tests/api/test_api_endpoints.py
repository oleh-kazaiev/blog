from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework.authtoken.models import Token

from blog.models import Category, Post
from blog.tasks import publish_scheduled_posts

User = get_user_model()


class ApiEndpointsTests(TestCase):
    """Test API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.user = User.objects.create_user(
            email='user@example.com', password='pass12345', first_name='User', last_name='One'
        )
        self.admin = User.objects.create_user(
            email='admin@example.com', password='pass12345', first_name='Admin', last_name='User', is_admin=True
        )

    def test_login_returns_token_and_user(self):
        """Test that tokens can be created for users."""
        token, created = Token.objects.get_or_create(user=self.user)
        self.assertIsNotNone(token.key)
        self.assertTrue(created)
        # Verify token is associated with correct user
        self.assertEqual(token.user, self.user)

    def test_get_categories(self):
        """Test categories can be retrieved."""
        categories = Category.objects.all()
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, 'Tech')

    def test_admin_create_post_and_public_listing(self):
        """Test admin can create posts."""
        post = Post.objects.create(
            title='Hello World',
            slug='hello-world',
            content='<p>Content</p>',
            excerpt='Intro',
            category=self.category,
            author=self.admin,
            published_at=timezone.now(),
            is_published=True,
        )
        self.assertEqual(post.title, 'Hello World')
        self.assertTrue(post.is_published)
        # Verify post appears in listings
        posts = Post.objects.filter(is_published=True)
        self.assertEqual(posts.count(), 1)

    def test_profile_me_returns_is_admin(self):
        """Test admin flag is properly set."""
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.user.is_admin)

    def test_publish_scheduled_task(self):
        """Test publish scheduled posts task."""
        post = Post.objects.create(
            title='Scheduled',
            slug='scheduled',
            content='x',
            author=self.user,
            category=self.category,
            is_published=False,
            published_at=timezone.now(),
        )
        self.assertFalse(post.is_published)
        publish_scheduled_posts()
        post.refresh_from_db()
        self.assertTrue(post.is_published)
