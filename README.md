# Go Links

A small internal URL shortcut service: `go/oncall` → `https://…/oncall-rota`.

Users can **create** a shortcut, **view** existing shortcuts, and **visit** one to be redirected. A visit to a shortcut that doesn't exist yet lands on the create form with the name prefilled.

- **Backend:** Python 3.12, FastAPI, SQLModel, SQLite
- **Frontend:** React 19 + TypeScript (Vite), plain CSS
- **Design notes:** [`DECISIONS.md`](DECISIONS.md) (every choice, the alternatives and why) · [`PLAN.md`](PLAN.md) (the plan written before coding)

## How to run

Requirements: [uv](https://docs.astral.sh/uv/) and Node 20+.

```bash
# Terminal 1 — API on http://localhost:8000
cd backend
uv sync
uv run fastapi dev app/main.py

# Terminal 2 — UI on http://localhost:5173
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, create a link (e.g. `oncall`), then visit `http://localhost:8000/oncall`.
To try the "missing link" flow, visit `http://localhost:8000/anything-new`.

API docs (OpenAPI/Swagger): http://localhost:8000/docs

```bash
# Tests + coverage (backend)
cd backend && uv run pytest
```

### Configuration (env vars, all optional)

| Variable                | Default                   | Purpose                                     |
|-------------------------|---------------------------|---------------------------------------------|
| `GOLINKS_DATABASE_URL`  | `sqlite:///./golinks.db`  | SQLAlchemy URL                              |
| `GOLINKS_FRONTEND_URL`  | `http://localhost:5173`   | Where unknown slugs are sent to be created  |
| `GOLINKS_LOG_LEVEL`     | `INFO`                    | Python log level                            |
| `VITE_GO_BASE_URL`      | `http://localhost:8000`   | (frontend) Host the `go/…` links point to   |

## API

| Method | Path          | Result                                                        |
|--------|---------------|---------------------------------------------------------------|
| GET    | `/api/links`  | `200` list of links, sorted by slug                           |
| POST   | `/api/links`  | `201` created · `422` invalid slug/URL · `409` slug taken     |
| GET    | `/{slug}`     | `302` to the target · unknown slug → `302` to UI `?slug=…`    |
| GET    | `/health`     | `200 {"status": "ok"}`                                        |

```bash
curl -X POST localhost:8000/api/links \
  -H 'Content-Type: application/json' \
  -d '{"slug": "oncall", "target_url": "https://example.com/rota"}'
```

Every response includes an `X-Request-ID` header (generated, or propagated if the caller sent one). The same ID appears in every log line for that request:

```
INFO [39f3e302…] golinks.access: GET /oncall -> 302 (2.4 ms)
```

## Project layout

```
backend/app/
  main.py            app factory (settings injected → easy to test)
  config.py          env-based settings
  db.py              engine + per-request session
  models.py          Link table + request/response schemas + validation rules
  repository.py      data access; routes never touch SQL directly
  observability.py   request-ID middleware + log format
  routes/            links (API), redirect (/{slug}), health
backend/tests/       pytest, in-memory SQLite per test
frontend/src/
  api.ts             typed fetch client, maps API errors to form fields
  App.tsx            page, load/error states, "missing link" prefill
  CreateLinkForm.tsx accessible form with inline errors
  LinkList.tsx       table of links
```

## Assumptions

- **Internal tool, trusted network:** no authentication. Anyone who can reach it can create links. (The brief explicitly says auth isn't expected.)
- **The service owns the root path.** In production `go` would resolve via DNS/search domain to this host, so `go/oncall` → `http://go/oncall` → `GET /oncall`. Locally that host is `localhost:8000`.
- **Slugs are case-insensitive** and kebab-case (`design-system`), 1–64 chars. `api`, `health`, `docs` and `redoc` are reserved so they can't shadow app routes.
- **Targets must be http/https**, which blocks `javascript:`/`data:` URLs.
- **Links are immutable in v1.** The brief asks for create, view and visit, so edit and delete were left out on purpose.

## Tradeoffs I chose

- **302 instead of 301.** 301s are cached by browsers forever, so a target could never be changed and visits would be invisible to the server. 302 costs one round-trip per visit, which is negligible for an internal tool.
- **SQLite over Postgres.** Zero setup for reviewers. SQLModel/SQLAlchemy keeps the swap to Postgres to a connection-string change. Uniqueness is enforced by a DB constraint rather than check-then-insert, so concurrent creates can't race.
- **Repository layer, even for 3 queries.** It keeps routes thin and gives teammates one obvious place to add queries, at the cost of a little indirection.
- **Two dev processes (Vite proxy) instead of FastAPI serving the build.** This is the normal React + API workflow and avoids CORS. Shipping as a single process would be a small change (`StaticFiles` mount).
- **No frontend state library or UI kit.** Two components don't justify one. Accessibility comes from semantic HTML: labels, `aria-invalid`/`aria-describedby`, `role="alert"` for errors, a polite live region for success, and visible focus.
- **Backend tests only (100% coverage, 29 tests).** The business rules (validation, conflicts, redirects) live in the backend. The UI was checked manually in the browser.
- **No Docker, CI, migrations or metrics.** The brief asks for a small, thoughtful first iteration.

## If I had another day

1. **Edit and delete links**, with an owner field so people know whom to ask. This is where auth (SSO) would start to matter.
2. **Visit counts and last-visited time**, recorded on redirect (async or batched, so the redirect stays fast) and shown in the list. This also helps find dead links.
3. **Search/filter** in the list once there are more than a few dozen links.
4. **Alembic migrations** before the schema changes, plus Postgres in deployment.
5. **Frontend tests** (Vitest + Testing Library) for the form's error mapping and the prefill flow.
6. **Structured JSON logs and basic metrics** (request count and latency by route, redirect hit/miss ratio).
7. **Parameterized links** (`go/jira/ABC-123` → `…/browse/ABC-123`), which internal teams use heavily.
8. Run uvicorn with `--no-access-log` in production, since the app already logs one access line per request with the request ID.

## How I worked

I used an AI assistant (Claude Code) as a pair programmer. Before any code, it laid out options for each design question and I made the decisions, which are recorded with their reasoning in [`DECISIONS.md`](DECISIONS.md). The git history follows the steps in [`PLAN.md`](PLAN.md), one commit per step.
