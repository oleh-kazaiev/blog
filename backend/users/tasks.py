"""Celery tasks for user-related operations including email notifications."""
import logging

from django.conf import settings
from django.core.mail import send_mail

from celery import shared_task

from blog.models import Comment, Post
from payments.models import Payment, Subscription

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_email_task(
    self,
    subject: str,
    message: str,
    recipient_email: str,
    fail_silently: bool = True
) -> bool:
    """Send email via Celery task.

    Args:
        subject: Email subject
        message: Email body
        recipient_email: Recipient email address
        fail_silently: Whether to suppress exceptions

    Returns:
        True if email sent successfully
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=fail_silently,
        )
        logger.info(f'Sent email to {recipient_email}: {subject}')
        return True
    except Exception as exc:
        logger.error(f'Failed to send email to {recipient_email}: {subject}')
        if not fail_silently:
            raise self.retry(exc=exc) from exc
        return False


@shared_task
def send_comment_notification_task(comment_id: int) -> bool:
    """Send notification when someone comments on user's post."""
    try:
        comment = Comment.objects.select_related('post__author').get(id=comment_id)
    except Comment.DoesNotExist:
        logger.error(f'Comment {comment_id} does not exist')
        return False

    post = comment.post
    author = post.author

    if not author:
        logger.info(f'Post {post.id} has no author, skipping notification')
        return False

    if (
        hasattr(author, 'notification_preferences')
        and not author.notification_preferences.comment_on_post
    ):
        logger.info(f'User {author.id} disabled comment_on_post notifications')
        return False

    subject = f'New comment on your post: {post.title}'
    message = (
        f'Hi {author.first_name or author.email},\n\n'
        f'{comment.name} commented on your post "{post.title}":\n\n'
        f'{comment.body}\n\n'
        f'Best regards,\nYour Blog'
    )

    send_email_task.delay(subject, message, author.email, fail_silently=False)
    return True


@shared_task
def send_reaction_notification_task(post_id: int, reactor_email: str, action: str) -> bool:
    """Send notification when someone reacts to user's post."""
    try:
        post = Post.objects.select_related('author').get(id=post_id)
    except Post.DoesNotExist:
        logger.error(f'Post {post_id} does not exist')
        return False

    author = post.author

    if not author:
        return False

    if (
        hasattr(author, 'notification_preferences')
        and not author.notification_preferences.post_reaction
    ):
        return False

    subject = f'Someone reacted to your post: {post.title}'
    message = (
        f'Hi {author.first_name or author.email},\n\n'
        f'{reactor_email} {action} on your post "{post.title}".\n\n'
        f'Best regards,\nYour Blog'
    )

    send_email_task.delay(subject, message, author.email)
    return True


@shared_task
def send_payment_success_notification_task(payment_id: int) -> bool:
    """Send notification when payment succeeds."""
    try:
        payment = Payment.objects.select_related('user', 'post').get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error(f'Payment {payment_id} does not exist')
        return False

    user = payment.user

    if (
        hasattr(user, 'notification_preferences')
        and not user.notification_preferences.payment_successful
    ):
        return False

    post_title = payment.post.title if payment.post else 'Unknown Post'

    subject = 'Payment Successful'
    message = (
        f'Hi {user.first_name or user.email},\n\n'
        f'Your payment for "{post_title}" was successful.\n'
        f'Amount: ${payment.amount / 100:.2f} {payment.currency.upper()}\n\n'
        f'You now have access to the content.\n\n'
        f'Best regards,\nYour Blog'
    )

    send_email_task.delay(subject, message, user.email)
    return True


@shared_task
def send_payment_failed_notification_task(payment_id: int) -> bool:
    """Send notification when payment fails."""
    try:
        payment = Payment.objects.select_related('user', 'post').get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error(f'Payment {payment_id} does not exist')
        return False

    user = payment.user

    if (
        hasattr(user, 'notification_preferences')
        and not user.notification_preferences.payment_failed
    ):
        return False

    post_title = payment.post.title if payment.post else 'Unknown Post'

    subject = 'Payment Failed'
    message = (
        f'Hi {user.first_name or user.email},\n\n'
        f'Your payment for "{post_title}" has failed.\n'
        f'Amount: ${payment.amount / 100:.2f} {payment.currency.upper()}\n'
        f'Error: {payment.error_message or "Unknown error"}\n\n'
        f'Please try again or contact support.\n\n'
        f'Best regards,\nYour Blog'
    )

    send_email_task.delay(subject, message, user.email)
    return True


@shared_task
def send_subscription_activated_notification_task(subscription_id: int) -> bool:
    """Send notification when subscription is activated."""
    try:
        subscription = Subscription.objects.select_related('user').get(id=subscription_id)
    except Subscription.DoesNotExist:
        logger.error(f'Subscription {subscription_id} does not exist')
        return False

    user = subscription.user

    if (
        hasattr(user, 'notification_preferences')
        and not user.notification_preferences.subscription_activated
    ):
        return False

    subject = 'Subscription Activated'
    valid_until = subscription.valid_until
    valid_until_str = valid_until.strftime('%Y-%m-%d %H:%M') if valid_until else 'N/A'
    message = (
        f'Hi {user.first_name or user.email},\n\n'
        f'Your {subscription.plan} subscription has been activated.\n'
        f'Valid until: {valid_until_str}\n\n'
        f'Thank you for subscribing!\n\n'
        f'Best regards,\nYour Blog'
    )

    send_email_task.delay(subject, message, user.email)
    return True


@shared_task
def send_subscription_cancelled_notification_task(subscription_id: int) -> bool:
    """Send notification when subscription is cancelled."""
    try:
        subscription = Subscription.objects.select_related('user').get(id=subscription_id)
    except Subscription.DoesNotExist:
        logger.error(f'Subscription {subscription_id} does not exist')
        return False

    user = subscription.user

    if (
        hasattr(user, 'notification_preferences')
        and not user.notification_preferences.subscription_cancelled
    ):
        return False

    subject = 'Subscription Cancelled'
    message = (
        f'Hi {user.first_name or user.email},\n\n'
        f'Your {subscription.plan} subscription has been cancelled.\n\n'
        f'We hope to see you again soon!\n\n'
        f'Best regards,\nYour Blog'
    )

    send_email_task.delay(subject, message, user.email)
    return True


@shared_task
def send_subscription_expiring_notification_task(subscription_id: int, days_until_expiry: int) -> bool:
    """Send notification when subscription is about to expire."""
    try:
        subscription = Subscription.objects.select_related('user').get(id=subscription_id)
    except Subscription.DoesNotExist:
        logger.error(f'Subscription {subscription_id} does not exist')
        return False

    user = subscription.user

    if (
        hasattr(user, 'notification_preferences')
        and not user.notification_preferences.subscription_expiring
    ):
        return False

    subject = f'Your subscription expires in {days_until_expiry} day(s)'
    message = (
        f'Hi {user.first_name or user.email},\n\n'
        f'Your {subscription.plan} subscription will expire on '
        f'{subscription.valid_until.strftime("%Y-%m-%d %H:%M")}.\n\n'
        f'Renew your subscription to continue enjoying our content.\n\n'
        f'Best regards,\nYour Blog'
    )

    send_email_task.delay(subject, message, user.email)
    return True
