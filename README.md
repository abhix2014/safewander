# SafeWander MVP (Full Stack Upgrade)

SafeWander is now organized as a **layered backend architecture** while preserving your original visual design.

## Upgraded stack in this repo

- **Frontend:** static HTML/CSS/vanilla JS (`safewander-v2.html`)
- **Backend runtime:** Python 3 standard library HTTP server (`ThreadingHTTPServer`)
- **Backend architecture:** modular layers:
  - `app/main.py` (HTTP interface / routing)
  - `app/store.py` (data access + business rules)
- **Database:** SQLite (`data/safewander.db`)
- **API shape:** versioned + legacy compatibility
  - `/api/v1/*` (new)
  - `/api/*` (legacy compatibility)
- **Tests:** pytest integration tests via live HTTP calls

## Run

```bash
python3 server.py
```

Open `http://localhost:8000`.

## Endpoints

- `GET /api/health` and `GET /api/v1/health`
- `GET /api/posts?limit=20` and `GET /api/v1/posts?limit=20`
- `POST /api/posts` and `POST /api/v1/posts`
- `POST /api/sos` and `POST /api/v1/sos`
- `GET /api/stats` and `GET /api/v1/stats`
- `GET /api/events` and `GET /api/v1/events`
- `GET /api/hostels` and `GET /api/v1/hostels`
- `GET /api/incidents?limit=20` and `GET /api/v1/incidents?limit=20`

## Test

```bash
pytest -q
```


## Migration RFCs

- `docs/rfc/001-production-migration-plan.md`
- `docs/rfc/002-api-compatibility-matrix.md`
- `docs/rfc/003-cutover-checklist.md`

## React/Next Frontend (Phase 2 start)

A new Next.js + TypeScript + Tailwind app scaffold now exists in `frontend/`.

```bash
cd frontend
npm install
npm run dev
```

Set API base if needed:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

## Containers (Phase 3 start)

Run the stack with Docker Compose:

```bash
docker compose up --build
```

Services exposed:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

Files added:
- `Dockerfile.backend`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
