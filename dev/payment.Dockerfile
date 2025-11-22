FROM python:3.13-slim

# Lightweight dev image for payment microservice
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential git \
    && rm -rf /var/lib/apt/lists/* \

WORKDIR /workspace

COPY ../ /workspace

RUN pip install --no-cache-dir poetry==2.1.4 \
    && poetry config virtualenvs.create false

RUN cd /workspace/microservices/payment \
    && poetry install --no-root --no-ansi
