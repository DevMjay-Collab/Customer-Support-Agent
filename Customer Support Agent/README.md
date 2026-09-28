# HMC AI Customer Support Platform

HMC is a single-organization customer-operations platform for bringing customer conversations, leads, appointments, and AI-assisted support work into one controlled system.

Its purpose is not to let an AI act autonomously. The platform gives an owner a reliable record of customer interactions and a configurable support agent that can propose structured actions. The backend remains responsible for validation, authorization, durable changes, and auditability.

## Core principles

- **One business, one workspace, one owner.** This project is deliberately not a multi-tenant SaaS platform.
- **Customers and conversations are first-class records.** Contacts, leads, conversations, messages, and appointments belong in PostgreSQL, not in an automation tool or a chat transcript.
- **AI is constrained.** Future AI capabilities will recommend or prepare structured actions; server-side rules decide whether anything is allowed to happen.
- **External tools do not own the business state.** n8n and channel providers may orchestrate work, but cannot become the source of truth or bypass authorization.
- **Every durable operational change is attributable.** Authenticated writes create audit-log entries without copying sensitive message content into the audit log.

## Current capabilities

The backend currently provides:

- owner login/logout with server-side sessions stored in PostgreSQL;
- business and agent configuration endpoints;
- contacts, leads, conversations, and conversation-message APIs;
- audit logging for operational writes;
- PostgreSQL migrations, Redis/database readiness checks, structured request logging, and containerized local startup;
- an OpenAPI interface at `/docs`.

The following are intentionally not connected yet: LLM execution, SMS/WhatsApp/email/voice providers, calendar providers, n8n workflows, inbound webhooks, and a customer-operations web UI. They need verified provider behavior, credentials, and explicit product rules before being enabled.

## Architecture

```text
Owner / future operations UI
            |
            v
       FastAPI API
            |
   authentication + validation
   authorization + audit logging
            |
            v
       PostgreSQL  <---- authoritative business data
            |
            +---- Redis (transient coordination and readiness)

Future integrations: AI, channel providers, calendar, n8n
They submit constrained requests; they do not own data or authorization.
```

## API overview

All `/api/v1` endpoints, except authentication, require the owner session cookie created by `POST /api/v1/auth/login`.

| Area | Available endpoints |
| --- | --- |
| Authentication | `POST /auth/login`, `POST /auth/logout` |
| Business settings | `GET/PATCH /settings/business` |
| Agent configuration | `GET/PATCH /settings/agent` |
| Contacts | `POST /contacts`, `GET /contacts`, `GET/PATCH /contacts/{contact_id}` |
| Leads | `POST /contacts/{contact_id}/leads`, `GET /leads` |
| Conversations | `POST/GET /conversations`, `GET/PATCH /conversations/{conversation_id}` |
| Messages | `POST/GET /conversations/{conversation_id}/messages` |
| Operations | `GET /health`, `GET /ready` |

Run the service and open [http://localhost:8000/docs](http://localhost:8000/docs) for request and response schemas.

## Local development

### Prerequisites

- Python 3.12 or later
- Docker and Docker Compose (recommended for PostgreSQL and Redis)

### Configure and run

1. Create a local environment file:

   ```bash
   cp .env.example .env
   ```

2. Set a unique `APP_SECRET_KEY` and a secure, private `OWNER_BOOTSTRAP_PASSWORD` in `.env`. Do not commit this file.

3. Start the stack:

   ```bash
   ENV_FILE=.env docker compose up --build
   ```

The `migrate` service applies all Alembic migrations before the API starts. The one-time owner account is created at startup only when the user table is empty and both owner bootstrap values are provided.

Check the service at:

- [http://localhost:8000/health](http://localhost:8000/health) — application liveness
- [http://localhost:8000/ready](http://localhost:8000/ready) — PostgreSQL and Redis readiness
- [http://localhost:8000/docs](http://localhost:8000/docs) — interactive API documentation

To run migrations outside Docker, set `DATABASE_URL_SYNC` and use:

```bash
alembic upgrade head
```

## Development checks

This repository includes a local virtual environment at `.venv` when created by the development setup. Run:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check app tests
.venv/bin/python -m mypy app
```

## Repository layout

```text
app/
  auth/             Owner authentication and session controls
  configuration/    Business settings
  agent/            Agent configuration (not AI execution)
  operations/       Contacts, leads, conversations, messages, audit helper
  core/             SQLAlchemy domain models
  health.py         Dependency readiness checks
alembic/             Versioned PostgreSQL schema migrations
tests/               Unit and API-foundation tests
docs/                Project and architecture notes
```

## Delivery roadmap

1. Add PostgreSQL-backed integration tests and CI.
2. Build the operations UI for the authenticated workflow.
3. Implement inbound channel adapters and idempotent webhook processing.
4. Add agent orchestration with policy-checked, structured actions and human escalation.
5. Add appointment workflows and verified calendar-provider synchronization.
6. Integrate approved communication providers with signature validation, retry controls, and observability.

## Security notes

- Keep `.env` private; `.env.example` contains placeholders only.
- Use a long, randomly generated `APP_SECRET_KEY` in every non-development environment.
- Run migrations before serving traffic; Compose enforces that dependency locally.
- Treat all future inbound provider callbacks as untrusted until signature validation and replay protection are implemented.
- No provider is considered connected merely because its environment variables exist.
