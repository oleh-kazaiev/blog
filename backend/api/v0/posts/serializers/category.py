from rest_framework import serializers

from blog.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""

    class Meta:
        """Meta configuration."""

        model = Category
        fields = ['id', 'name', 'slug']
