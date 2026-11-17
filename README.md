# Delivery Booking

Book, approve and check in site deliveries and collections. Three portals:
**admin** (site rules, capacity, approvals), **contractor** (book vehicles), and
**gate** (scan QR, check in/out).

- `apps/web`: Next.js frontend
- `backend`: Python API (FastAPI + SQLAlchemy)

## Run it locally (no database or other services needed)

Requirements: Node.js 20+ and [uv](https://docs.astral.sh/uv/) (uv installs
the right Python version itself).

```bash
npm run setup   # first time only: installs JS and Python dependencies
npm run dev     # starts API on :8000 and web on :3000
```

Open http://localhost:3000. You should see "API OK".
API docs (interactive): http://localhost:8000/docs

```bash
npm test        # backend tests
npm run lint
npm run db:reset                      # wipe the local database and rebuild it
npm run db:migration -- "add gates"   # after changing models: generate a migration
```

`npm run dev` applies any pending database migrations automatically.

Booking page: http://localhost:3000/contractor/book

## Configuration

Everything has a working local default. By default the database is a SQLite
file at `backend/dev.db`, created automatically. Delete it to start fresh.

To use real infrastructure later, copy `backend/.env.example` to `backend/.env`
and set the values, e.g. `DATABASE_URL` for PostgreSQL. The frontend reads
`API_URL` if the backend isn't on `http://127.0.0.1:8000`.
