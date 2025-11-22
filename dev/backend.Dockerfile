FROM python:3.13-slim

# Install system tools and Node.js 24 (LTS)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       bash \
       curl \
       git \
       procps \
       ca-certificates \
       build-essential \
       libpq-dev \
       wget \
       gnupg \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_24.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==2.1.4 \
    && poetry config virtualenvs.create false

WORKDIR /workspace

COPY ../ /workspace

RUN cd /workspace/backend \
    && poetry lock --no-interaction --no-ansi \
    && poetry install --no-ansi

RUN cd /workspace/frontend \
    && npm install
