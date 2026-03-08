# SafeWander MVP (Production-Ready Baseline)

SafeWander now includes a hardened baseline for real-world launch prep while preserving your existing UI and backward API compatibility.

## Current architecture

- **Frontend:**
  - Legacy static UI: `safewander-v2.html`
  - Migration frontend: Next.js scaffold in `frontend/`
- **Backend:** Python stdlib `ThreadingHTTPServer` with layered structure:
  - `app/main.py` (routing, request handling, security headers, rate limit)
  - `app/store.py` (SQLite persistence + business logic)
- **Database:** SQLite (`DB_PATH`, default `data/safewander.db`)
- **API:** `/api/*` and `/api/v1/*` compatibility

## Local run (backend)

```bash
python3 server.py
```

Open `http://localhost:8000`.

## Key runtime env vars

- `PORT` (default: `8000`)
- `DB_PATH` (default: `data/safewander.db`)
- `APP_ENV` (default: `development`)
- `LOG_LEVEL` (default: `INFO`)
- `CORS_ORIGINS` (comma-separated, default: `*`)
- `RATE_LIMIT_PER_MIN` (default: `120`)
- `WRITE_API_KEY` (optional; if set, required as `X-API-Key` for POST writes)

## API endpoints

- `GET /api/health` and `GET /api/v1/health`
- `GET /api/ready` and `GET /api/v1/ready`
- `GET /api/posts?limit=20` and `GET /api/v1/posts?limit=20`
- `POST /api/posts` and `POST /api/v1/posts`
- `POST /api/sos` and `POST /api/v1/sos`
- `GET /api/stats` and `GET /api/v1/stats`
- `GET /api/events` and `GET /api/v1/events`
- `GET /api/hostels` and `GET /api/v1/hostels`
- `GET /api/incidents?limit=20` and `GET /api/v1/incidents?limit=20`

## Local run (frontend migration scaffold)

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

## Containers

```bash
docker compose up --build
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

## Tests

```bash
pytest -q
```

## Migration governance

- `docs/mvp-plan.md`
- `docs/rfc/001-production-migration-plan.md`
- `docs/rfc/002-api-compatibility-matrix.md`
- `docs/rfc/003-cutover-checklist.md`
