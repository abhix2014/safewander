# SafeWander MVP rollout

## Completed so far

- Layered backend structure (`app/main.py` + `app/store.py`)
- API compatibility for `/api/*` and `/api/v1/*`
- Live feed + SOS integration in legacy UI
- Next.js + TypeScript + Tailwind phase-2 scaffold
- Docker + CI phase-3 baseline

## Launch-readiness hardening added

- Security response headers on API responses
- Request tracing via `X-Request-ID`
- Configurable CORS allowlist via `CORS_ORIGINS`
- Configurable in-memory API rate limiting via `RATE_LIMIT_PER_MIN`
- Optional write protection using `WRITE_API_KEY` for POST endpoints
- Readiness endpoint (`/api/ready` + `/api/v1/ready`) with DB check
- Structured logging setup (`LOG_LEVEL`, request id in logs)

## Next milestones

1. Replace SQLite with Postgres in active runtime path
2. Move stdlib backend runtime to FastAPI while keeping contract compatibility
3. Add JWT auth and role-based moderation access
4. Add queue-backed async SOS dispatch and moderation jobs
5. Add production observability stack (metrics, traces, alerts)

## Governance docs

- RFC-001: production migration plan
- RFC-002: API compatibility matrix
- RFC-003: cutover checklist
