# RFC-001: SafeWander Production Migration Plan

- **Status:** Proposed
- **Owner:** SafeWander Engineering
- **Last Updated:** 2026-03-08

## 1) Context

SafeWander currently runs a static frontend (`safewander-v2.html`) with a Python stdlib API backend (`app/main.py`) and SQLite persistence (`app/store.py`). This is excellent for MVP speed but not ideal for high concurrency, strict reliability SLOs, or large-team development.

## 2) Goals

1. Migrate to a production-ready stack incrementally without a big-bang rewrite.
2. Preserve current user-facing design language while modernizing delivery.
3. Maintain backward compatibility for existing `/api/*` integrations during migration.
4. Introduce operational foundations: CI/CD, containerization, caching, and observability.

## 3) Non-goals

- Full feature rewrite in one release.
- Immediate removal of legacy endpoints.
- Premature multi-region deployment in phase 1.

## 4) Target Architecture

### Backend
- FastAPI service layer
- SQLAlchemy ORM + Alembic migrations
- PostgreSQL as source of truth
- Redis for cache + background queueing

### Frontend
- Next.js (React + TypeScript)
- TailwindCSS + design token mapping from current visual system

### DevOps
- Docker images for app services
- Nginx as ingress/reverse proxy
- GitHub Actions CI/CD pipeline
- Monitoring stack (OpenTelemetry + logs/metrics)

## 5) Migration Strategy (Strangler Pattern)

- Keep existing service live and stable.
- Introduce new services behind versioned routes (`/api/v2/*`) while keeping `/api/*` and `/api/v1/*` compatibility.
- Migrate endpoint-by-endpoint with contract tests.
- Shift frontend traffic gradually by feature flags.

## 6) Phased Delivery

## Phase 1 — Database + API Layer (2–4 weeks)

### Deliverables
- Postgres schema + Alembic migrations
- FastAPI service with parity endpoints:
  - health, posts, sos, incidents, stats, events, hostels
- Contract tests to ensure response compatibility with legacy API
- Data migration utility: SQLite → Postgres

### Exit Criteria
- New API passes parity test suite.
- Read endpoints switched to Postgres-backed service in staging.
- Rollback validated.

## Phase 2 — Frontend Upgrade (3–6 weeks)

### Deliverables
- Next.js app shell + routing + TypeScript setup
- Tailwind theme mapped from existing SafeWander palette/components
- Migrated screens: feed + map + sos + events + hostels
- Frontend compatibility layer for legacy API fields

### Exit Criteria
- Lighthouse baseline accepted.
- Pixel/UX parity approved for critical journeys.

## Phase 3 — Containerization + CI/CD (1–2 weeks)

### Deliverables
- Dockerfiles for API and frontend
- docker-compose for local dev with Postgres + Redis
- GitHub Actions: lint, test, build, image publish
- Nginx config for routing and static asset caching

### Exit Criteria
- One-command local startup.
- Automated deployment to staging on main branch.

## Phase 4 — Caching + Monitoring (1–3 weeks)

### Deliverables
- Redis cache for hot reads (posts/events/hostels)
- Async queue for SOS dispatch and moderation events
- Structured logging, metrics dashboards, alert rules
- SLOs and runbooks

### Exit Criteria
- Cache hit-rate and latency improvements documented.
- Alerts and on-call runbook tested.

## 7) Risks & Mitigations

- **Contract drift:** Use snapshot/contract tests against legacy API.
- **Data migration errors:** Dry-run migration and row-count checks.
- **Frontend regressions:** Feature flags + gradual rollout.
- **Operational complexity:** Add one subsystem at a time (DB, then CI/CD, then cache/monitoring).

## 8) Rollback Strategy

- Keep legacy runtime deployable until post-cutover stability window (2 weeks).
- Versioned endpoint routing toggle at Nginx layer.
- Database rollback scripts for migration batches.

## 9) Team Estimate

- 1 Backend + 1 Frontend + fractional DevOps:
  - 7–15 weeks total depending on scope and QA rigor.

## 10) Immediate Next Actions

1. Approve this RFC.
2. Create tickets per phase (epics + stories).
3. Implement Phase 1 skeleton (FastAPI + Postgres compose + Alembic base migration).
