from rest_framework import serializers

from users.models import User

from ...emails.serializers.email import EmailSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration and profile management."""

    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    emails = EmailSerializer(many=True, read_only=True)

    class Meta:
        """Meta configuration."""

        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'password', 'confirm_password',
            'bio', 'profile_picture', 'website', 'is_admin', 'full_name', 'emails'
        ]
        read_only_fields = ['id', 'full_name', 'is_admin', 'emails']

    def validate(self, data):
        """Validate password fields match."""
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({'password': "Passwords don't match."})
            data.pop('confirm_password')
        return data

    def create(self, validated_data):
        """Create a user with hashed password."""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """Update user instance with optional password change."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
