# Phase 0 — Repository Reconnaissance

Date: 2026-08-26

## Repository map

The repository was initialized with Git but contained no application code, dependency manifests, environment files, tests, infrastructure configuration, documentation, or commits. `main` is the current unborn branch.

## Existing behaviour and checks

There was no runnable application and no test, lint, type-check, build, or migration command to execute. No user changes exist to preserve.

## Governing constraints recorded

- One deployment, business configuration, workspace, and owner/admin; multi-tenancy is prohibited.
- PostgreSQL is authoritative; pgvector starts retrieval; Redis provides transient coordination.
- The LLM proposes structured actions only; backend validation and authorization control durable changes.
- n8n orchestrates external workflows and does not own business state or authorization.
- Provider behavior must be officially verified before its implementation.

## Phase 1 starting point

Create the smallest FastAPI foundation with environment-only configuration, structured logging, database/Redis readiness checks, Docker local dependencies, and Alembic migration support. Domain models and external providers remain out of scope.

