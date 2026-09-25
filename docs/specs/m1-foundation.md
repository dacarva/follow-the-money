# M1 foundation: scaffold `backend/` + `apps/web`, Postgres 17, SQL migrations, CI, Supabase staging with a closed Data API

## Context

Cabos Sueltos has a locked M1 plan (`docs/designs/follow-the-money.md`, decisions R1-R45) and no code. Every M1 task imports from the `cabosueltos` package, writes to the private `ftm` schema, or runs in CI, so none of them can start until those exist. This issue builds that root: the two app skeletons, a local Postgres 17 that matches Supabase, a migration runner, a CI pipeline that gates lint, types, tests and the build, and a Supabase staging project whose Data API cannot read app tables. It merges eng-review tasks T1 and T15 and pulls in the i18n skeleton that design decision 22 requires "from the first commit" (design T11). The audience is the maintainer and the agents that build T2 onward.

## Current State (verified 2026-09-25)

- Repo contents: `docs/`, `DESIGN.md`, `TODOS.md`, `CLAUDE.md`, an empty `AGENTS.md`, `.gitignore` (5 entries: `.agents`, `.claude`, `.PERSONAL_RULES`, `.gstack`, `tmp`). No `backend/`, `apps/`, `docker-compose.yml`, `.env.example`, `.github/` or `infra/`.
- GitHub `dacarva/follow-the-money` exists, public, empty (no default branch).
- **Prerequisite, done by the maintainer when this issue is filed:** the planning docs are pushed as the first commit on `main`, which becomes the default branch. Implementation starts from a branch off `main`.
- No Supabase project exists.
- Decisions this issue implements:

| Decision | Source | What it fixes for this issue |
|---|---|---|
| Stack, package `cabosueltos`, modules `ids ingest resolver api db`, two entry points | `docs/designs/follow-the-money.md:172-176`, R26, eng D4 | Layout and names |
| FastAPI serves API + Vite build from one origin; dev uses the Vite `/api` proxy | R27 (`follow-the-money.md:176`) | Scaffold serves `index.html`; T17 adds per-route status rules |
| pytest + real Postgres 17 with `pg_trgm` + Hypothesis; Vitest + Testing Library | R13 as amended by R23 | Test stack. `docs/reviews/eng-review-test-plan-2026-09-25.md:6` still says Postgres 16; that line is superseded |
| Supabase Postgres 17; `DATABASE_URL` direct, `DATABASE_POOL_URL` pooler; private `ftm` schema; RLS deny-all on `public`; no `anon`/`authenticated` grants; CI probe with the publishable key; secrets only in env | R23 (`docs/reviews/eng-review-2026-09-25.md:1535-1545`) | Migration 0001, probe, env |
| es-CO only, every string in an ICU catalog, lint against literal UI strings, shared formatters; API returns raw values | design decision 22 (`docs/reviews/design-review-2026-09-25.md:216`) | Web i18n skeleton |
| Money columns "Millones COP", never "M" | `DESIGN.md:295-296` | Formatter behavior |
| Secrets, data files and Fontshare fonts are never committed | project rules, R30 | `.gitignore`, `.env.example` |

## Proposed Change

```
repo root
├── mise.toml                 python 3.14, node 24, uv, bun
├── docker-compose.yml        db: postgres:17 on host port 55432
├── .env.example              placeholders only
├── .github/workflows/ci.yml  backend · web · migrate-staging · supabase-probe
├── infra/supabase/README.md  staging project settings checklist
├── backend/
│   ├── pyproject.toml        uv project, scripts cabosueltos + cabosueltos-api
│   ├── migrations/0001_ftm_schema.sql
│   ├── cabosueltos/{__init__.py, settings.py, cli.py}
│   ├── cabosueltos/db/{__init__.py, migrate.py, pool.py}
│   ├── cabosueltos/api/{__init__.py, app.py}
│   ├── cabosueltos/{ids,ingest,resolver}/__init__.py   empty, owned by T2/T5/T3
│   └── tests/
└── apps/web/
    ├── package.json, bun.lock, vite.config.ts, tsconfig.json, eslint.config.js
    ├── src/{main.tsx, App.tsx}
    └── src/i18n/{es-CO.json, IntlProvider.tsx, format.ts}
```

### Implementation Details

**Toolchain (`mise.toml`)**: `python = "3.14"`, `node = "24"`, and `uv` and `bun` pinned to **exact versions**. The implementer resolves the current releases on day one (`mise latest uv`, `mise latest bun`) and writes those exact numbers; no committed file says `latest`. `apps/web/package.json` repeats the bun version in `packageManager` (`"bun@<version>"`). CI installs through `jdx/mise-action`, so local and CI read one file.

**JavaScript package manager: bun.** bun installs dependencies (text lockfile `bun.lock`, committed) and runs the `package.json` scripts with `bun run <script>`. Vite, Vitest (R13), ESLint and `tsc` keep running on Node 24, which is why Node stays pinned: `bun run` executes each tool's Node shebang, and no script uses `--bun`. Tests run with `bun run test` (Vitest), never `bun test` (bun's own runner, which R13 did not choose). No `package-lock.json`, `pnpm-lock.yaml` or `yarn.lock` is committed; CI fails if one appears.

**Backend (`backend/pyproject.toml`)**
- `requires-python = ">=3.14"`. Runtime deps: `fastapi`, `uvicorn[standard]`, `psycopg[binary,pool]` (v3), `pydantic-settings`, `typer`. Dev deps: `pytest`, `hypothesis`, `httpx`, `ruff`, `mypy`.
- Scripts: `cabosueltos = "cabosueltos.cli:app"`, `cabosueltos-api = "cabosueltos.api.app:run"`.
- `ruff` rules: `E,F,I,UP,B,SIM,S`; `ruff format`. `mypy --strict` on `cabosueltos/`.

**Settings (`cabosueltos/settings.py`)**, pydantic-settings, env only, no defaults for URLs:

| Var | Used by | Required |
|---|---|---|
| `APP_ENV` | all | yes: `local`, `ci`, `staging`, `production` |
| `DATABASE_URL` | CLI, migrations, tests | yes |
| `DATABASE_POOL_URL` | API | no; falls back to `DATABASE_URL` (R23) |
| `WEB_DIST_DIR` | API | no; default `../apps/web/dist` relative to `backend/` |
| `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` | probe tests only | only when running `-m supabase_probe` |

A missing required var exits with a message naming the var, never a stack trace.

**Migration runner (`cabosueltos/db/migrate.py`, CLI `cabosueltos db migrate` and `cabosueltos db status`)**
- Files: `backend/migrations/NNNN_slug.sql`, applied in numeric order.
- Takes `pg_advisory_lock(hashtext('cabosueltos.migrate'))`; a second concurrent run waits, it never double-applies.
- Bootstraps `CREATE SCHEMA IF NOT EXISTS ftm` and `ftm.schema_migrations (version text PRIMARY KEY, checksum text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())`.
- Each file runs in its own transaction together with its `schema_migrations` insert. A failure rolls back that file and exits 1.
- Checksum is SHA-256 of the file bytes. An applied file whose checksum changed makes `migrate` exit 1 with the version named; it never re-applies.
- `status` prints each version as `applied` or `pending`; exit 0.

**`backend/migrations/0001_ftm_schema.sql`**
```sql
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA extensions;

REVOKE ALL ON SCHEMA ftm FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA ftm FROM PUBLIC;

DO $$
DECLARE r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      EXECUTE format('REVOKE ALL ON SCHEMA ftm FROM %I', r);
      EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA ftm FROM %I', r);
      EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA ftm REVOKE ALL ON TABLES FROM %I', r);
      EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA ftm REVOKE ALL ON SEQUENCES FROM %I', r);
      EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA ftm REVOKE ALL ON FUNCTIONS FROM %I', r);
    END IF;
  END LOOP;
END $$;

-- R23: RLS deny-all on anything in public. A fresh project has no tables there;
-- this covers any that exist, and the PR check below fails any later public table without RLS.
DO $$
DECLARE t text;
BEGIN
  FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);
  END LOOP;
END $$;
```
The app never creates tables in `public`. The `pg_roles` guard lets the same file run on plain `postgres:17` (no Supabase roles) and on Supabase.

**API (`cabosueltos/api/app.py`)**
- `create_app()` factory; `run()` starts uvicorn on `0.0.0.0:${PORT:-8000}`.
- `GET /api/salud` → `200 {"estado": "ok", "db": "ok"}` after `SELECT 1` on the pool; `503 {"estado": "degradado", "db": "error"}` when the DB is unreachable (1 s connect timeout).
- Serves `WEB_DIST_DIR/assets/*` as static files and `index.html` for `/`. Any other non-`/api` path returns `index.html` with 200 for now; T17 replaces this with the per-route 200/302/404 rules. If `WEB_DIST_DIR` has no `index.html`, `/` returns 404 and the API still starts.

**Web (`apps/web`)**
- Vite + React 19 + TypeScript `strict`. Dev server proxies `/api` to `http://localhost:8000` (R27).
- Scripts: `dev`, `build`, `preview`, `test` (Vitest, jsdom), `lint` (`eslint . --max-warnings=0`), `typecheck` (`tsc --noEmit`), `format:check` (Prettier).
- i18n with FormatJS: `react-intl`; `src/i18n/es-CO.json` holds ICU messages; `IntlProvider.tsx` wraps the app with `locale="es-CO"`. ESLint: `typescript-eslint`, `eslint-plugin-react`'s `react/jsx-no-literals` (error, `noStrings: true`, `ignoreProps: false`, allow list empty, and `elementOverrides: { FormattedMessage: { ignoreProps: true } }` so only the catalog component takes literal props; a literal `aria-label` fails) and `eslint-plugin-formatjs` (recommended config). Tests and config files are exempt.
- `src/i18n/format.ts`, locale-parameterized, all `Intl`-based:
  - Both money formatters take an amount in **pesos** (the API's raw value), round half away from zero, and throw on negative, `NaN` or non-finite input. Neither handles a missing value; "sin valor reportado" belongs to T19.
  - `formatCOP(value: number)`: below 1.000 millones, whole pesos → `COP 450.000.000`; at or above 1.000 millones, whole millones → `COP 32.000 millones`. `formatCOP(0)` = `COP 0` (R43). `formatCOP(1_234.6)` = `COP 1.235`. `formatCOP(1_234_567_890_123)` = `COP 1.234.568 millones`. Never "M".
  - `formatMillonesCOP(value: number)`: plain es-CO number of whole millones for table cells. `32_000_000_000` → `32.000`; `450_000_000` → `450`; `1_500_000` → `2`; `0` → `0`; any amount above 0 and below 500.000 → `< 1`.
  - The display form is chosen **after** rounding to whole pesos: a rounded value of at least 10^9 pesos (1.000 millones) uses the millones form. So `999_999_999.4` → `COP 999.999.999`, and `999_999_999.6` → `COP 1.000 millones`.
  - `formatFecha(iso: string)`: accepts only a calendar date `YYYY-MM-DD` (the API sends dates without a time) and prints that same calendar date as `dd-mm-aaaa`, with no time-zone conversion: `2024-03-07` → `07-03-2024`. Timestamps, impossible dates (`2024-02-30`) and any other input throw.
- `App.tsx` renders one `<main>` with an `<h1>` whose text comes from the catalog key `app.titulo` = "Cabos Sueltos". No DESIGN.md tokens or fonts yet (T20 and the screen tasks own those).

**Local Supabase roles (`infra/postgres/init/00_supabase_roles.sql`)**: `CREATE ROLE anon NOLOGIN; CREATE ROLE authenticated NOLOGIN;`, each guarded by `IF NOT EXISTS` in a `DO` block. Compose mounts it into `/docker-entrypoint-initdb.d/`, and CI runs it with `psql` before `db migrate`, so the grant revokes in `0001` and the privilege tests run against the same roles Supabase has.

**Compose (`docker-compose.yml`)**: one service `db`, image `postgres:17`, `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?set in .env}` (compose refuses to start without it), `POSTGRES_DB=cabosueltos`, host port `55432`, named volume `pgdata`, healthcheck `pg_isready`. Local `DATABASE_URL` in `.env` points at user `postgres`, host `localhost`, port `55432`, database `cabosueltos`, with the same password; `.env.example` sets `POSTGRES_PASSWORD` to the literal local-only value `local-dev-only` and a matching local `DATABASE_URL`, so `cp .env.example .env` gives a working local setup; staging and production values never appear in any committed file. CI's service container sets its own throwaway password in the workflow env.

**`.env.example`**: every var from the Settings table plus `POSTGRES_PASSWORD`, one-line comment each; `APP_ENV=local`; local values as above; `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` left empty.

**`.gitignore` additions**: `.env`, `.env.*`, `!.env.example`, `apps/web/node_modules/`, `apps/web/dist/`, `apps/web/public/fonts/`, `backend/.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `data/`, `*.parquet`, `*.csv.gz`.

**CI (`.github/workflows/ci.yml`)**, on `pull_request`, `push` to `main`, and `workflow_dispatch`:

| Job | Runs when | Steps |
|---|---|---|
| `backend` | always | mise install → `uv sync --frozen` → `ruff check` → `ruff format --check` → `mypy --strict` → `psql -f infra/postgres/init/00_supabase_roles.sql` → `cabosueltos db migrate` → `pytest -m "not supabase_probe"` with a `postgres:17` service container. Includes the privilege tests (below), so every PR proves the closed state at the database level with no Supabase secrets |
| `web` | always | mise install → `bun install --frozen-lockfile` → `bun run lint` → `bun run format:check` → `bun run typecheck` → `bun run test` → `bun run build`; a step fails the job if `package-lock.json`, `pnpm-lock.yaml` or `yarn.lock` exists |
| `migrate-staging` | push to `main` or `workflow_dispatch`, after `backend` | `environment: staging`; `cabosueltos db migrate` with `DATABASE_URL=${{ secrets.STAGING_DATABASE_URL }}` |
| `supabase-probe` | push to `main` or `workflow_dispatch`, after `migrate-staging` | `environment: staging`; `pytest -m supabase_probe` with `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` mapped from the three `STAGING_*` secrets |

PR runs never touch staging and never receive secrets, so fork PRs work unchanged. The `staging` Environment has no required reviewers and allows only the `main` branch plus manual dispatch from `main`.

Concurrency group per ref cancels superseded runs; `migrate-staging` uses a single non-cancelling group so two pushes never race.

**Privilege tests (`backend/tests/test_privileges.py`, every CI run, local Postgres with the emulated roles)**
- P1: `SELECT count(*) FROM information_schema.role_table_grants WHERE table_schema = 'ftm' AND grantee IN ('anon', 'authenticated', 'PUBLIC')` = 0.
- P2: `SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND NOT rowsecurity` = 0.
- P3: `has_schema_privilege('anon', 'ftm', 'USAGE')` and the same for `authenticated` are both false.
- P4: connected as the migration role (the `DATABASE_URL` user, `postgres` locally, in CI and on Supabase; the test asserts `current_user` matches), the test creates a scratch table in `ftm` inside a rolled-back transaction; P1 still holds for it. `ALTER DEFAULT PRIVILEGES` only covers objects created by the role that ran it, so all app tables are created by migrations under this same role.

**Supabase probe (`backend/tests/test_supabase_probe.py`, marker `supabase_probe`, staging only)**. Every request sends `apikey` and `Authorization: Bearer` set to the publishable key. Responses were recorded on staging on 2026-09-25 (table in `infra/supabase/README.md`): with the Data API **disabled**, every endpoint answers `503` with code `PGRST002`; **enabled**, an unknown table answers `404 PGRST205` and `Accept-Profile: ftm` answers `406 PGRST106`. The `/rest/v1/` root answers 401 to any non-secret key in both states, so it is not checked. An enabled API also answers `503 PGRST002` for under 30 s while it restarts after a toggle, so one sample cannot prove the disabled state.
0. Sanity: `GET {SUPABASE_URL}/auth/v1/settings` returns 200. This proves the URL and publishable key are valid and the project is up; if it fails, the probe **errors** (red), it never passes.
1. Data API disabled: 3 samples, 20 s apart. Each sample requests an unknown table, `/graphql/v1`, and every `ftm` table (listed via `DATABASE_URL`; never empty because `ftm.schema_migrations` always exists) both with `Accept-Profile: ftm` and without it. Every response must be exactly `DATA_API_DISABLED_STATUS = 503` with `DATA_API_DISABLED_CODE = "PGRST002"`. Any 2xx fails; any enabled-state code (`PGRST205`, `PGRST106`, `PGRST202`) fails with "the Data API is enabled"; any other status or code **errors** (outage or platform change), never passes.
2. P1, P2 and P3 above, run against staging over `DATABASE_URL`.

**Supabase staging project (maintainer step, documented in `infra/supabase/README.md`)**
- Name `cabosueltos-staging`, region `sa-east-1` (São Paulo), Postgres 17, Free tier (the R20 ops gate decides the paid plan later).
- Data API: **disabled** at Integrations → Data API → Overview → "Enable Data API" off (not under Project Settings). `ftm` is never added to exposed schemas.
- The maintainer creates the GitHub Environment `staging` (no reviewers, deployment branch `main` only) and sets its three secrets.
- Connection: the **Session pooler** URL (Dashboard → Connect → Session pooler; port 5432, user `postgres.<project-ref>`). The direct host `db.<project-ref>.supabase.co` is IPv6-only and GitHub-hosted runners have no IPv6. Session mode keeps the migration runner's advisory lock working; the transaction pooler (6543) is never used.
- Right after creating the project, the maintainer puts `APP_ENV=staging`, `DATABASE_URL`, `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in a gitignored `.env.staging` at the repo root, runs `uv run --env-file ../.env.staging cabosueltos db migrate` once from `backend/`, then triggers the workflow manually to confirm `migrate-staging` and `supabase-probe` pass.
- GitHub Environment `staging` secrets: `STAGING_DATABASE_URL` (Session pooler, port 5432), `STAGING_SUPABASE_URL`, `STAGING_SUPABASE_PUBLISHABLE_KEY`. Nothing else from Supabase is stored.
- Production project: not created here; created at the M1 launch gate.

## Acceptance Criteria

1. On a clean clone with mise and Docker installed, `cp .env.example .env && mise install && docker compose up -d --wait db && cd backend && uv sync && uv run cabosueltos db migrate && uv run pytest -m "not supabase_probe"` exits 0. (`uv run` loads `../.env` via pydantic-settings' `env_file`.)
2. `cd apps/web && bun install --frozen-lockfile && bun run lint && bun run typecheck && bun run test && bun run build` exits 0 and writes `apps/web/dist/index.html`.
3. With the build present and the API running, `curl -s localhost:8000/api/salud` returns HTTP 200 with `{"estado":"ok","db":"ok"}`; with `db` stopped it returns 503 within 2 s.
4. `curl -s localhost:8000/` returns the built `index.html`, and the page shows "Cabos Sueltos" from the catalog.
5. `cabosueltos db migrate` run twice applies `0001` once; `db status` then lists `0001 applied`.
6. Editing an applied migration file makes `db migrate` exit 1 and name the version.
7. Two concurrent `db migrate` runs on an empty DB leave exactly one row per version in `ftm.schema_migrations`.
8. `SELECT extname FROM pg_extension` includes `pg_trgm` on compose, CI and staging.
9. A JSX file containing `<p>Hola</p>` fails `bun run lint`; the same text through `<FormattedMessage id="…" />` passes.
10. Every example listed under `format.ts` above holds as a unit test, plus `formatFecha("2024-03-07")` = `07-03-2024`; negative input to either money formatter throws. No formatter output contains a standalone "M".
11. The PR's CI run has `backend` (including P1-P4) and `web` green, with no job reading a secret; after merge, `migrate-staging` then `supabase-probe` are green on `main`.
12. All three probe tests pass against staging. Two negative checks are done once by hand and then reverted: turning the Data API on makes probe check 1 fail (endpoints answer `404 PGRST205` / `406 PGRST106`); granting `SELECT` on `ftm.schema_migrations` to `anon` makes the P1 count in probe check 2 non-zero.
13. `git ls-files` contains no `.env` (except `.env.example`), no font files, and no data files.
14. The first test plan's "Postgres 16" line carries a note pointing to R23.

## Testing Plan

| Layer | What | Count |
|---|---|---|
| Unit (py) | Settings: missing var message, pool URL fallback, `APP_ENV` validation | +3 |
| Unit (py) | Migration ordering and checksum computation (Hypothesis over file names) | +2 |
| Integration (py, real Postgres 17) | migrate applies once; idempotent rerun; checksum mismatch exits 1; concurrent runs; failed file rolls back; `pg_trgm` present | +6 |
| Integration (py, privileges) | P1-P4 | +4 |
| Integration (py) | `/api/salud` 200 and 503; `/` serves `index.html`; missing dist → 404 and app still starts | +4 |
| Probe (py, staging) | Sanity, disabled Data API (3 samples), privileges | +3 |
| Unit (web) | `formatCOP` (each listed example, exactly 1.000 millones, negative and `NaN` throw), `formatMillonesCOP` (each listed example, `< 1` boundary at 499.999 and 500.000), `formatFecha` (valid, invalid) | +14 |
| Component (web) | `App` renders the catalog title inside `<main>` | +1 |
| Lint fixture (web) | Literal JSX string fails ESLint | +1 |

## Rollback Plan

Code: revert the PR; nothing depends on it yet. Database: `0001` only creates a schema, an extension and revokes grants; drop `ftm` on staging if needed (no data exists). Supabase: delete the staging project and the three GitHub secrets. If the probe ever fails on `main`, treat it as a stop: disable the Data API (already the target state) before any other work.

## Effort Estimate

| Part | Human | CC |
|---|---|---|
| mise, compose, `.gitignore`, `.env.example` | 2 h | 5 min |
| Backend skeleton, settings, API, CLI | 4 h | 20 min |
| Migration runner + `0001` + tests | 5 h | 25 min |
| Web skeleton + i18n + formatters + lint rules + tests | 5 h | 30 min |
| CI workflow (4 jobs, environments, concurrency) | 3 h | 20 min |
| Supabase staging project, secrets, probe tests, README | 3 h | 20 min (plus the maintainer's dashboard steps) |
| **Total** | **~2.75 days** | **~2 h** |

## Files Reference

| File | Change |
|---|---|
| `mise.toml` | New: tool pins |
| `docker-compose.yml` | New: `db` on Postgres 17 |
| `.env.example` | New: placeholders |
| `.gitignore` | Add env, build, cache, font and data entries |
| `.github/workflows/ci.yml` | New: 4 jobs |
| `infra/postgres/init/00_supabase_roles.sql` | New: emulated `anon` / `authenticated` roles for local and CI |
| `infra/supabase/README.md` | New: staging settings checklist and secret names |
| `backend/pyproject.toml`, `backend/uv.lock` | New |
| `backend/cabosueltos/settings.py` | New: env settings |
| `backend/cabosueltos/cli.py` | New: `db migrate`, `db status` |
| `backend/cabosueltos/db/{migrate,pool}.py` | New |
| `backend/cabosueltos/api/app.py` | New: factory, `/api/salud`, static serving |
| `backend/cabosueltos/{ids,ingest,resolver}/__init__.py` | New, empty |
| `backend/migrations/0001_ftm_schema.sql` | New |
| `backend/tests/` | New: settings, migrate, api, privilege and probe tests |
| `apps/web/*` | New: Vite app, ESLint, Prettier, Vitest config |
| `apps/web/src/i18n/{es-CO.json,IntlProvider.tsx,format.ts}` | New |
| `docs/reviews/eng-review-test-plan-2026-09-25.md:6` | Note that Postgres 16 is superseded by R23 (17) |

## Out of Scope

- Staging login and JWT middleware (T16).
- Per-route serving rules, CSP and `X-Robots-Tag` (T17).
- Font pipeline and DESIGN.md tokens (T20).
- Domain tables, ingest, resolver, ID normalization (T2-T7).
- Playwright E2E (T10, needs the golden fixture) and axe.
- The deploy workflow and the hosting target (separate issue).
- Supabase production project (launch gate).
- NIT and masked-ID display formatting (T2 and the screen tasks).
- Repo and package rename from `TODOS.md`.

## Related

- Plan: `docs/designs/follow-the-money.md` (Stack, R23, R26, R27)
- Eng review 1 tasks T1, T15: `docs/reviews/tasks-eng-review-2026-09-25.jsonl`
- Design review task T11 (i18n): `docs/reviews/tasks-design-review-2026-09-25.jsonl`
- Unblocks: T2 (ids), T4 (tables), T16, T17, T20 and every web task
