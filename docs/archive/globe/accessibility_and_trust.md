# Accessibility and trust

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/accessibility_and_trust.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding for MVP and later. Color-only encodings fail review.

The visual language must **not** rely only on color. Trust is a UX property: no deceptive smoothing, no misleading animation speed, no hidden interpolation.

---

## 1. Color vision

- Palettes: **Okabe–Ito** + limited ColorBrewer sequential families assigned in `visual_truth_states.md`.  
- Never encode presence vs absence, or stress vs safe, as **red vs green**.  
- W1: Typical = gray, Elevated = amber, High = **red outline on white**, Cannot-issue = black/white hatch. Green is **not** used for “OK to harvest.”  
- Contrast: WCAG 2.2 AA for text and chips; hatch remains visible at 200% zoom.  
- Offer a **pattern-heavy** theme (textures only, near-grayscale fills).

---

## 2. Texture and shape (required channels)

| Meaning | Non-color channel |
|---|---|
| Observed | Solid stamp / solid line |
| Inferred | Dotted outline |
| Forecast | Dashed + clock icon |
| Unknown / gap | Diagonal hatch |
| Restricted | Lock + large pixels |
| eDNA | Stipple |
| Acoustic | Wave hatch |
| Extrapolation | Edge ticks |

If two layers differ only by hue, fail QA.

---

## 3. Labels and units

- Every legend has **units** and **quantity class** in the title.  
- Depth in meters positive down, plus bin name.  
- Clocks: UTC and local.  
- “Not for navigation” on bathymetry.  
- No naked color bar.

---

## 4. Screen readers

Core results expose a text alternative (not a color name):

```text
Willapa coarsened cell. Category D operational stress forecast: Elevated.
Confidence Low. Depth: emersion and surface water. Not food-safety.
Not harvest authorization. Last on-lease direct observation: none.
Data coverage: low. Fixture data. Not a live animal map.
```

Mode, truth state, confidence, valid window, and does-not-mean list are in the accessibility tree. Decorative bathymetry is marked decorative **only if** the not-for-navigation notice is still read once per session.

---

## 5. Tables and printable reports

- **Export table** of visible cells: id, quantity, units, truth state, confidence, depth, times, publish class.  
- **Printable** 1-page report aligned with commercial PDF contract (`user_output_contract_visual.md`).  
- Globe is optional; table + PDF must stand alone (low-vision, no-WebGL, operator on a boat wifi).

---

## 6. Low-bandwidth and fallback

| Mode | Behavior |
|---|---|
| Low-bandwidth | No 3D; no playback; coverage + chips + table |
| Static image / report | Issued PNG/PDF of **this** `brief_id` |
| No GPU / no WebGL | 2D MapLibre or even image tiles + panel |
| Transparent methodology | Link to rule/model version and prediction contract |

Do not load raw observations into the browser (sibling tile design).

---

## 7. No deceptive smoothing or animation

| Practice | Rule |
|---|---|
| Kernel density of a few points into a “hotspot” | **Forbidden** unless the quantity is explicitly a density of **records** with effort caption |
| Smooth interpolation over UNKNOWN | **Forbidden** |
| Spline through empty depth bins | **Forbidden** |
| Eased animation inventing mid-times | **Forbidden** |
| Animation speed implying live chase | **Forbidden**; label time ratio |
| Glow / bloom / fish sprites | **Forbidden** |
| Hidden climatology fill | **Forbidden** without toggle + banner |
| Random jitter of points “for privacy” | **Forbidden** (reversible; use grids) |

Progressive refinement of **tiles** is allowed if coarser tiles are **parent aggregations** with preserved UNKNOWN, not guesses.

---

## 8. Trust copy (always-on banner)

```text
NOT A LIVE ANIMAL MAP
Estimates are evidence-typed. UNKNOWN is a valid result.
Commercial harvest/food-safety decisions stay with official authorities.
```

Fixture builds add: `FIXTURE / SYNTHETIC CELLS · NO INGEST`.

---

## 9. Motion and vestibular

Respect `prefers-reduced-motion`: no playback autoplay, no pulsing corridors. Forecast remains dashed and static.
