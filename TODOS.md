# TODOS

## Legal & privacy

### Resolve the open office-hours correction-flow concerns before the M1 legal review

**What:** Update the design doc (`docs/designs/follow-the-money.md` and the gstack copy) for office-hours concerns R3-10, R3-11, R3-12, R3-13.

**Why:** All four are M1 correction-flow obligations the lawyer will review; three carry legal exposure (impersonation, ID-document retention, missed Ley 1581 deadlines).

**Context:** From /plan-eng-review 2026-09-25 (decision D27). Fixes:
- R3-10: only verified requesters get annotations labeled "a solicitud del titular"; unverified ones are labeled "declaración de un tercero no verificado" and moderated, or not offered.
- R3-11: drop the blanket "15 business days"; state consulta 10 and reclamo 15 business days.
- R3-12: say where requester ID copies live (e.g. encrypted mailbox or vault), who can read them (moderator only), retention (ticket close + legal hold) and deletion.
- R3-13: name a backup moderator or an escalation path; re-measure the suspect-ID queue on national data before launch; Ley 1581 deadlines take priority over the suspect-ID queue.
The other 12 office-hours concerns were resolved in the eng review or moved to the M3 review (see Planning below).

**Effort:** S
**Priority:** P1
**Depends on:** Must be done before booking the M1 legal review.

### Ask the M1 legal review whether natural-person entity pages may be indexed by search engines

**What:** Add "index or noindex natural-person entity pages (legal reps, ordenadores, supervisors)" to the M1 legal-review agenda.

**Why:** A person's name in search results next to public contracts is a larger privacy footprint than the same data inside the site, and Ley 1581 suppression is slow to undo once a search engine holds it.

**Context:** From /plan-eng-review (re-review) 2026-09-25, decision D13. Company and agency pages are indexable; lead views are already `noindex` (design line 131). The switch is R27's per-route `X-Robots-Tag` header, so either answer costs nothing to apply.

**Effort:** S
**Priority:** P2
**Depends on:** Booking the M1 legal review.

## Ingest

### Register a datos.gov.co (Socrata) app token

**What:** Register an app token on datos.gov.co and set it in the deploy secret store as the ingest env var the client reads for `X-App-Token`.

**Why:** Anonymous clients are throttled harder; the initial 6M-row SECOP pull and the weekly `:id` sweep could exceed the 6-hour refresh limit in the ops gate.

**Context:** From /plan-eng-review 2026-09-25 (decision D28). The ingest client sends `X-App-Token` from an environment variable from the first commit (anonymous when unset); only the registration is left. Never commit the token.

**Effort:** S
**Priority:** P2
**Depends on:** Before the pre-widening ops-gate measurement on staging.

### Measure whether SECOP Proveedores Registrados is needed as a second current-rep source

**What:** After M1 launch, count company contractors with no RUES current legal rep but a valid rep in SECOP Proveedores Registrados (`qmzu-gj57`). If more than 5% of company contractors, add a reachable-only adapter that never ingests rep phone or email.

**Why:** Foreign suppliers and entities outside cámaras de comercio have no RUES rep, so the "other contractors" hop is dead for them.

**Context:** From /plan-eng-review 2026-09-25 (decision D30; D5 chose RUES only). `qmzu-gj57` has 1,614,430 suppliers, CC BY-SA 4.0, and a rep-document field full of junk placeholders (`-`, `.`, `0`, `000000`, `0-0-0-`). Reuse the typed-record, hash, version and sweep patterns.

**Effort:** M
**Priority:** P3
**Depends on:** M1 launch.

## Engineering

### Confirm migrate-staging and supabase-probe go green after merging to main

**What:** After PR #2 merges (or a manual `workflow_dispatch` from `main`), confirm the `migrate-staging` and `supabase-probe` CI jobs both run and pass — they're gated to `push:main`/`workflow_dispatch` and are correctly skipped on this PR's own `pull_request` run, so they've never actually executed yet.

**Why:** Deferred from plan: docs/specs/m1-foundation.md (AC11/AC12) — plan completion audit classified this NOT DONE because no push to `main` has happened yet; it's expected to stay open until after merge, not a gap in this PR.

**Context:** From /ship plan-completion audit, 2026-09-25. Also confirm (manually, in the Supabase dashboard — out of scope for this agent to check) that the staging project's Data API is disabled and `ftm` isn't in the exposed-schemas list, per `infra/supabase/README.md`.

**Effort:** S
**Priority:** P1
**Depends on:** Merging PR #2.

### Ship migrations/ with the backend before any wheel-based deployment

**What:** `MIGRATIONS_DIR` is resolved as a sibling of the `cabosueltos` package (`backend/migrations/`), but the configured wheel only packages `cabosueltos/`. Installing that wheel without the source tree gives the migration runner an empty (now: missing, and loudly erroring) migrations directory.

**Why:** Confirmed independently by two Codex reviews (adversarial + structured, P1). Not exploitable today — CI and staging both run `uv run cabosueltos db migrate` from a source checkout, never from an installed wheel — but the runner now fails loudly (`MigrationsDirectoryMissingError`) instead of silently reporting success with zero migrations applied, which was the actual danger (it would have skipped the privilege revokes and RLS setup with no error). That loud-failure guard ships in this PR; only the actual packaging fix (or a documented "always run from source" policy) is deferred.

**Context:** From /ship pre-landing review (Codex adversarial + structured review), 2026-09-25. `backend/cabosueltos/db/migrate.py`, `backend/pyproject.toml`.

**Effort:** S
**Priority:** P2
**Depends on:** Before any deployment method that installs the backend as a built wheel rather than running from the checkout.

### Decide whether ftm tables need FORCE ROW LEVEL SECURITY

**What:** `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` (migration 0001, and the template for future migrations) doesn't set `FORCE ROW LEVEL SECURITY`. Postgres lets the table owner (and superusers) bypass RLS unless FORCE is also set.

**Why:** If the migration/app role ends up owning the tables it creates (likely), every query it runs bypasses any RLS policy written on those tables later — a silent trust-boundary gap that's much cheaper to close in the migration template now, before the first real policy exists, than to retrofit after.

**Context:** From /ship pre-landing review (Claude adversarial subagent), 2026-09-25. No tables/policies exist in `ftm` yet, so nothing is exposed today.

**Effort:** S
**Priority:** P2
**Depends on:** Before the first migration that adds a real RLS policy.

### Give /api/* a shared JSON error envelope

**What:** Define a shared error shape (e.g. `{"error": {"code": ..., "message": ...}}`) and use it for every `/api/*` response, including the unmatched-path 404 the SPA catch-all currently returns as a bare empty-body `Response(status_code=404)`.

**Why:** `/api/salud`'s 503 already returns a structured JSON body (`{"estado": "degradado", "db": "error"}`) but the unmatched-route 404 doesn't return JSON at all — two different error shapes from day one. Cheap to fix now, before more endpoints copy the inconsistency.

**Context:** From /ship pre-landing review (API Contract specialist), 2026-09-25. `backend/cabosueltos/api/app.py`.

**Effort:** S
**Priority:** P2
**Depends on:** None.

### Move /api/* routes onto a dedicated APIRouter before the SPA catch-all

**What:** Register current and future `/api/*` routes on an `APIRouter(prefix="/api")` and `include_router()` it before mounting the SPA catch-all route, instead of relying on source-order plus the manual `full_path.startswith("api/")` check.

**Why:** Any new API route added after the catch-all in file order will silently 404 through the SPA fallback instead of reaching its handler — nothing enforces the ordering today.

**Context:** From /ship pre-landing review (API Contract specialist), 2026-09-25. `backend/cabosueltos/api/app.py`.

**Effort:** S
**Priority:** P2
**Depends on:** None.

### Adopt an /api/v1 prefix before any external client depends on /api/salud

**What:** Add a version prefix (e.g. `/api/v1/salud`) before load balancers, uptime monitors, or mobile clients start hardcoding the unversioned path.

**Why:** Free to add now; a breaking change to retrofit once real consumers exist.

**Context:** From /ship pre-landing review (API Contract specialist), 2026-09-25.

**Effort:** S
**Priority:** P2
**Depends on:** None.

### Declare a response_model for /api/salud

**What:** Define Pydantic models for the 200/503 shapes and declare them via `response_model=`/`responses=` on the route so the auto-generated OpenAPI docs match actual behavior.

**Why:** Right now FastAPI can't infer a schema from the raw `JSONResponse` return type, so `/docs` and `/openapi.json` don't document the 503 case — a documentation-drift precedent from the very first endpoint.

**Context:** From /ship pre-landing review (API Contract specialist), 2026-09-25. `backend/cabosueltos/api/app.py`.

**Effort:** S
**Priority:** P3
**Depends on:** None.

### Decide a rollback policy for the SQL migration runner before a migration touches real data

**What:** Either document forward-only migrations as deliberate policy (roll-forward fixes only), or add a paired down-file convention (e.g. `000N_name.down.sql`) plus a `db rollback` CLI command.

**Why:** `backend/cabosueltos/db/migrate.py` only ever applies forward; migration 0001 is safe (empty schema) but the pattern has no rollback story once migrations start mutating populated tables.

**Context:** From /ship pre-landing review (Data Migration specialist), 2026-09-25.

**Effort:** M
**Priority:** P3
**Depends on:** Before a migration that isn't purely additive on an empty schema.

### Distinguish "DB unreachable" from "pool momentarily saturated" in /api/salud

**What:** `salud()` catches a bare `except Exception` around the pooled connection attempt, so a `PoolTimeout` (pool exhausted under a request burst) is reported identically to the database actually being down.

**Why:** Harmless with zero production traffic today, but an external health-checker/orchestrator can't tell the two apart once there's real load, which is exactly the kind of ambiguity that causes bad auto-remediation (restart loops).

**Context:** From /ship pre-landing review (Claude adversarial subagent), 2026-09-25. `backend/cabosueltos/api/app.py`. Needs a human call on pool sizing + health-check semantics, not a mechanical fix.

**Effort:** S
**Priority:** P3
**Depends on:** None.

### Note the fresh-volume-only limitation of the Supabase role init script

**What:** `infra/postgres/init/00_supabase_roles.sql` only runs via `docker-entrypoint-initdb.d`, which Postgres only executes against a brand-new data volume. A developer with a pre-existing `pgdata` volume from before this PR won't get the `anon`/`authenticated` roles, and `test_privileges.py` will fail with a confusing role-does-not-exist error unrelated to their actual change.

**Why:** CI is unaffected (always a fresh container); this is a local-dev-only DX gotcha worth a one-line README note (`docker compose down -v` after pulling this change).

**Context:** From /ship pre-landing review (Claude adversarial subagent), 2026-09-25.

**Effort:** S
**Priority:** P4
**Depends on:** None.

### Revisit the Supabase Data API probe's restart-window false-negative risk

**What:** The staging probe accepts three `503 PGRST002` samples 20s apart as proof the Data API is disabled, but the project's own recorded observations show an *enabled* API returns that same code while restarting after a toggle (<30s). If a restart happens to span the whole sampling window, the probe would pass even though the API is actually enabled once the restart finishes.

**Why:** Narrow timing window, but it's the one way this specific probe design could give a false "disabled" reading on the exact thing it exists to guard.

**Context:** From /ship pre-landing review (Codex adversarial review), 2026-09-25. `backend/tests/test_supabase_probe.py`, `infra/supabase/README.md`. Needs the maintainer's judgment on probe design, not a mechanical fix — and verifying it means touching the real staging Data API, which this agent is not permitted to do.

**Effort:** M
**Priority:** P3
**Depends on:** None.

### Stop hardcoding migration-runner test fixture versions

**What:** `backend/tests/test_migrate_integration.py` uses fixed literal versions ("9001"-"9006") cleaned up by fixture teardown. Because local dev uses a persistent `docker-compose` volume, a run interrupted before teardown leaves a stale applied version that fails the next run's idempotency assertion for unrelated reasons.

**Why:** Confusing false-failure mode for local dev after a Ctrl-C or crash mid-test-run.

**Context:** From /ship pre-landing review (Testing specialist), 2026-09-25.

**Effort:** S
**Priority:** P4
**Depends on:** None.

## Planning

### Claim the Cabos Sueltos name and rename the repo and package

**What:** Register `cabosueltos.co` (and `.com.co`), create the `cabosueltos` GitHub org, reserve `cabosueltos` on PyPI, rename the repo from `follow-the-money`, and use `cabosueltos` as the Python package name in the eng T1 scaffold.

**Why:** The name was chosen on 2026-09-25 and all four were free that day, but nothing is claimed yet. Renaming after launch breaks shared links and press mentions.

**Context:** From /design-consultation 2026-09-25 (D5). Availability checked with whois and the PyPI/GitHub APIs. The design doc and eng review still say "follow-the-money"; update them in the same pass.

**Effort:** S
**Priority:** P1
**Depends on:** Nothing. Blocks the T1 scaffold's package name.

### Run /plan-eng-review before M2 and before M3, with carried items

**What:** Run an eng review before starting M2 and again before M3.
- M2 carries: the M1 legal review's answer on CC BY-SA × CC BY-NC × ODbL compatibility; PEP source choice (OpenSanctions CC BY-NC vs the primary Función Pública source); typed-record adapters per source; the M2 exit criterion renamed to "a reviewed suspect-ID report".
- M3 carries office-hours concerns R3-6 (ICIJ free-text name parsing), R3-7 (multi-key blocking), R3-8 (country in blocking drops cross-border cases), R3-9 (define "co-linked entity"), R3-14 (confirmed / refuted / unresolved metric), R3-15 (ODbL share-alike for derived leads).

**Why:** The 2026-09-25 eng review locked only M1 (decision D3). These items are already known and would otherwise be rediscovered.

**Context:** The M1 eng review report (`docs/reviews/eng-review-2026-09-25.md`) lists decisions R1-R22 that M2/M3 must stay compatible with (own identity tables, in-transaction propagation, versioned typed source records).

**Effort:** S
**Priority:** P2
**Depends on:** M1 launch (M2 review); M2 exit (M3 review).

## Completed

### Pick the product name (design Open Question 3)

**Completed:** 2026-09-25 in /design-consultation. The name is **Cabos Sueltos** (slug `cabosueltos`). Claiming it is the P1 item above.

### Create DESIGN.md with /design-consultation

**Completed:** 2026-09-25. `DESIGN.md` at the repo root: Azul carbón palette, Cabinet Grotesk + General Sans + JetBrains Mono, graph grammar, light print theme, measured contrast. Preview: `docs/designs/assets/design-system/preview.html`.
