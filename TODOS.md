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
