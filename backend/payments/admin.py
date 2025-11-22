from django.contrib import admin

from .models import Payment, Subscription


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""

    list_display = (
        'id',
        'user',
        'amount',
        'currency',
        'status',
        'stripe_payment_intent_id',
        'created_at',
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('id', 'user__email', 'stripe_payment_intent_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model."""

    list_display = (
        'id',
        'user',
        'plan',
        'status',
        'price_id',
        'valid_until',
        'created_at',
    )
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('id', 'user__email', 'stripe_subscription_id', 'idempotency_key')
    readonly_fields = ('created_at', 'updated_at', 'client_secret')
    list_select_related = ('user',)
