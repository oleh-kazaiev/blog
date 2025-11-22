import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('blog')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure queues
app.conf.task_default_queue = 'default'

# Raspberry Pi 5 optimizations
# Limit concurrency based on available resources
app.conf.worker_concurrency = int(os.environ['CELERY_CONCURRENCY'])

# Prefetch multiplier (lower for more fair task distribution)
app.conf.worker_prefetch_multiplier = 1

# Maximum memory per child (in KB) - restart workers if they exceed this
app.conf.worker_max_memory_per_child = 200000  # 200MB

# Maximum number of tasks a worker can execute before it's replaced
app.conf.worker_max_tasks_per_child = 100

# Beat scheduler optimizations
app.conf.beat_schedule_filename = os.environ['CELERY_BEAT_SCHEDULE_FILENAME']
app.conf.beat_sync_every = 0  # Sync schedule after every task (prevents lost schedules)
app.conf.beat_max_loop_interval = 5  # Check for due tasks every 5 seconds (default is 5)

# Periodic tasks (optimized for lower frequency)
app.conf.beat_schedule = {
    'collect-daily-stats-midnight': {
        'task': 'blog.tasks.collect_daily_stats',
        'schedule': crontab(minute=0, hour=0),
    },
    # Publish scheduled posts every 5 minutes (was every minute - reduced load)
    'publish-scheduled-posts': {
        'task': 'blog.tasks.publish_scheduled_posts',
        'schedule': crontab(minute='*/5'),
    },
    # Backfill safety check every 2 hours (was 30 minutes - reduced load)
    'publish-scheduled-posts-backfill': {
        'task': 'blog.tasks.backfill_publish_check',
        'schedule': crontab(minute=0, hour='*/2'),
    },
    'cancel-stale-payments': {
        'task': 'payments.tasks.cancel_stale_payments',
        'schedule': crontab(minute='*/30'),
    },
    'cancel-stale-subscriptions': {
        'task': 'payments.tasks.cancel_stale_subscriptions',
        'schedule': crontab(minute='*/30'),
    },
}

# Load task modules from all registered Django app configs (after configuration).
app.autodiscover_tasks()
