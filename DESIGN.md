---
# gstack: design-md-format=spec
name: Cabos Sueltos
description: Papel carbón azul. A case file read at night; flat navy ink, paper text, and color only where you are looking or where the state put its stamp.
colors:
  background: "#0B1322"
  surface: "#111C30"
  surface-raised: "#182640"
  hairline: "#26375A"
  text: "#EFEBE0"
  text-secondary: "#AEB6C6"
  text-muted: "#9AA4B8"
  primary: "#EFEBE0"
  on-primary: "#0B1322"
  primary-hover: "#AEB6C6"
  accent: "#F5D547"
  on-accent: "#0B1322"
  accent-tint: "rgba(245,213,71,0.14)"
  sello: "#FF6B4A"
  graph-node: "#1A2842"
  graph-node-stroke: "#AEB6C6"
  graph-edge: "#7483A0"
  print-paper: "#FAF8F2"
  print-surface: "#FFFFFF"
  print-raised: "#F2EFE6"
  print-hairline: "#C9C5B8"
  print-ink: "#16181A"
  print-secondary: "#4A4C47"
  print-muted: "#5E5F59"
  print-marker: "#F6E27F"
  print-sello: "#B3301A"
  print-edge: "#3B3D3A"
typography:
  display:
    fontFamily: Cabinet Grotesk
    fontWeight: 800
    fontSize: 3rem
    lineHeight: 1.05
    letterSpacing: -0.01em
  headline:
    fontFamily: Cabinet Grotesk
    fontWeight: 800
    fontSize: 2.5rem
    lineHeight: 1.1
    letterSpacing: -0.01em
  title:
    fontFamily: Cabinet Grotesk
    fontWeight: 800
    fontSize: 1.75rem
    lineHeight: 1.15
    letterSpacing: -0.01em
  section:
    fontFamily: Cabinet Grotesk
    fontWeight: 800
    fontSize: 1.4375rem
    lineHeight: 1.2
  panel:
    fontFamily: Cabinet Grotesk
    fontWeight: 800
    fontSize: 1.1875rem
    lineHeight: 1.25
  body:
    fontFamily: General Sans
    fontWeight: 400
    fontSize: 1rem
    lineHeight: 1.5
  small:
    fontFamily: General Sans
    fontWeight: 400
    fontSize: 0.875rem
    lineHeight: 1.45
  label:
    fontFamily: Cabinet Grotesk
    fontWeight: 700
    fontSize: 0.75rem
    letterSpacing: 0.06em
  mono:
    fontFamily: JetBrains Mono
    fontWeight: 400
    fontSize: 0.875rem
    fontFeature: tnum
rounded:
  sm: 2px
  md: 4px
  lg: 12px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px
  3xl: 48px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: transparent
    textColor: "{colors.text}"
    borderColor: "{colors.hairline}"
    rounded: "{rounded.md}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.graph-node-stroke}"
    rounded: "{rounded.md}"
  chip:
    textColor: "{colors.text-secondary}"
    borderColor: "{colors.hairline}"
    rounded: "{rounded.full}"
  stamp:
    textColor: "{colors.sello}"
    borderColor: "{colors.sello}"
    rounded: "{rounded.sm}"
  link-official:
    textColor: "{colors.sello}"
  nav-link:
    textColor: "{colors.text}"
  entity-card:
    width: 280px
  evidence-drawer:
    backgroundColor: "{colors.surface}"
    width: 380px
  table-row:
    height: 44px
  table-row-mobile:
    height: 44px
  table-row-selected:
    backgroundColor: "{colors.accent-tint}"
  graph-edge-selected:
    strokeColor: "{colors.accent}"
---

# Cabos Sueltos

## Overview

**Creative North Star:** Papel carbón azul. The carbon copy of an official file, read at night: flat navy ink, paper-colored text, and only two hues, each with one meaning. This is what a product promising "every line has a receipt" looks like. It is a document you can defend, not a conspiracy board.

**Product context:** A public, open-source investigation site for Colombia. Search a name, NIT or cédula, open an entity page, and follow contracts, companies, legal representatives and approving officials from SECOP II and RUES (CC BY-SA 4.0). Audience: investigative journalists and anti-corruption activists, plus the editors and media lawyers who have to trust what gets published. Spanish (es-CO) only, i18n from the first commit. Peers: ICIJ Offshore Leaks, OpenSanctions, OpenCorporates, OCCRP Aleph, Arkham Intel (the original UX reference).

**Mode per surface:**
- Home: Persuade, lightly. A search poster, no feature sections.
- Entity page, graph, Conexiones table: Operate.
- Evidence drawer and Metodología: Read.
- PNG export: Read, in the light print theme.

**Visual reference:** `docs/designs/assets/design-system/preview.html` renders these tokens with the real fonts. The final renders are `final-*.png` in the same folder.

**Reference sites (researched 2026-09-25):** offshoreleaks.icij.org, opensanctions.org, opencorporates.com and rutasdelconflicto.com. intel.arkm.com blocked the headless browser.

**Key characteristics:**
- Navy ink surfaces with warm paper-white text; no grey-on-grey.
- Yellow appears only where the reader is looking.
- Vermilion appears only where an official record speaks.
- Every ID, code, amount and date is set in mono and can be copied exactly.
- Heavy poster-grotesque headings give long legal names weight.

## Colors

**Strategy: Restrained with semantic hues, on a Committed navy ground.** Navy owns the surfaces. The graph grammar already carries category (shape and line pattern, readable in grayscale), which leaves color free to carry provenance.

Each hue has exactly one job:
- **`accent` (highlighter yellow):** means "what you are looking at now". It is used for the selected edge, its end-node rings, the selected table row, focus rings and the breadcrumb's current step. Nothing else is yellow.
- **`sello` (vermilion):** means "an official record says this". It is used for "Ver registro oficial ↗", source stamps (SECOP II, RUES), license stamps and source codes that link out. Nothing else is vermilion, and it is never used for errors or warnings.
- **Blue** is only the ink of the paper. It is never used for links, categories or status.
- **Internal links** are paper-white (`text`) with a 1px underline.

**No success, warning or error hues.** The product never says "verificado" or "confirmado", so there is no green. Errors use `text` with an icon, a bold label and a hairline box. The "vínculo en revisión" state is a neutral chip with a dashed outline.

**Light or dark: dark.** Journalists work long research sessions on newsroom laptops, often at night, and the approved layout reference is dark. The PNG export is a separate light print theme (`print-*` tokens), because it lands in articles and on paper.

**Print theme:** paper `print-paper`, ink `print-ink`, `print-sello` for sources. The selected edge prints as a `print-ink` stroke over a 12px `print-marker` swipe, and the selected label gets a marker-swipe underline. It stays legible in black-and-white print.

**Measured contrast (WCAG 2.2 AA):**

| Pair | Ratio |
|---|---|
| `text` on `background` | 15.6:1 |
| `text-secondary` on `surface-raised` | 7.4:1 |
| `text-muted` on `surface-raised` | 6.0:1 |
| `accent` on `background` | 12.8:1 |
| `sello` on `surface` | 6.0:1 |
| `sello` on `surface-raised` | 5.4:1 |
| `graph-edge` on `background` (non-text, needs 3:1) | 4.9:1 |
| `print-ink` on `print-paper` | 15.9:1 |
| `print-sello` on `print-paper` | 5.9:1 |

Metadata never drops below 4.5:1.

**Depth in dark mode** comes from stepping surfaces (`background` → `surface` → `surface-raised`) and hairlines, not from inverting lightness or adding glow.

## Typography

The source world is the poster and the official record: a heavy grotesque for the voice, a neutral sans for reading, and a mono for everything that must be copied exactly. The register is Operate (dense UI) with Read islands (evidence, methodology).

**Cabinet Grotesk (700–800)** covers the wordmark, page and entity names, panel titles and uppercase labels. It is a poster grotesque: direct, heavy, and readable in screenshots. The wordmark "Cabos Sueltos" is set in Cabinet Grotesk 800, with no symbol for now.

**General Sans (400–600)** covers body, UI, the evidence summary and the "objeto" text. It stays neutral so headings and data carry the voice.

**JetBrains Mono (400/700)** covers every NIT, masked C.C., contract code (CO1.PCCNTR…), COP amount, date and source stamp, with tabular figures. **Ligatures must be off** (`font-variant-ligatures: none; font-feature-settings: "calt" 0, "liga" 0`), because with ligatures on, JetBrains Mono renders `***` as a ligature and a masked cédula must read exactly `C.C. ***7730`. Masked IDs never wrap (`white-space: nowrap`).

**Scale:**

| Size | Use |
|---|---|
| 48 | home headline |
| 40 | large entity name |
| 28 | entity header |
| 23 | section |
| 19 | panel title |
| 16 | body |
| 14 | table, controls, metadata |
| 12 | edge labels, stamps, legend (minimum) |

Heading levels differ by size, not just weight.

**Loading and licensing (hard rule):**
- Cabinet Grotesk and General Sans are Fontshare fonts under the ITF Free Font License. Self-hosting on our own servers is allowed. **Committing the font files to this public repo is forbidden** (the license bans redistribution through public repositories).
- A build step fetches the WOFF2 files from Fontshare into the build output, which is gitignored. The app serves them from its own origin with `font-display: swap`, preloading the 800 and 400 weights.
- Do not load fonts from the Fontshare CDN at runtime: that sends every visitor's IP address to a third party, which is wrong for a tool journalists use.
- JetBrains Mono is OFL. It can be self-hosted from `@fontsource/jetbrains-mono`.
- Fallback stacks: `"Cabinet Grotesk", "Arial Narrow", sans-serif`; `"General Sans", system-ui, sans-serif`; `"JetBrains Mono", ui-monospace, monospace`.

## Layout

**Desktop entity page (≥ 1280px, design review 16A):**
- Header strip: name, NIT, RUES status chip, then Copiar enlace, Descargar PNG and a "Solicitar corrección" text link.
- Three columns: **280px entity card**, a middle column, and a **380px evidence drawer**. The card and the drawer run the full height.
- The middle column holds the breadcrumb row (Deshacer, Volver al foco), the graph, and the **Conexiones table** under the graph, as in `docs/designs/assets/m1-entity-graph/m1-desktop-v2.png`.

**Tablet (768–1279px):**
- The card collapses into the header strip as inline counts.
- The graph and table stack full width.
- The drawer becomes a 380px overlay from the right on selection. It has a close button, Esc closes it, and focus returns to where it was.
- Wide tables scroll inside their own container, never the page.

**Mobile (< 768px):**
- Header: name, ID, status, Copiar enlace, PNG, a "⋯" menu, and a visible "Solicitar corrección".
- Card counts, including the finding line.
- Tabs: "Conexiones" first (44px rows grouped by kind), then "Grafo" (pan and zoom).
- Evidence opens as a bottom sheet.
- 16px side gutter, and no horizontal page scroll at 375px.

**Density:** 4px base, 8px rhythm, 24px between major regions, and 48px between home sections. Conexiones rows are 44px: the entity name sits over its ID so every column fits at 1440px. The main content max width is 1440px.

**Home:** a left-aligned search poster with the headline "Siga el vínculo hasta el registro.", one labeled search field, two example links, and a source statement with the data cut date. No feature grid, no hero image.

## Elevation & Depth

Elevation is flat. Depth comes from the three surface steps and 1px hairlines. The only shadow is the mobile bottom sheet (`0 -8px 24px rgba(0,0,0,.35)`), which has a real offset because it sits above the page. There is never a zero-offset glow or halo. The selected graph node gets a 2px `accent` ring offset about 5px from the node, not a blur.

## Shapes

Radii:
- `sm` (2px): stamps.
- `md` (4px): buttons, inputs, panels and record blocks.
- `lg` (12px): only the top corners of the mobile sheet.
- `full`: chips and the graph aggregate pill.

Nested radius equals the outer radius minus the gap. Panels are divided by hairlines; do not put cards inside cards.

**Graph grammar (from the design review, unchanged):**
- Node shapes: square = public agency, circle = company, diamond (rounded corners) = natural person, dashed pill = aggregate ("+2 entidades · tabla").
- Edges: contract = solid 1.25px `graph-edge`.
- Rep reported in SECOP = solid 3px `graph-node-stroke` with an arrow.
- Current rep per RUES = 10/6 long dash, 1.5px, with an arrow.
- Ordenador / supervisor = dotted, round caps, 1.5px, attached to the agency side.
- Edge labels are 12px General Sans with a 5px `background`-colored stroke behind them (`paint-order: stroke`), so they stay legible over lines.

## Components

- **Buttons:**
  - Primary (paper on navy): used only for Buscar.
  - Secondary: hairline outline, `surface-raised` on hover.
  - All buttons: 32px minimum height on desktop, 44px on touch.
  - Focus-visible: 2px `accent` outline, 2px offset.
  - Disabled: 50% opacity and `not-allowed` cursor, never hidden.
- **Search input:** a visible label ("Buscar por nombre, NIT o cédula"), never placeholder-only; 19px text; `graph-node-stroke` border.
- **Chips:** RUES status ("Activa · RUES, corte 01-09-2026") and "vínculo en revisión" (dashed). Neutral only.
- **Stamp:** uppercase mono 12px in `sello`, with a 1px `sello` border and 2px radius. It marks the source of a row or record: SECOP II, RUES, CC BY-SA 4.0.
- **Evidence drawer (receipt, "tirilla"):**
  - Title and summary sentence.
  - Record blocks separated by dashed hairlines; each block has "Registro N de M" plus a stamp.
  - The key/value list uses mono values. Labels are uppercase mono 12px in `text-muted`; the objeto and entity name use the body face. The value line is bold.
  - Each record ends with "Ver registro oficial ↗" (sello) and "Copiar cita" (secondary button).
  - A tear-off stub closes the drawer: a 2px dashed top edge on `surface-raised`, the source, license and cut date, and "Copiar cita" for the whole link.
  - No fake perforated edge graphic.
- **Conexiones table:**
  - Columns: Tipo de vínculo, Entidad (name over its mono ID, plus an inline "+ Expandir" link), Contratos, Millones COP, Fuente.
  - Money columns are headed "Millones COP" with plain es-CO numbers. Never abbreviate as "M", which reads as thousands in Colombian accounting.
  - Uppercase Cabinet labels; mono ID and number columns, right-aligned numbers.
  - The selected row gets an `accent-tint` fill plus a 3px inset `accent` bar on its first cell. This is the table twin of the highlighted edge, and only one row is ever selected.
- **States:**
  - Empty: says what was searched and what to try.
  - Loading: skeleton bars in `surface-raised`.
  - Error: an icon plus bold text plus Reintentar, with no hue.
  - Partial: "Mostrando 50 de 214 contratos", then "Cargar 50 más".
- **Graph:**
  - Flat at rest.
  - On selection, the edge turns `accent` at 3.5px with an accent arrowhead, both end nodes get rings, and the table row and drawer update together.

## Do's and Don'ts

**Do:**
- Keep yellow only on the current selection or focus, and vermilion only on official-source links and stamps.
- Set every ID, code, amount and date in JetBrains Mono, with ligatures off and no wrapping inside the ID.
- Carry node and edge kind by shape and line pattern; check every graph screen in grayscale.
- Label edges only with what the source record states ("rep. reportado en SECOP", "rep. vigente a <corte> (RUES)").
- Export PNGs in the print theme, with the source and license footer.

**Don't:**
- Glow, halo, neon or grid-paper backgrounds: the Arkham look this system departs from.
- Color-coding node types (the Linkurious, Maltego and Arkham habit), or blue links.
- Green "verified" badges or any success color. We show records, not verdicts.
- Vermilion for errors or warnings, since red already means "the state said this".
- Committing Fontshare font files, or loading them from a third-party CDN at runtime.

## Motion

- **Approach:** minimal-functional. `prefers-reduced-motion` disables everything except instant state changes.
- **Easing:** enter ease-out, exit ease-in, move ease-in-out.
- **Duration:**
  - micro 80ms (hover)
  - short 150–200ms (drawer, sheet, row highlight)
  - medium 250ms (graph expand/collapse layout)
  - Nothing is longer.
- **The one authored moment:** selecting a connection sweeps the highlighter along the edge (a stroke-dashoffset draw of about 200ms, ease-out) while its table row and receipt light up in the same frame.

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-25 | Initial design system created | /design-consultation. Product context from the approved design doc and the /plan-design-review decisions; research on ICIJ, OpenSanctions, OpenCorporates and Rutas del Conflicto; independent proposals from Codex (gpt-6-sol) and a Claude subagent |
| 2026-09-25 | Product name: Cabos Sueltos (`cabosueltos`) | `follow-the-money` clashes with the FtM library; `cabosueltos` was free on PyPI, GitHub, .co and .com.co |
| 2026-09-25 | Memorable thing: "Every line has a receipt" | Every design choice must make provenance visible |
| 2026-09-25 | Type: Cabinet Grotesk, General Sans, JetBrains Mono ("Cartel") | User rejected Archivo condensed + Atkinson Hyperlegible as boring; picked Cartel from four rendered directions |
| 2026-09-25 | Palette: Azul carbón (navy ink) | User found the grey carbon palette boring; picked navy from three renders. Yellow on navy gives the strongest selection contrast, and blue, yellow and red echo Colombia without a flag |
| 2026-09-25 | Two-color provenance semantics, receipt-style drawer | User-selected risks: color means "you selected it" or "an official record says it", never a category |
| 2026-09-25 | "Glow only on selection" becomes a flat highlighter stroke with an offset ring | Refines the design-review decision (12A): selection stays the only emphasis, without the zero-offset glow |
| 2026-09-25 | Layout corrected to design review 16A breakpoints (1280/768) and the approved mockup (table under the graph) | The first DESIGN.md draft had 1100/600 and a full-width table, which contradicted approved decisions |
| 2026-09-25 | Conexiones rows 44px with the ID under the name; value column "Millones COP" | /design-html entity page: fits all columns at 1440px; "M" is ambiguous in es-CO |
| 2026-09-25 | Fontshare fonts are fetched at build time, never committed | ITF Free Font License forbids redistribution through public repos; self-hosting is allowed |
