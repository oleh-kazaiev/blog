from django.contrib.auth import get_user_model

from rest_framework.test import APIRequestFactory, APITestCase

from api.v0.posts.serializers.category import CategorySerializer
from api.v0.posts.serializers.comment_create import CommentCreateSerializer
from api.v0.posts.serializers.detail import PostDetailSerializer
from api.v0.posts.serializers.list import PostListSerializer
from api.v0.posts.serializers.reaction import PostReactionSerializer
from api.v0.posts.serializers.write import PostCreateUpdateSerializer
from blog.models import Category, Post, PostReaction

User = get_user_model()


class TestPostCategoryCommentSerializers(APITestCase):
    """Test post, category and comment serializers."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='a@example.com', password='pass12345', first_name='A', last_name='U'
        )
        self.other = User.objects.create_user(
            email='b@example.com', password='pass12345', first_name='B', last_name='U'
        )
        self.category = Category.objects.create(name='Tech')
        self.post = Post.objects.create(
            title='Hello', content='World', author=self.user, category=self.category, is_published=True
        )

    def test_category_serializer_fields(self):
        """Test category serializer fields."""
        data = CategorySerializer(self.category).data
        self.assertEqual(data['id'], self.category.id)
        self.assertEqual(data['name'], 'Tech')
        self.assertEqual(data['slug'], self.category.slug)

    def test_post_list_serializer_counts_and_user_reaction(self):
        """Test post list serializer counts and user reaction."""
        # Add reactions
        PostReaction.objects.create(post=self.post, user=self.user, reaction_type='like')
        PostReaction.objects.create(post=self.post, user=self.other, reaction_type='dislike')

        # Anonymous request => user_reaction None
        from django.contrib.auth.models import AnonymousUser
        anon_request = self.factory.get('/')
        anon_request.user = AnonymousUser()
        data = PostListSerializer(self.post, context={'request': anon_request}).data
        self.assertEqual(data['likes_count'], 1)
        self.assertEqual(data['dislikes_count'], 1)
        self.assertIsNone(data['user_reaction'])

        # Authenticated request => user_reaction reflects user's own
        auth_request = self.factory.get('/')
        auth_request.user = self.user
        data = PostListSerializer(self.post, context={'request': auth_request}).data
        self.assertEqual(data['user_reaction'], 'like')

    def test_post_detail_serializer_comments_and_counts(self):
        """Test post detail serializer comments and counts."""
        # Create an approved and an unapproved comment (approval is default True)
        approved_request = self.factory.post('/')
        approved_request.user = self.user
        approved_context = {'post_id': self.post.id, 'request': approved_request}
        s = CommentCreateSerializer(data={'body': 'hi'}, context=approved_context)
        self.assertTrue(s.is_valid(), s.errors)
        s.save()

        # Unapproved comment should not show up
        unapproved_request = self.factory.post('/')
        unapproved_request.user = self.user
        unapproved_context = {'post_id': self.post.id, 'request': unapproved_request}
        s2 = CommentCreateSerializer(data={'body': 'no'}, context=unapproved_context)
        self.assertTrue(s2.is_valid(), s2.errors)
        c2 = s2.save()
        c2.is_approved = False
        c2.save(update_fields=['is_approved'])

        req = self.factory.get('/')
        req.user = self.user
        data = PostDetailSerializer(self.post, context={'request': req}).data
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['likes_count'], 0)
        self.assertEqual(data['dislikes_count'], 0)

    def test_post_write_serializer_sets_author_from_request(self):
        """Test post write serializer sets author from request."""
        req = self.factory.post('/')
        req.user = self.user
        s = PostCreateUpdateSerializer(
            data={'title': 'New', 'content': 'C', 'excerpt': 'E', 'category': self.category.id},
            context={'request': req},
        )
        self.assertTrue(s.is_valid(), s.errors)
        post = s.save()
        self.assertEqual(post.author, self.user)

    def test_comment_serializer_sets_author_when_authenticated(self):
        """Test comment serializer sets author when authenticated."""
        req = self.factory.post('/')
        req.user = self.user
        ctx = {'post_id': self.post.id, 'request': req}
        s = CommentCreateSerializer(data={'body': 'b'}, context=ctx)
        self.assertTrue(s.is_valid(), s.errors)
        c = s.save()
        self.assertEqual(c.author, self.user)

    def test_post_reaction_serializer_fields(self):
        """Test post reaction serializer fields."""
        reaction = PostReaction.objects.create(post=self.post, user=self.user, reaction_type='like')
        data = PostReactionSerializer(reaction).data
        self.assertEqual(data['id'], reaction.id)
        self.assertEqual(data['post'], self.post.id)
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['reaction_type'], 'like')
