from django.conf import settings
from django.db import models
from django.utils import timezone

from .post import Post


class Comment(models.Model):
    """Comment model for user comments on posts."""

    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=120, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    body = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        """Meta configuration."""

        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at'], name='comment_post_date_idx'),
        ]

    def __str__(self):
        """Return string representation."""
        author_display = (
            getattr(self.author, 'email', None)
            or self.email
            or self.name
            or 'Unknown'
        )
        return f'Comment by {author_display} on {self.post}'
