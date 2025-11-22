# noqa: A005
from django.conf import settings
from django.db import models


class Email(models.Model):
    """Store sent emails for user viewing."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emails',
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField()
    to_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        """Meta options for Email model."""

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f'{self.subject} - {self.to_email}'
