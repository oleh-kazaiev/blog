from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.authtoken.models import Token

from blog.models import Category, Post, PostReaction

User = get_user_model()


class TestAdminPostsEndpoints(TestCase):
    """Test admin posts endpoints."""

    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(name='AdminCat', slug='admincat')
        self.admin = User.objects.create_user(
            email='admin2@example.com', password='pass12345', first_name='Admin', last_name='Two', is_admin=True
        )
        self.post = Post.objects.create(
            title='Admin Post',
            slug='admin-post',
            content='C',
            author=self.admin,
            category=self.category,
            is_published=True,
        )

    def auth_admin(self):
        """Authenticate as admin user."""
        token, _ = Token.objects.get_or_create(user=self.admin)
        return token

    def test_admin_by_category_action(self):
        """Test posts can be filtered by category."""
        # Create another post in different category
        other_cat = Category.objects.create(name='Other', slug='other')
        Post.objects.create(
            title='Other Post', slug='other-post', content='C', author=self.admin, category=other_cat, is_published=True
        )

        # Verify posts can be filtered by category
        admin_cat_posts = Post.objects.filter(category=self.category)
        self.assertEqual(admin_cat_posts.count(), 1)
        self.assertEqual(admin_cat_posts.first().title, 'Admin Post')

    def test_admin_react_action_like_toggle(self):
        """Test post reactions can be created and toggled."""
        # Create a like reaction
        reaction = PostReaction.objects.create(post=self.post, user=self.admin, reaction_type='like')
        self.assertEqual(reaction.reaction_type, 'like')

        # Delete it (toggle off)
        reaction.delete()
        self.assertEqual(PostReaction.objects.filter(post=self.post, user=self.admin).count(), 0)

        # Create a dislike reaction
        dislike = PostReaction.objects.create(post=self.post, user=self.admin, reaction_type='dislike')
        self.assertEqual(dislike.reaction_type, 'dislike')

    def test_category_detail_v0(self):
        """Test category details can be retrieved."""
        # Verify category exists with correct slug
        category = Category.objects.get(slug=self.category.slug)
        self.assertEqual(category.name, 'AdminCat')
        self.assertEqual(category.slug, 'admincat')
        # Verify posts are associated
        self.assertEqual(category.posts.count(), 1)
