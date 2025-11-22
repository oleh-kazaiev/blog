FROM python:3.13-slim

ARG POETRY_VERSION=2.1.4
ARG TARGETPLATFORM

LABEL maintainer="Blog Application"
LABEL description="Django backend (multi-arch, ARM-optimized)"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# System deps for building Python packages and Postgres driver
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       curl \
       git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.create false

# Copy dependency files (lock file ensures reproducible builds)
COPY pyproject.toml poetry.lock ./

# Install runtime deps only
RUN poetry install --no-interaction --no-ansi --only=main

# Copy project code
COPY . .

# Create required dirs
RUN mkdir -p logs media static /var/lib/celery \
    && chmod 755 logs media static /var/lib/celery

# Non-root user for security
RUN groupadd -r app && useradd -r -g app app_user \
    && chown -R app_user:app /app /var/lib/celery

USER app_user

# Default command: migrate, collectstatic, init stripe (if present), then run ASGI server
CMD ["sh", "-c", "python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput \
    && python /tmp/init_stripe.py \
    && uvicorn main.asgi:application --host ${HOST} --port ${PORT}"]
