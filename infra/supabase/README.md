# Supabase staging project

This is a maintainer-only checklist. None of it can be done from this
repository; it documents what to click/run once, by hand, against the real
Supabase dashboard and GitHub settings.

## 1. Create the project

- Name: `cabosueltos-staging`
- Region: `sa-east-1` (São Paulo)
- Postgres version: 17
- Plan: Free tier (R20's ops gate decides the paid plan later)

## 2. Disable the Data API

- Integrations → Data API → Overview → turn **Enable Data API** off.
  (Not Project Settings: the toggle lives under Integrations.)
- `ftm` must never be added to the exposed schemas list, whether the Data
  API is on or off.

## 3. Run the first migration

Use the **Session pooler** connection string (Dashboard → Connect →
Session pooler): host `aws-0-sa-east-1.pooler.supabase.com`, port 5432,
user `postgres.<project-ref>`. The direct host `db.<project-ref>.supabase.co`
resolves to IPv6 only, and GitHub-hosted runners have no IPv6. Session mode
keeps one server connection per client, so the migration runner's advisory
lock and DDL work. Never use the transaction pooler (port 6543).

Keep the values in a gitignored `.env.staging` at the repo root
(`APP_ENV=staging`, `DATABASE_URL`, `SUPABASE_URL`,
`SUPABASE_PUBLISHABLE_KEY`), then from `backend/`, once:

```bash
uv run --env-file ../.env.staging cabosueltos db migrate
```

## 4. Data API responses (recorded 2026-09-25)

Observed with the publishable key on `cabosueltos-staging`:

| Data API | Unknown table | `ftm` table with `Accept-Profile: ftm` | `/graphql/v1` | `/rest/v1/` root |
|---|---|---|---|---|
| Enabled | 404 `PGRST205` | 406 `PGRST106` ("Only the following schemas are exposed: public") | 404 `PGRST202` | 401 |
| Disabled (steady) | 503 `PGRST002` | 503 `PGRST002` | 503 `PGRST002` | 401 |
| Restarting after a toggle (< 30 s) | 503 `PGRST002` | 503 `PGRST002` | 503 `PGRST002` | 401 |

The root answers 401 ("Secret API key required") to any non-secret key in
both states, so it proves nothing. The probe
(`backend/tests/test_supabase_probe.py`) therefore requires `503 PGRST002`
from every endpoint on 3 samples 20 s apart, fails on any 2xx or any
enabled-state code, and errors on anything else. `auth/v1/settings` must
answer 200 first, so a bad key or a paused project can't pass as disabled.

## 5. Create the GitHub Environment

- Name: `staging`
- No required reviewers.
- Deployment branches: `main` only (manual `workflow_dispatch` from `main`
  is also allowed by the CI workflow).
- Secrets (nothing else from Supabase is stored):
  - `STAGING_DATABASE_URL`: the Session pooler URL (see step 3), port 5432
  - `STAGING_SUPABASE_URL`
  - `STAGING_SUPABASE_PUBLISHABLE_KEY`

## 6. Confirm CI end-to-end

Trigger the `ci.yml` workflow manually (`workflow_dispatch`) from `main`
and confirm `migrate-staging` and `supabase-probe` both go green.

## 7. One-time negative checks (do, verify red, then revert)

Both done on 2026-09-25:

- Data API turned on: endpoints answered 404 `PGRST205` / 406 `PGRST106`,
  which probe check 1 fails on. Turned back off: steady 503 `PGRST002`.
- `GRANT SELECT ON ftm.schema_migrations TO anon` inside a transaction: the
  grant count behind probe check 2 went from 0 to 1; rolled back to 0.

## Rollback

If the probe ever goes red on `main`, treat it as a stop-the-line signal:
disable the Data API (the target state) before doing anything else. To
tear the project down entirely: delete the Supabase project and the three
`staging` environment secrets in GitHub.

## Production

Not created here. The production Supabase project is created at the M1
launch gate, following the same checklist.
