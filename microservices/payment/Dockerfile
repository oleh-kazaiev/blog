# Production Dockerfile for payment microservice
FROM python:3.13-slim AS base

ENV POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION}

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy pyproject and lock first for layer caching
COPY pyproject.toml poetry.lock* ./
# Install deps globally (no venv) so runtime tools are on PATH
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main --no-ansi

# Copy application code
COPY payment ./payment

EXPOSE 8100

# Run uvicorn directly (Poetry installed packages are in the global env)
CMD ["uvicorn", "payment.app:app", "--host", "0.0.0.0", "--port", "8100"]

