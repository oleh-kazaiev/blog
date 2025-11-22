import logging
from typing import TYPE_CHECKING

from .tasks import (
    send_comment_notification_task,
    send_payment_failed_notification_task,
    send_payment_success_notification_task,
    send_reaction_notification_task,
    send_subscription_activated_notification_task,
    send_subscription_cancelled_notification_task,
    send_subscription_expiring_notification_task
)

if TYPE_CHECKING:
    from blog.models import Comment, Post
    from payments.models import Payment, Subscription

logger = logging.getLogger(__name__)


def send_comment_notification(comment: 'Comment') -> None:
    """Queue notification when someone comments on user's post."""
    send_comment_notification_task.delay(comment.id)
    logger.debug(f'Queued comment notification for comment {comment.id}')


def send_reaction_notification(post: 'Post', reactor_email: str, action: str) -> None:
    """Queue notification when someone reacts to user's post."""
    send_reaction_notification_task.delay(post.id, reactor_email, action)
    logger.debug(f'Queued reaction notification for post {post.id}')


def send_payment_success_notification(payment: 'Payment') -> None:
    """Queue notification when payment succeeds."""
    send_payment_success_notification_task.delay(payment.id)
    logger.debug(f'Queued payment success notification for payment {payment.id}')


def send_payment_failed_notification(payment: 'Payment') -> None:
    """Queue notification when payment fails."""
    send_payment_failed_notification_task.delay(payment.id)
    logger.debug(f'Queued payment failed notification for payment {payment.id}')


def send_subscription_activated_notification(subscription: 'Subscription') -> None:
    """Queue notification when subscription is activated."""
    send_subscription_activated_notification_task.delay(subscription.id)
    logger.debug(f'Queued subscription activated notification for subscription {subscription.id}')


def send_subscription_cancelled_notification(subscription: 'Subscription') -> None:
    """Queue notification when subscription is cancelled."""
    send_subscription_cancelled_notification_task.delay(subscription.id)
    logger.debug(
        f'Queued subscription cancelled notification for subscription {subscription.id}'
    )


def send_subscription_expiring_notification(subscription: 'Subscription', days_until_expiry: int) -> None:
    """Queue notification when subscription is about to expire."""
    send_subscription_expiring_notification_task.delay(subscription.id, days_until_expiry)
    logger.debug(
        f'Queued subscription expiring notification for subscription {subscription.id}'
    )
