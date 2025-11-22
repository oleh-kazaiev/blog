import os
from pathlib import Path
from typing import Any, Dict

import stripe

from .settings_helpers import get_bool

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
LOGS_DIR = PROJECT_ROOT / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)


# Environment variable validation
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable is required')

DEBUG = get_bool('DEBUG')

# Security settings - some should always be set for better security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

SECURE_SSL_REDIRECT = get_bool('SECURE_SSL_REDIRECT')

# HSTS and secure cookies - configurable for Cloudflare tunnel setups
ENABLE_HSTS = get_bool('ENABLE_HSTS')
ENABLE_SECURE_COOKIES = get_bool('ENABLE_SECURE_COOKIES')

if not DEBUG:
    if ENABLE_HSTS:
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
    if SECURE_SSL_REDIRECT:
        SECURE_SSL_REDIRECT = True
    if ENABLE_SECURE_COOKIES:
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True

# Only trust X-Forwarded-Proto if using a reverse proxy
if get_bool('USE_PROXY_SSL_HEADER'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(' ')

CACHES: Dict[str, Any] = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ['REDIS_CACHE_URL'],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'blog',
        'VERSION': 1,
        'TIMEOUT': 0,
    }
}
CACHE_MIDDLEWARE_SECONDS = 0
CACHE_MIDDLEWARE_KEY_PREFIX = 'blog'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_ckeditor_5',
    'django_elasticsearch_dsl',
    'blog',
    'api',
    'users',
    'payments',
]

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'
ASGI_APPLICATION = 'main.asgi.application'

DATABASES: Dict[str, Any]
DATABASES = {  # noqa: ECE001
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT'],
        'CONN_MAX_AGE': int(os.environ['DB_CONN_MAX_AGE']),
        'CONN_HEALTH_CHECKS': True,
        'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'prefer',
        },
        'TEST': {
            'NAME': f"test_{os.environ['POSTGRES_DB']}",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')

# S3/LocalStack storage (always enabled)
INSTALLED_APPS.append('storages')
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
AWS_S3_ENDPOINT_URL = os.environ['AWS_S3_ENDPOINT_URL']
# S3_DOMAIN for public URL generation (via Traefik/Cloudflare)
S3_DOMAIN = os.environ['S3_DOMAIN']
AWS_S3_FORCE_PATH_STYLE = get_bool('AWS_S3_FORCE_PATH_STYLE')
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_FILE_OVERWRITE = False

# Storage configuration for Django 4.2+
STORAGES = {
    'default': {
        'BACKEND': 'main.storage.MediaRootS3Boto3Storage',
    },
    'staticfiles': {
        'BACKEND': 'main.storage.StaticRootS3Boto3Storage',
    },
}

# Set public URLs for static/media files served through LocalStack proxy
STATIC_URL = f'https://{S3_DOMAIN}/{AWS_STORAGE_BUCKET_NAME}/static/'
MEDIA_URL = f'https://{S3_DOMAIN}/{AWS_STORAGE_BUCKET_NAME}/media/'

# Stripe integration (always enabled)
STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
STRIPE_WEBHOOK_SECRET = os.environ['STRIPE_WEBHOOK_SECRET']
STRIPE_API_BASE = os.environ['STRIPE_API_BASE']
STRIPE_PRICE_ID = os.environ['STRIPE_PRICE_ID']
STRIPE_SUBSCRIPTION_PRICE_ID = os.environ.get('STRIPE_SUBSCRIPTION_PRICE_ID', STRIPE_PRICE_ID)
STRIPE_SUCCESS_URL = os.environ['STRIPE_SUCCESS_URL']
STRIPE_CANCEL_URL = os.environ['STRIPE_CANCEL_URL']

stripe.api_key = STRIPE_SECRET_KEY
stripe.api_base = STRIPE_API_BASE

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modern Django settings
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Session security
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF protection
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = os.environ['CSRF_TRUSTED_ORIGINS'].split(',')

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.environ['CORS_ALLOWED_ORIGINS'].split(' ')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CKEditor 5 configuration
CUSTOM_COLOR_PALETTE = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'link',
            'bulletedList', 'numberedList', 'blockQuote', 'imageUpload',
        ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': [
            'heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
            'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
            'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
            'insertTable',
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', '|', 'imageStyle:alignLeft', 'imageStyle:alignRight',
                'imageStyle:alignCenter', 'imageStyle:side',
            ],
            'styles': ['full', 'side', 'alignLeft', 'alignRight', 'alignCenter'],
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties',
            ],
            'tableProperties': {
                'borderColors': CUSTOM_COLOR_PALETTE,
                'backgroundColors': CUSTOM_COLOR_PALETTE,
            },
            'tableCellProperties': {
                'borderColors': CUSTOM_COLOR_PALETTE,
                'backgroundColors': CUSTOM_COLOR_PALETTE,
            },
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
            ],
        },
    },
    'list': {
        'properties': {'styles': 'true', 'startIndex': 'true', 'reversed': 'true'},
    },
}

CKEDITOR_5_UPLOAD_PATH = 'uploads/'
CKEDITOR_5_FILE_STORAGE = 'main.storage.MediaRootS3Boto3Storage'

KAFKA_BOOTSTRAP_SERVERS = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_PRODUCER_TIMEOUT = float(os.environ.get('KAFKA_PRODUCER_TIMEOUT', '10'))
KAFKA_TOPIC_PAYMENTS_REQUEST = os.environ['KAFKA_TOPIC_PAYMENTS_REQUEST']
KAFKA_TOPIC_PAYMENTS_COMPLETED = os.environ['KAFKA_TOPIC_PAYMENTS_COMPLETED']
KAFKA_TOPIC_SUBSCRIPTIONS_REQUEST = os.environ['KAFKA_TOPIC_SUBSCRIPTIONS_REQUEST']
KAFKA_TOPIC_SUBSCRIPTIONS_COMPLETED = os.environ['KAFKA_TOPIC_SUBSCRIPTIONS_COMPLETED']
KAFKA_TOPIC_PAYMENTS_CANCELLED = os.environ['KAFKA_TOPIC_PAYMENTS_CANCELLED']
KAFKA_TOPIC_SUBSCRIPTIONS_CANCELLED = os.environ['KAFKA_TOPIC_SUBSCRIPTIONS_CANCELLED']

CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_DEFAULT_QUEUE = 'default'

# Email
EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = int(os.environ['EMAIL_PORT'])
EMAIL_USE_TLS = get_bool('EMAIL_USE_TLS')
EMAIL_USE_SSL = get_bool('EMAIL_USE_SSL')
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_TIMEOUT = int(os.environ['EMAIL_TIMEOUT'])
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = os.environ['SERVER_EMAIL']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_production': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'blog.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'console_production', 'file'],
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'console_production', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'console_production', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'console_production', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'console_production', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Elasticsearch
ELASTICSEARCH_URL = os.environ['ELASTICSEARCH_URL']
ES_INDEX_POSTS = os.environ['ES_INDEX_POSTS']

# Django Elasticsearch DSL
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_URL,
        'timeout': 30,
    },
}

ELASTICSEARCH_DSL_AUTOSYNC = True
