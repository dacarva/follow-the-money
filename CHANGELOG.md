# Changelog

All notable changes to this project are documented in this file.

## [0.1.0.0] - 2026-09-25

### Added

- Backend service (`backend/`, FastAPI + Python): a `/api/salud` health
  endpoint backed by a pooled Postgres connection, and static serving of the
  built web app with a SPA fallback route.
- A SQL migration runner with a CLI (`cabosueltos db migrate`, `cabosueltos db
  status`): applies numbered migrations under an advisory lock, tracks
  checksums so an already-applied migration can't silently change, and is
  safe to run concurrently.
- The first schema migration: a private `ftm` schema with `pg_trgm`, no
  grants for the `anon`/`authenticated` roles, and row-level security
  enabled on anything in `public` — locked down before any table exists.
- A local Postgres 17 dev/CI environment (`docker-compose.yml`) that emulates
  Supabase's `anon`/`authenticated` roles, so privilege checks run the same
  locally, in CI, and against real Supabase staging.
- Web app scaffold (`apps/web/`, Vite + React 19 + TypeScript strict, via
  bun): a Spanish (es-CO) message catalog with `react-intl`, currency (COP)
  and date formatters, and a lint rule that fails the build on literal UI
  text or props instead of translated messages.
- CI on every pull request: backend lint/format/typecheck/tests and
  Postgres privilege checks, plus web lint/format/typecheck/tests/build.
  A separate main-only pipeline stage migrates the Supabase staging database
  and probes that its Data API stays disabled.
- A Supabase staging setup checklist (`infra/supabase/README.md`) recording
  the project's Data API behavior in both states, so the staging probe's
  expectations are traceable to an observed baseline.

### Fixed

Hardening found by this release's own pre-landing review, before anything
shipped:

- The migration runner now sorts by numeric version instead of lexically
  (so a future `10_x.sql` can't sort before `2_x.sql`), rejects `.sql` files
  that don't match its naming convention instead of silently skipping them,
  rejects two files sharing the same version number, and fails loudly if its
  migrations directory is missing entirely (a wheel-based install that
  didn't package `migrations/` would otherwise report success while quietly
  skipping every privilege and RLS setup step).
- A killed migration run can no longer wedge every future `migrate` call
  behind an unreleased advisory lock indefinitely — the connection now
  bounds the wait with a 30s lock timeout.
- The local `docker-compose` Postgres port no longer binds to every host
  interface; it's now `127.0.0.1`-only.
- `/api/salud`'s connection pool is now closed off the event loop on
  shutdown, and the `/assets` static mount no longer crashes the whole app
  with an unhandled 500 the first time it's hit before a web build exists.
- CI's workflow-level concurrency cancellation could kill an in-flight
  staging migration out from under its own non-cancelling job-level guard
  when a second push landed quickly; the outer group is now scoped so a
  `push:main` run is never cancelled by another. `migrate-staging` also
  gets a 10-minute timeout and now reports `APP_ENV=staging` instead of the
  inherited `ci` default.
- `formatFecha`'s leap-year check no longer misclassifies years 0-99 (a
  legacy two-digit-year quirk of the `Date` constructor it used to rely on).
