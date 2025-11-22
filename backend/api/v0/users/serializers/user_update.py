from rest_framework import serializers

from users.models import User


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating the current user's profile."""

    class Meta:
        """Meta configuration."""

        model = User
        fields = [
            'first_name',
            'last_name',
            'bio',
            'profile_picture',
            'website',
        ]
        extra_kwargs = {
            'profile_picture': {'required': False, 'allow_null': True},
        }

    def validate_profile_picture(self, value):
        """Validate profile picture file size and type."""
        if value:
            # Limit to 5MB
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError('Image file size must be less than 5MB')

            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f'Invalid image type. Allowed types: {", ".join(allowed_types)}'
                )

        return value
