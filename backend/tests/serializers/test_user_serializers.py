from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from api.auth.serializers.login import UserLoginSerializer
from api.v0.users.serializers.user import UserSerializer
from api.v0.users.serializers.user_brief import UserBriefSerializer

User = get_user_model()


class TestUserSerializers(APITestCase):
    """Test user serializers."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='u@example.com', password='pass12345', first_name='U', last_name='Ser', is_admin=True
        )

    def test_user_brief_serializer(self):
        """Test user brief serializer."""
        data = UserBriefSerializer(self.user).data
        self.assertEqual(data['id'], str(self.user.id))
        self.assertEqual(data['email'], 'u@example.com')
        self.assertEqual(data['first_name'], 'U')
        self.assertEqual(data['last_name'], 'Ser')
        self.assertEqual(data['full_name'], 'U Ser')

    def test_user_serializer_password_mismatch_validation(self):
        """Test user serializer password mismatch validation."""
        s = UserSerializer(data={
            'email': 'x@example.com',
            'first_name': 'X',
            'last_name': 'Y',
            'password': 'abc',
            'confirm_password': 'zzz',
        })
        self.assertFalse(s.is_valid())
        self.assertIn('password', s.errors)

    def test_user_serializer_create_sets_password_and_hides_fields(self):
        """Test user serializer create sets password and hides fields."""
        s = UserSerializer(data={
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'pass12345',
            'confirm_password': 'pass12345',
        })
        self.assertTrue(s.is_valid(), s.errors)
        user = s.save()
        self.assertTrue(user.check_password('pass12345'))
        data = UserSerializer(user).data
        self.assertNotIn('password', data)
        self.assertNotIn('confirm_password', data)
        self.assertEqual(data['email'], 'new@example.com')
        self.assertFalse(data['is_admin'])

    def test_user_serializer_update_handles_password(self):
        """Test user serializer update handles password."""
        s = UserSerializer(
            instance=self.user,
            data={'password': 'newpass', 'confirm_password': 'newpass'},
            partial=True,
        )
        self.assertTrue(s.is_valid(), s.errors)
        user = s.save()
        self.assertTrue(user.check_password('newpass'))

    def test_user_login_serializer_basic_validation(self):
        """Test user login serializer basic validation."""
        s = UserLoginSerializer(data={'email': 'u@example.com', 'password': 'pass12345'})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data['email'], 'u@example.com')
