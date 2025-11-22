import os
from datetime import timedelta
from typing import Dict, Optional

DEFAULT_CURRENCY = os.environ.get('SUBSCRIPTION_PLAN_CURRENCY', 'usd')


def get_subscription_plans() -> Dict[str, Dict]:
    """Return the configured subscription plans."""
    return {
        'day': {
            'key': 'day',
            'label': 'Day Pass (24h)',
            'price_cents': 399,
            'currency': DEFAULT_CURRENCY,
            'duration': timedelta(days=1),
            'stripe_price_id': os.environ.get('STRIPE_PLAN_DAY_ID', 'plan_blog_day'),
        },
        'week': {
            'key': 'week',
            'label': 'Weekly Access',
            'price_cents': 1299,
            'currency': DEFAULT_CURRENCY,
            'duration': timedelta(weeks=1),
            'stripe_price_id': os.environ.get('STRIPE_PLAN_WEEK_ID', 'plan_blog_week'),
        },
        'month': {
            'key': 'month',
            'label': 'Monthly Membership',
            'price_cents': 2499,
            'currency': DEFAULT_CURRENCY,
            'duration': timedelta(days=30),
            'stripe_price_id': os.environ.get('STRIPE_PLAN_MONTH_ID', 'plan_blog_month'),
        },
    }


def get_plan_config(plan_key: str) -> Optional[Dict]:
    """Get configuration for a specific subscription plan."""
    return get_subscription_plans().get(plan_key)
