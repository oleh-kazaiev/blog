from rest_framework import serializers

from blog.models import PostReaction


class ReactionToggleSerializer(serializers.Serializer):
    """Validate reaction toggle payload."""

    reaction_type = serializers.ChoiceField(choices=[choice[0] for choice in PostReaction.REACTION_CHOICES])
