# Blog Platform (Event-Driven Demo)

**Live Demo**: [blog.olehkazaiev.com](https://blog.olehkazaiev.com)

A full-stack blog platform deployed on a **Raspberry Pi 5**, designed to showcase **microservices**, **event-driven architecture**, and **production-grade patterns** (Kafka, Elasticsearch, Celery).

> **Note**: All external services (AWS S3, Stripe) are **mocked** (LocalStack, LocalStripe) to keep this project self-contained and cost-free.

## Core Features & Workflow

This project demonstrates a complete content platform designed to showcase complex business logic and architectural patterns.

### Key Capabilities
*   **Content Creation**: Users can create standard posts, **paid posts**, and **delayed posts** (automatically published via Celery tasks).
*   **Monetization**:
    *   **Buy Subscription**: Unlock premium features using a mock credit card (e.g., `4242...`).
    *   **Buy Post**: Purchase access to individual paid articles.
*   **Interactive Features**:
    *   Create and publish content (Active Subscription Required or admin role).
    *   Engage with the community via **likes, dislikes, and comments**.

## Architecture

The system uses an event-driven approach where the Django backend and FastAPI payment service communicate asynchronously via Kafka. Both services implement **Producers** and **Consumers** to handle distributed transactions (e.g., subscription activation, payment confirmation).

**Cloudflare Tunnel** exposes specific services (Frontend, Backend, LocalStack) to the internet.

```
┌─────────────────────────────────────────────────────────────┐
│                      Cloudflare Tunnel                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                        Traefik Proxy                        │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
┌──────▼─────┐          ┌──────▼──────┐          ┌─────▼──────┐
│  Frontend  │          │  Backend x2 │─────────►│ LocalStack │
│   (React)  │          │   (Django)  │          │  (S3 Mock) │
└────────────┘          └──────┬──────┘          └────────────┘
                               │
         ┌──────────────┬──────┼──────┬──────────────┐
         │              │      │      │              │
    ┌────▼─────┐   ┌────▼──┐   │   ┌──▼────┐    ┌────▼─────┐
    │ Postgres │   │ Redis │   │   │Elastic│    │ RabbitMQ │
    │   (DB)   │   │(Cache)│   │   │(Search)    │ (Broker) │
    └──────────┘   └───────┘   │   └───────┘    └────▲─────┘
                               │                     │
                               │                ┌────┴─────┐
                               │                │  Celery  │
                               │                │ (Workers)│
                               │                └──────────┘
                               │
                       ┌───────▼───────┐
                       │ Apache Kafka  │
                       │(Event Stream) │
                       └───────▲───────┘
                               │
               ┌───────────────┴───────────────┐
               │                               │
       ┌───────▼───────┐               ┌───────▼───────┐
       │   Payment x2  │               │ Payment Evts  │
       │   (FastAPI)   │               │  (Consumer)   │
       │  [Prod/Cons]  │               │   (Django)    │
       └───────┬───────┘               └───────────────┘
               │
       ┌───────▼───────┐
       │  LocalStripe  │
       │ (Stripe Mock) │
       └───────────────┘
```

### Tech Stack
*   **Backend**: Django 5, Python 3.13, FastAPI (Microservice)
*   **Frontend**: React 18, TypeScript, MUI
*   **Data**: PostgreSQL 17, Redis 8, Elasticsearch 9
*   **Messaging**: Apache Kafka 4.1, RabbitMQ 4.2, Celery 5
*   **Infrastructure**: Docker Compose, Traefik v3.6

## Quick Start

1.  **Clone & Config**:
    ```bash
    git clone <repo>
    cd blog
    cp .env.sample .env
    ```
2.  **Run (Production Mode)**:
    ```bash
    make prod-up
    ```
3.  **Access**:
    *   Frontend: `http://localhost:3081`
    *   API: `http://localhost:3082`
    *   LocalStack: `http://localhost:3083`

## Development Commands

*   `make dev-up` - Start development stack with hot-reload.
*   `make test` - Run full test suite (pytest, flake8, mypy).
*   `make prod-rebuild` - Rebuild and restart production containers.

---
*Created by Oleh Kazaiev*
