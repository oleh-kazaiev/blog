import logging
from datetime import timedelta

from django.utils import timezone

from celery import shared_task

from payments.models import Subscription
from users.notifications import send_subscription_expiring_notification

from .models.post import Post

logger = logging.getLogger(__name__)


@shared_task
def publish_scheduled_posts() -> int:
    """Publish scheduled posts whose `published_at` is in the past or now.

    This task is intentionally simple for tests: find all posts that are not
    yet published and whose `published_at` is <= now, mark them published and
    return the number of posts updated.

    Returns:
        Number of posts published
    """
    now = timezone.now()
    # We need to iterate and save individually to trigger signals for Elasticsearch indexing
    posts = list(Post.objects.filter(is_published=False, published_at__lte=now))

    for post in posts:
        post.is_published = True
        post.save(update_fields=['is_published'])

    updated_count = len(posts)
    if updated_count:
        logger.info(f'Published {updated_count} scheduled posts')
    return updated_count


@shared_task
def collect_daily_stats() -> dict[str, int]:
    """Collect simple daily stats (demo).

    Returns:
        Dictionary containing daily statistics
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    posts_today = Post.objects.filter(is_published=True, published_at__gte=today_start).count()
    logger.info(f'Daily stats: posts_published_today={posts_today}')
    return {'posts_published_today': posts_today}


@shared_task
def backfill_publish_check() -> int:
    """Backfill safety check for scheduled posts (demo).

    Returns:
        Number of posts published during backfill check
    """
    result = publish_scheduled_posts()  # reuse existing logic
    logger.info(f'Backfill publish check updated={result}')
    return result


@shared_task
def expire_subscriptions() -> int:
    """Automatically expire subscriptions that are past their valid_until date.

    This task should be run periodically (e.g., hourly) to ensure subscriptions
    are marked as expired when they reach their expiration date.

    Returns:
        Number of subscriptions expired
    """
    now = timezone.now()

    # Send expiring soon notifications (3 days before expiry)
    expiring_soon = Subscription.objects.filter(
        status='active',
        valid_until__gte=now,
        valid_until__lte=now + timedelta(days=3),
    ).select_related('user')

    for sub in expiring_soon:
        days_until_expiry = (sub.valid_until - now).days
        if days_until_expiry in [3, 1]:  # Send at 3 days and 1 day
            send_subscription_expiring_notification(sub, days_until_expiry)

    # Expire subscriptions that are past their valid_until date
    expired_count = Subscription.objects.filter(
        status='active',
        valid_until__lt=now,
    ).update(status='expired')

    if expired_count:
        logger.info(f'Expired {expired_count} subscriptions')

    return expired_count
