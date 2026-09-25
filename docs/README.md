# Docs

Planning and design records for Cabos Sueltos (working repo name `follow-the-money`). The root [`DESIGN.md`](../DESIGN.md) is the design system every UI change must follow. Superseded mockups and option boards live only in `~/.gstack/projects/follow-the-money/designs/`.

## Design

- [`designs/follow-the-money.md`](designs/follow-the-money.md) is the product design doc: written at /office-hours and amended with every approved decision from the reviews below (R1-R45). It also holds the second eng review's ledger and report at the end.
- [`designs/assets/m1-entity-graph/entity-page.html`](designs/assets/m1-entity-graph/entity-page.html) is the **visual and interaction reference for the entity page** (eng T9), produced by /design-html. The production graph is built on Cytoscape.js, not ported from this file (eng review 2, R31). It is one self-contained file with every interaction working: selection sync, expand, undo, filter, citations, URL state, tablet overlay, mobile sheet and the PNG print preview. The data in it is fictional.
- `designs/assets/m1-entity-graph/m1-desktop-v2.png` and `m1-mobile-v2.png` are the layout mockups the page was built from. The colors in them are superseded by `DESIGN.md`.
- [`designs/assets/design-system/preview.html`](designs/assets/design-system/preview.html) is the live token reference: real fonts, exact colors, and a toggle for the print theme. `final-full.png` is a static render of it.
- `designs/assets/follow-the-money-mockup-variant-B.png` is the original office-hours mockup that the design doc embeds.

The previews load Cabinet Grotesk and General Sans from the Fontshare CDN because it is a design reference only. The app itself must not do this; see Typography in `DESIGN.md`.

## Reviews

- [`reviews/eng-review-2026-09-25.md`](reviews/eng-review-2026-09-25.md) is the first /plan-eng-review report: M1 locked, decisions R1–R24. The second eng review (R25–R45) lives at the end of the design doc; its test plan is [`reviews/eng-review-2-test-plan-2026-09-25.md`](reviews/eng-review-2-test-plan-2026-09-25.md).
- [`reviews/eng-review-test-plan-2026-09-25.md`](reviews/eng-review-test-plan-2026-09-25.md) is the test plan from that review.
- [`reviews/design-review-2026-09-25.md`](reviews/design-review-2026-09-25.md) is the /plan-design-review report: 7 passes, 23 decisions.
- `reviews/tasks-*.jsonl` are the implementation task lists from each review.

## Order of authority

1. `DESIGN.md` for anything visual.
2. `designs/follow-the-money.md` for everything else: it now carries every approved decision.
3. The review reports, as the history and reasoning behind those decisions.

Every file here has a matching copy in `~/.gstack/projects/follow-the-money/` (the design doc as `tru-master-design-20260925-050150.md`, with absolute image paths). Update both together.
