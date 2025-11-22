from django.core.mail.backends.base import BaseEmailBackend

from .models import Email, User


class DatabaseEmailBackend(BaseEmailBackend):
    """Email backend that stores emails in the database per user."""

    def send_messages(self, email_messages):
        """Save email messages to database."""
        num_sent = 0
        for message in email_messages:
            for recipient in message.to:
                # Find user by email
                try:
                    user = User.objects.get(email=recipient)
                    Email.objects.create(
                        user=user,
                        subject=message.subject,
                        body=message.body,
                        from_email=message.from_email,
                        to_email=recipient,
                    )
                    num_sent += 1
                except User.DoesNotExist:
                    # If recipient not found, skip (or log)
                    pass
        return num_sent
