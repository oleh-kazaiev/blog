from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """Django app configuration for payments."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
