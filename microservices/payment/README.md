# payment

Async payment processor microservice using FastAPI and Kafka (`kafka-python`).

- Consumes `payments.request` and `subscriptions.request` topics
- Calls LocalStripe to create+confirm a PaymentIntent
- Publishes `payments.completed` / `subscriptions.completed` messages
- Broadcasts WebSocket updates at `/ws/payments/{payment_id}`

Environment variables (inherit from devcontainer or set explicitly):
- `KAFKA_BOOTSTRAP_SERVERS` (e.g. `kafka:9092`)
- `KAFKA_CONSUMER_GROUP` (optional, defaults to `payment-service`)
- `STRIPE_SECRET_KEY`
- `STRIPE_API_BASE` (e.g. `http://stripelocal:8420` in dev)

Dev run:
- `poetry install`
- `uvicorn payment.app:app --host 0.0.0.0 --port 8100 --reload`
