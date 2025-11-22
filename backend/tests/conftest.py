import os
from unittest.mock import MagicMock

import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
os.environ.setdefault('CELERY_BROKER_URL', 'memory://')
os.environ.setdefault('CELERY_RESULT_BACKEND', 'cache+memory://')
os.environ.setdefault('CELERY_TASK_ALWAYS_EAGER', 'True')
os.environ.setdefault('CELERY_TASK_EAGER_PROPAGATES', 'True')

if not settings.configured:
    django.setup()

# Force Celery to run tasks eagerly in tests to avoid external broker usage
from celery import current_app  # noqa: E402

current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True

# Disable Elasticsearch indexing for all tests
import django_elasticsearch_dsl  # noqa: E402

django_elasticsearch_dsl.apps.DEDConfig.default_auto_field = 'django.db.models.BigAutoField'

# Mock the registry update method to prevent ES connections
from blog import documents  # noqa: E402

mock_update = MagicMock(return_value=None)
documents.PostDocument.update = mock_update
