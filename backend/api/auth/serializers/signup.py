from rest_framework import serializers

from users.models import User


class UserSignupSerializer(serializers.ModelSerializer):
    """Serializer for user sign-up."""

    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        """Meta configuration."""

        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
        ]

    def validate(self, data):
        """Ensure password confirmation matches."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'password': "Passwords don't match."})
        data.pop('confirm_password', None)
        return data

    def create(self, validated_data):
        """Create a user with a hashed password."""
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
