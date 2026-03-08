# SafeWander MVP rollout

## Upgrade completed

- Refactored backend into a layered structure (`app/main.py` + `app/store.py`)
- Added versioned API routes (`/api/v1/*`) with full legacy compatibility (`/api/*`)
- Preserved UI while keeping live feed + SOS integrations
- Hardened validation for post content, SOS coordinate pairing/ranges, and query limit parsing
- Kept zero-external-runtime dependency backend for easier deployment reliability

## Next milestones

1. Add JWT auth and traveler session model
2. Add moderation workflow APIs with audit trails
3. Add trust-score event ledger and scheduled recompute tasks
4. Add queue-based SOS dispatch integrations
5. Add containerized production deployment and observability


## Governance docs

- RFC-001: production migration plan
- RFC-002: API compatibility matrix
- RFC-003: cutover checklist


## Phase 2 progress

- Added initial Next.js + TypeScript + Tailwind scaffold under `frontend/`.
- Implemented first migrated screen slices (`Hero`, `CommunityFeed`) wired to existing `/api/v1/posts` and `/api/v1/posts` POST endpoints.
- Preserved legacy static frontend while enabling incremental route-by-route migration.


## Phase 3 progress

- Added backend and frontend Dockerfiles.
- Added `docker-compose.yml` with backend, frontend, Postgres, and Redis services.
- Added GitHub Actions CI workflow for backend tests and frontend build checks.
