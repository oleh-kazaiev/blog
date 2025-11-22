import uuid
from typing import Dict, Tuple

import stripe

from blog.models import Post, PostPurchase
from payments.models import Payment


def initiate_post_purchase(user, post: Post) -> Tuple[Dict, int]:
    """
    Initiate the purchase of a post.

    Args:
        user: The user initiating the purchase.
        post: The post to be purchased.

    Returns:
        Tuple containing the response data and HTTP status code.
    """
    if not post.is_paid:
        return {'error': 'Post is not paywalled.'}, 400
    if post.price_cents <= 0:
        return {'error': 'Post is missing a valid price.'}, 400

    if post.user_has_access(user):
        return {'status': 'already_owned'}, 200

    pending_purchases = post.purchases.filter(user=user, status='pending')
    existing = pending_purchases.select_related('payment').select_for_update().first()

    if existing and existing.payment.stripe_payment_intent_id:
        return {
            'purchase_id': existing.id,
            'payment_id': existing.payment_id,
            'client_secret': existing.payment.client_secret,
            'status': existing.status,
        }, 200

    # Create Payment and PostPurchase records
    idempotency_key = uuid.uuid4().hex
    payment = Payment.objects.create(
        user=user,
        post=post,
        amount=post.price_cents,
        currency='usd',
        status='pending',
        idempotency_key=idempotency_key,
    )
    purchase = PostPurchase.objects.create(
        user=user,
        post=post,
        payment=payment,
        status='pending',
    )

    # Create Stripe Payment Intent
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=post.price_cents,
            currency='usd',
            metadata={
                'payment_id': str(payment.id),
                'post_id': str(post.id),
                'post_slug': post.slug,
                'user_id': str(user.id),
                'user_email': user.email,
            },
            idempotency_key=idempotency_key,
        )

        # Store Payment Intent ID and client secret
        payment.stripe_payment_intent_id = payment_intent.id
        payment.client_secret = payment_intent.client_secret
        payment.save(update_fields=['stripe_payment_intent_id', 'client_secret'])

    except Exception as e:
        # If Stripe fails, mark payment as failed
        payment.status = 'failed'
        payment.error_message = str(e)
        payment.save(update_fields=['status', 'error_message'])
        purchase.status = 'failed'
        purchase.save(update_fields=['status'])
        return {'error': f'Failed to create payment intent: {str(e)}'}, 500

    # NOTE: We don't enqueue the payment request here because the Payment Intent
    # doesn't have a payment method attached yet. The PaymentConfirmView will
    # enqueue the request after the user submits their payment details.

    return {
        'purchase_id': purchase.id,
        'payment_id': payment.id,
        'client_secret': payment.client_secret,
        'amount': post.price_cents,
        'currency': 'usd',
        'status': purchase.status,
    }, 201
