import os
import time

import stripe

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_local')
stripe.api_base = os.environ.get('STRIPE_API_BASE', 'http://stripelocal:8420')


def init_stripe():
    """Initialize Stripe products and prices."""
    print(f'Connecting to Stripe at {stripe.api_base}')

    # Wait for Stripe to be ready
    for i in range(10):
        try:
            stripe.Product.list(limit=1)
            break
        except Exception:
            print('Waiting for Stripe...')
            time.sleep(2)

    # Check if product exists
    try:
        products = stripe.Product.list(limit=100)
        product = next((p for p in products.data if p.name == 'Blog Subscription'), None)
    except Exception as e:
        print(f'Error listing products: {e}')
        return

    if not product:
        try:
            product = stripe.Product.create(name='Blog Subscription')
            print(f'Created Product: {product.id}')
        except Exception as e:
            print(f'Error creating product: {e}')
            return
    else:
        print(f'Product already exists: {product.id}')

    # Define plans with stable predefined IDs from environment
    plans = [
        {
            'key': 'day',
            'id': os.environ['STRIPE_PLAN_DAY_ID'],
            'amount': 399,
            'interval': 'day'
        },
        {
            'key': 'week',
            'id': os.environ['STRIPE_PLAN_WEEK_ID'],
            'amount': 1299,
            'interval': 'week'
        },
        {
            'key': 'month',
            'id': os.environ['STRIPE_PLAN_MONTH_ID'],
            'amount': 2499,
            'interval': 'month'
        },
    ]

    for plan in plans:
        plan_id = plan['id']

        # Try to retrieve existing plan with stable ID
        try:
            existing_plan = stripe.Plan.retrieve(plan_id)
            print(f'Plan for {plan["key"]} already exists: {existing_plan.id}')
            continue
        except Exception:
            print(f'Plan {plan_id} not found, creating with stable ID...')

        # Create plan with predefined stable ID
        try:
            new_plan = stripe.Plan.create(
                id=plan_id,
                amount=plan['amount'],
                currency='usd',
                interval=plan['interval'],
                product=product.id,
                nickname=f'{plan["key"].capitalize()} Pass'
            )
            print(f'Created plan for {plan["key"]}: {new_plan.id}')
        except Exception as e:
            print(f'Error creating plan for {plan["key"]}: {e}')

    print('\nStripe initialization complete with stable IDs:')
    print(f'STRIPE_PLAN_DAY_ID={plans[0]["id"]}')
    print(f'STRIPE_PLAN_WEEK_ID={plans[1]["id"]}')
    print(f'STRIPE_PLAN_MONTH_ID={plans[2]["id"]}')


if __name__ == '__main__':
    init_stripe()
