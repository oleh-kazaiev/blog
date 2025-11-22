from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Django app configuration for blog."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
