# Decision Log

Each entry: the options considered, what was chosen, and why.
Built with an AI assistant (Claude Code) acting as the implementer; every architectural decision below was made by me after reviewing the options it proposed.

---

## D1 — Which project
- **Options:** Go Links, Service Status Dashboard, Feature Flag Manager, API Explorer, Workflow Inbox, Team Directory, existing project.
- **Chosen:** Go Links.
- **Why:** Small, well-bounded domain with an interesting backend core (HTTP redirect semantics, slug validation, uniqueness) that fits a Python + React role.

## D2 — Architecture / stack
- **Options:** FastAPI + React (Vite) · FastAPI + server-rendered HTML · API-only (Swagger as UI) · Django + templates.
- **Chosen:** FastAPI + React (Vite, TypeScript).
- **Why:** Matches the role (Python + React). The brief values UX and accessibility, which need a real UI. FastAPI gives typed validation and OpenAPI docs for free.

## D3 — Persistence
- **Options:** SQLite + SQLModel · SQLite + raw `sqlite3` · in-memory dict · JSON file.
- **Chosen:** SQLite + SQLModel.
- **Why:** Real persistence with zero infrastructure. A UNIQUE constraint makes the DB the source of truth for slug collisions (no race between check-and-insert). Easy path to Postgres later.

## D4 — How AI was used / documented
- **Options:** PLAN.md + DECISIONS.md · plus a CLAUDE.md · agent harness / multi-agent · no AI docs.
- **Chosen:** PLAN.md + DECISIONS.md.
- **Why:** Lightweight and reviewable. A full agent harness would be over-engineering for a 60-minute exercise, which goes against the brief's "you don't need to impress us".

## D5 — Repository hosting
- **Context:** The brief only requires "a Git repository", not GitHub specifically.
- **Options:** Public GitHub · private GitHub · local git only.
- **Chosen:** Public GitHub repo (`wolfhund/go-links`).
- **Why:** Easiest for reviewers to access with a single link.

## D6 — Redirect semantics
- **Options:** 302 on `GET /{slug}` · 301 permanent · 307 on `/go/{slug}`.
- **Chosen:** 302 Found on `GET /{slug}`.
- **Why:** Browsers don't cache it, so updating a link's target takes effect immediately and every visit hits the server (which enables analytics later). 301 would get cached forever by clients.

## D7 — Slug rules
- **Options:** strict kebab-case · hierarchical (`team/oncall`) · free text.
- **Chosen:** Strict kebab-case, `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars, lowercased, with reserved words blocked. Duplicate → 409 Conflict.
- **Why:** Predictable and easy to type and share. Lowercasing avoids `OnCall` vs `oncall` duplicates. Reserved words prevent shadowing API routes.

## D8 — Feature scope
- **Options considered:** visit counter, search/filter, edit/delete, owner/description.
- **Chosen:** None. Only what the brief asks: create, list, redirect.
- **Why:** The brief rewards prioritization under a time limit. Extras are listed under "next day" in the README.

## D9 — Observability
- **Options:** request ID + structured logs + `/health` · basic logging only · plus Prometheus metrics.
- **Chosen:** Request-ID middleware (`X-Request-ID` generated or propagated, echoed in the response, included in logs), one access-log line per request, and `/health`.
- **Why:** Cheap (~30 lines) and covers the core of what an operator needs to trace a request. Metrics are overkill for v1.

## D10 — Testing
- **Options:** backend pytest >80% coverage · backend + frontend (Vitest) · smoke tests only.
- **Chosen:** Backend pytest with >80% coverage.
- **Why:** The backend holds the business rules (validation, conflicts, redirects). Frontend tests were left out for time and are listed as a next step.

## D11 — Tooling / runtime
- **Options:** uv + npm (two processes, Vite proxy) · pip + venv + npm · FastAPI serves the built frontend.
- **Chosen:** uv + npm, two processes; the Vite dev server proxies `/api` to FastAPI.
- **Why:** uv is fast and has a lockfile. Two dev processes is the standard React + API workflow.

## D12 — Frontend approach
- **Options:** React + TS + plain CSS · + Tailwind · + TanStack Query · React with JS.
- **Chosen:** React + TypeScript + plain CSS, `fetch` + `useState`.
- **Why:** No extra dependencies for two components. Focus on semantic HTML, labels, `aria-live` error messages and visible focus (accessibility).

## D13 — Unknown slug behavior
- **Options:** 302 to UI with prefilled create form · 404 JSON · 404 HTML page.
- **Chosen:** 302 to the UI with `?slug=<slug>` so the create form is prefilled ("go/foo doesn't exist yet — create it").
- **Why:** The classic go-links UX: a miss becomes a creation opportunity instead of a dead end.

## D14 — Allowed target URLs
- **Options:** http/https only · any scheme · http/https + loop detection.
- **Chosen:** http/https only (Pydantic `HttpUrl`).
- **Why:** Blocks `javascript:` / `data:` / `file:` targets, which are an XSS vector. Loop detection is a nice-to-have for later.

## D15 — Language
- **Chosen:** English for code, docs, commits and UI.
- **Why:** The brief is in English, and English is the working language with clients.

## D16 — Time management
- **Options:** commit per step, no strict timebox · strict 60-min timebox · single final commit.
- **Chosen:** One commit per plan step, no strict timebox. AI assistance is disclosed in the README.
- **Why:** The git history shows how the work progressed and makes the decisions easy to review.

## D17 — Single command to run the monorepo
- **Context:** D11 meant starting two processes in two terminals, which is awkward for reviewers.
- **Options:** root Makefile (`make dev` runs both in parallel) · root `package.json` + `concurrently` · FastAPI serves the built UI (one process) · `dev.sh` script.
- **Chosen:** Root Makefile with `install`, `dev` and `test` targets.
- **Why:** Zero extra dependencies (make ships with macOS and Linux), a conventional entry point for a mixed Python/JS repo, and it keeps Vite hot-reload. Serving the build from FastAPI would cost the dev loop.

---

## Notes found during implementation

- **API schemas are plain Pydantic models, not SQLModel.** SQLModel's `Field` doesn't support `pattern`. Splitting the table model (`Link`) from the request/response schemas (`LinkCreate`, `LinkRead`) also keeps the API contract separate from storage.
- **Friendly validation messages in the UI.** Pydantic's default copy (`String should match pattern '^[a-z0-9]+…'`) is accurate but unfriendly, so the API client maps known error types to plain language and keeps the server messages for everything else.
- **Bug caught in manual browser testing:** after creating a link from the "go/x doesn't exist yet" flow, the notice stayed on screen and success was only announced to screen readers. Fixed by making the notice state and showing a visible success message (still in a live region).
- **Duplicate access logs:** uvicorn's own access log duplicates the app's request-ID access line. This is left as is in dev and noted for production (`--no-access-log`).
