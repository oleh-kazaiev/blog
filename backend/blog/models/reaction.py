from django.conf import settings
from django.db import models

from .post import Post


class PostReaction(models.Model):
    """Model for tracking user reactions to posts."""

    REACTION_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    post = models.ForeignKey(Post, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reactions', on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta configuration."""

        unique_together = ('post', 'user')
        indexes = [
            models.Index(fields=['post', 'reaction_type'], name='reaction_post_type_idx'),
        ]

    def __str__(self):
        """Return string representation."""
        return f'{self.user} {self.reaction_type} {self.post}'
