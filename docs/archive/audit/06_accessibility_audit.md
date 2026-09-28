# Accessibility audit

**Live DOM:** 2026-09-19, `http://localhost:5173/`, 1440×900.  
**Spec:** `globe/accessibility_and_trust.md`. **CSS:** `globe/prototype/src/styles.css`.

This is not a full WCAG certification. It is what a keyboard user, screen-reader user, and color-blind user would hit **on this page**.

---

## 1. What is already in place (keep)

| Feature | Where | Note |
|---|---|---|
| `html lang="en"` | `index.html` | OK |
| Skip link | `a.skip` → `#evidence` | Visible on focus; `transform` so it doesn’t grow the scrollport |
| `role="status"` on banner | `header.banner` | Disclaimer is in the accessibility tree |
| Fieldsets + visually-hidden legends | Mode, depth, overlays | Radios are labeled |
| Unknown map checkbox label | “Show ignorance as the feature” | Labeled, but jargon |
| `aria-label` on rail, legend, timebar, map | `index.html` | Map: “Willapa Bay coarsened fixture cells” |
| Evidence honesty `aria-label="Honesty questions"` | `evidence.ts` | Good region |
| OPS `aria-label="W1 oyster operational stress example"` | `evidence.ts` | Jargon in the accessible name |
| `aria-live="polite"` on selection | `#map-status` | Updates on cell change |
| `prefers-reduced-motion` | `styles.css` | Kills animation/transition (map has little animation) |
| Pattern + color | `patterns.ts`, `.swatch` | Not color-only for truth states |
| Keyboard cell list | `#cell-select` | Exists — **below the fold** |
| Contrast (sampled) | Banner 15.4:1; body text on panel 7.26:1; timebar 12.8:1 | **AA pass** for those pairs |
| Evidence `tabindex="-1"` | `#evidence` | Skip-link target can focus |

---

## 2. Failures against the spec and against WCAG-ish use

### 2.1 No `h1`

Headings start at **h2** (AOI, Globe mode, Evidence explorer…). Document name is only `<title>`. Landmark outline is a list of lab section titles. Spec example SR string in `accessibility_and_trust.md` §4 is a **composed sentence**; the live page never exposes that sentence as a heading.

### 2.2 Map `role="application"`

`#map` is `role="application"` (`index.html`). That tells AT to hand keys to the map. There is **no documented keyboard map** besides MapLibre’s own (poorly advertised) and the off-fold `<select>`. Users can tab to Zoom in/out/compass. They cannot arrow between cells. **Click-only biology.**

VERIFICATION.md: canvas clicks miss. Combined with `application`, SR users get a live region update only **after** a selection they may not be able to make.

### 2.3 Live region is visually clipped and jargon-filled

`#map-status` uses `.sr-live { clip: rect(0 0 0 0) }`. Text:

> Selected WILLAPA-C17, FORECAST, confidence low. Depth band in view: Surface (water skin). Not a live animal map.

Accessible alternative is **still** cell IDs and enums. Spec §4 wanted: “Category D operational stress forecast: Elevated. Confidence Low. Depth: emersion… Not food-safety…” — not implemented as a composed SR string. C17 ops flags are visual; SR gets FORECAST + low.

### 2.4 Skip link skips the wrong thing

Skip to **evidence explorer** (C17 wall of Category D). There is no skip to a search field. First focusable after skip is deep in the ops/JSON/links depending on tab order through the panel.

### 2.5 Combobox accessible name is a dump

Snapshot name:

> Select a coarsened cell Select a coarsened cell WILLAPA-C01 · DIRECT_OBSERVATION …

The visually-hidden span plus the options concatenate. 28 options of `WILLAPA-Cxx · ENUM`. Unusable as a species list; barely usable as geography.

### 2.6 Legend not in the first screen, not a live `img` alternative

Legend is in the left rail **below the fold**. Map canvas has **no** `aria-describedby` pointing at `#legend`. Color-blind users who need the pattern **key** must find and scroll the rail. Swatch `<i aria-hidden="true">` is correct (text is beside it) **if** they get there.

### 2.7 Text in the canvas

`cell-ids` and density `n=` are **drawn text** (`symbol` layers). They are not in the accessibility tree. Zoom/compass buttons are. The actual content of the map is not.

Stations in Mode 8: circles only, no SR names (`FIXTURE-STATION-TOKE` lives in GeoJSON, not in UI).

### 2.8 Contrast / size leftovers

- Timebar labels `.k` are **0.65rem** (~10px) uppercase. Contrast is OK; **size** fails comfortable reading (and likely WCAG 1.4.4 usability at 200% because seven columns + ISO strings wrap into sludge — already wrapping at 1440).
- Map stamp 0.72rem over the map.
- `.fields h3` 0.72rem uppercase — 16 of them.
- Focus: radios use native focus; `.copy-json` has no custom `:focus` ring beyond browser default. `--focus: #005f73` is unused on controls.

### 2.9 Motion / gestures

- `cooperativeGestures: true` — overlay “Use ⌘ + scroll to zoom.” Pointer-events none (VERIFICATION). Fine for trackpads; **bad** for some assistive zoom.
- Compass **rotate** on a 2D bay increases orientation cost for vestibular / cognitive load. Spec forbids deceptive animation; rotate is still extra motion.

### 2.10 Density / cognitive a11y

896 words in the evidence panel, 305 in the rail, 69 in the timebar, 34 in the banner — **~1300+ words** on one “screenful” of product, most of it **not** the 30s answers. This is a **cognitive accessibility** fail (POUR: understandable). Founder feedback is this.

C17 ops block 1181px pushes the four required questions (`evidence_explorer.md`) out of the viewport — also an a11y fail: the “text alternative” is below the fold.

### 2.11 Missing spec features

| Spec (`accessibility_and_trust.md`) | Prototype |
|---|---|
| Pattern-heavy near-grayscale theme | Not offered |
| Export table of visible cells | Only “Copy cell JSON” per cell |
| Printable 1-page report | No |
| Low-bandwidth / no-WebGL image fallback | No (WebGL canvas required) |
| Composed SR result sentence | Partial live region, jargon |
| Units in every legend title | Legend is truth-states; SST units only when overlay on and user scrolled to legend |

### 2.12 Links

WA DOH / NOAA links open in the same tab (`target` not set; `rel="noopener"` only). OK-ish. Link text is good (“WA DOH Commercial Shellfish Map Viewer”) — then license paragraph still says “not ingested.”

### 2.13 Reduced motion vs forecast dash

Dashed forecast is static — good. No playback Mode 6 — good.

---

## 3. Keyboard path (as tested in structure)

Tab order roughly: skip → mode radios → unknown checkbox → depth radios → overlay checkboxes → **(must tab through all of those)** → cell select (off-fold) → map zoom/compass/attrib → (evidence links/JSON if selected).

There is **no** shortcut to the cell list. A keyboard user spends many tabs on Mode 1/8/9 and unused later-mode **text** (not tabbable, but visually in the way). Overlays are tab stops before the one control that changes the story.

---

## 4. Mobile / zoom

`@media (max-width: 1100px)` stacks: rail, 50vh map, evidence; timebar 2×2-ish. Banner stacks to one column. **No** 44px tap targets specified; radios are native. Evidence 3802px scroll on a phone is a wall. `user_output_contract_visual.md` “does-not-mean strip stays sticky” — **not implemented**.

200% zoom: three-column `.shell` `minmax(16rem,20rem) 1fr minmax(20rem,26rem)` will collapse via the 1100px breakpoint only if the **viewport CSS pixels** shrink; browser zoom on 1440 may keep three panes and clip. Not verified as passing 1.4.10 Reflow.

---

## 5. P0 a11y for this product

A11y is not the first P0 (the missing species job is), but these block **any** user including AT:

1. Map content not in the accessibility tree except a jargon live region.
2. Default “answer” (why/trust/class) not on screen.
3. Combobox of enums as the only non-pointer selection.
4. Cognitive overload (jargon + 16 fields) — WCAG 3.1 Readable.

Fix together with the redesign: **one composed answer** in the DOM (not only in a clipped live region), search as first heading/control, Expert Mode for JSON/16 fields, legend visible or `aria-describedby`, map not `application` unless cell keyboard nav exists.
