# Implementation Plan — Go Links

First iteration of an internal URL shortcut service (`go/oncall` → long URL).
Scope is exactly what the brief asks for: **create**, **list**, **visit & redirect**.

## Architecture

```
go-links/
├── backend/                 FastAPI + SQLModel + SQLite (uv)
│   ├── app/
│   │   ├── main.py          app factory, routers, middleware wiring
│   │   ├── config.py        settings (DB URL, frontend URL)
│   │   ├── db.py            engine + session dependency
│   │   ├── models.py        Link table + API schemas (create/read)
│   │   ├── repository.py    data access (get by slug, list, create)
│   │   ├── routes/
│   │   │   ├── links.py     /api/links  (GET list, POST create)
│   │   │   └── redirect.py  /{slug}     (302 to target or to UI)
│   │   └── observability.py request-ID middleware + structured logging
│   └── tests/               pytest + TestClient, in-memory SQLite
├── frontend/                React + TypeScript (Vite), plain CSS
│   └── src/
│       ├── api.ts           typed fetch client
│       ├── App.tsx          page layout, reads ?slug= prefill
│       ├── CreateLinkForm.tsx
│       └── LinkList.tsx
├── README.md
├── PLAN.md
└── DECISIONS.md
```

## API

| Method | Path          | Success              | Errors                                  |
|--------|---------------|----------------------|-----------------------------------------|
| GET    | `/api/links`  | 200 `Link[]`         | —                                       |
| POST   | `/api/links`  | 201 `Link`           | 422 invalid slug/URL, 409 slug taken    |
| GET    | `/{slug}`     | 302 → target URL     | unknown slug → 302 to UI `?slug=<slug>` |
| GET    | `/health`     | 200 `{status: ok}`   | —                                       |

`Link = { slug, target_url, created_at }`

Validation:
- slug: lowercased, `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars, not reserved (`api`, `health`, `docs`, `openapi.json`, `redoc`).
- target_url: Pydantic `HttpUrl` (http/https only).
- Uniqueness enforced by a DB UNIQUE constraint (source of truth), surfaced as 409.

Every response carries `X-Request-ID` (propagated if the client sent one); each request logs one line: request id, method, path, status, duration ms.

## Steps (one commit each)

1. Scaffold: `git init`, backend with `uv`, frontend with Vite React-TS, `.gitignore`.
2. Backend model + repository + DB session.
3. `/api/links` endpoints with validation and 409 handling.
4. Redirect route (302 found / 302 to UI prefilled).
5. Observability: request-ID middleware, logging, `/health`.
6. Tests: pytest, >80% coverage.
7. Frontend: API client, list, create form (labels, aria-live errors, prefill from `?slug=`), Vite proxy.
8. README (run, assumptions, tradeoffs, next day) + finalize DECISIONS.md.
9. Root Makefile: `make install`, `make dev`, `make test` (added after review, see D17).
10. Create public GitHub repo `wolfhund/go-links` and push (only after explicit OK).

## Out of scope (documented in README "next day")

Edit/delete, visit counter, search, owner/description, auth, Docker, CI/CD, frontend tests.
