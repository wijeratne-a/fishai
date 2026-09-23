# Disagreement map spec

**Date:** 2026-09-18  
**Status:** Visual contract for contestability. **No tiles shipped. No live data.**  
**Audience:** later globe / evidence UI. **This file does not write `globe/`** (that tree is in flight). When the globe agent lands encodings, map the tables in §5 onto `globe/visual_truth_states.md` rather than inventing a second palette.

**Law:** never one red scale titled fish, oysters, life, hotspot, or abundance. Disagreement is **not** presence.

---

## 1. What a disagreement map is allowed to show

A disagreement map answers: **do the v0 members agree on the OSI-72 band for this coarsened cell, and why not?**

It is a **meta-layer** over member forecasts. It does not replace:

- the Unknown / data-gap coverage map  
- the W1 ordinal stress chips (Typical / Elevated / High / Cannot issue)  
- official DOH growing-area **context outlines**

**W1 public grain:** WA DOH growing area or larger bay unit. Not bed, raft, or lease polygon. Not H3-8 as a public product cell if that grain can invert a lease (`privacy` policies). Internal PRIVATE UI may use farm-zone **for that partner only**.

**Forbidden on any public disagreement map:**

- Farm mortality, yield, growth, disease, or workability outcomes  
- Another farm’s High chip  
- Aggregations that fail a rule-of-3 (or that isolate one producer by toggling filters)  
- Red flood = “oysters dying” or “fish here”  
- Smooth interpolation across `cannot_issue` cells  
- Habitat suitability or CPUE on the same legend

---

## 2. Two layers, two legends (never merged)

### Layer A — Member OSI-72 (already specified elsewhere)

Use the **W1 ordinal encoding**, not a biological presence table:

| Chip | Visual intent (from globe §6; implement later there) | Means |
|---|---|---|
| Typical | Gray fill, solid | Mid tercile of comparison set |
| Elevated | Amber fill | Upper tercile indicator |
| High | **Red outline** on white — not a red flood | Extreme of comparison set |
| Cannot issue | Black/white hatch | UNKNOWN / None |

Always-visible: `NOT FOOD-SAFETY · NOT HARVEST AUTHORIZATION`.

If both members are shown on a map, **do not** pick one color for the cell. Use Layer B or a split fill.

### Layer B — Agreement state (this spec)

| State | Texture (mandatory, not color-only) | Fill note | Legend title |
|---|---|---|---|
| `AGREE` | Solid, muted | Neutral slate; **not** green-for-go | `Baselines agree · OSI-72 band in panel` |
| `DISAGREE` | **Split fill** (diagonal bisection) or side-by-side hatch of the two member chips | No average color | `Baselines disagree · not an average` |
| `DATA_GAP` | Wide diagonal hatch (coverage language) | No estimate fill | `Missing member input or logs · not absence` |
| `INCOMPARABLE` | Blocked-candidate chip, not a cell fill | — | `Different quantity · not in this ensemble` |
| `OOD` | Magenta **edge ticks** (modifier) | Stacks on AGREE or DISAGREE | `Extrapolated · members may be jointly wrong` |

**Disputed modifier (globe already named):** two-state split fill + “sources disagree.” This layer **is** that modifier for `ENS-W1-OSI72-v0`. Do not also paint a sequential “disagreement heat” in red.

---

## 3. Cell interaction (required)

Click/tap/focus of a cell (or a row in the email/PDF, which is the commercial primary surface) opens **all** of:

1. Each member’s band + one-line mechanism (`B4: air×daytime emersion`; `B12: month×area rate`).  
2. Why-code(s) from [`disagreement_taxonomy.md`](disagreement_taxonomy.md).  
3. Missing inputs.  
4. OOD dimensions if any.  
5. Publish class.  
6. `does_not_mean`.  
7. Whether a planner ticket would fire (internal) — **not** a public “go sample this lease” pin.

Commercial v1 remains email/PDF. A map is **not** required to ship W1. If a map exists, it must obey this spec.

---

## 4. Anti-patterns (design-review fail)

| Anti-pattern | Why it fails |
|---|---|
| RdYlGn of \(D\) titled “risk” or “life” | Collapses disagreement into a go-fish / die-oyster scale |
| Mean band as the **only** fill, members in a tooltip | Hides contestability; ship block per `ensemble_math.md` §5 |
| Green agree next to DOH “Approved” | Food-safety contamination |
| Kriging \(D\) between growing areas | Manufactured smoothness |
| Public choropleth of “farms where B4≠B12” at lease grain | Performance leakage |
| Same teal as habitat suitability | Quantity-class mix |
| Animation of split fills that looks like a bloom | Deceptive motion |
| Candidate `MC-HAB` underlay “to add context” in the OSI legend | Incomparable |

---

## 5. Hook to globe truth states (do not edit globe here)

When `globe/visual_truth_states.md` is the renderer:

| Ensemble object | Globe `truth_state` / modifier |
|---|---|
| B4 or B12 OSI-72 issuance | `FORECAST` + quantity `operational_stress_indicator` (not presence) |
| Missing logs / cannot_issue | `UNKNOWN` and/or `DATA_GAP` |
| Split members | Modifier **Disputed** (“do not average secretly”) |
| Coarsened public geometry | `RESTRICTED_OR_COARSENED` badge |
| Habitat candidate (not a member) | `HABITAT_SUITABILITY` on a **separate** mode/legend, or omit |
| Partner outcome (PRIVATE) | `OPERATIONAL_CATCH_OR_EFFORT` analogue — farm log; never public |

Globe MVP modes that could later host Layer B: Evidence explorer + Unknown map — **not** Mode 10 food-web, not a volumetric oyster cloud.

---

## 6. Email/PDF substitute (W1 primary)

If there is no map, the “disagreement map” is a **three-row table**:

```text
Climatology (B12)     Typical | Elevated | High | Cannot issue
Expert-rule (B4)      Typical | Elevated | High | Cannot issue
Farm-manager (B5)     {logged band | not logged — DATA_GAP}
Agreement             AGREE | DISAGREE (codes) | DATA_GAP
```

Never a single traffic light. Never a 0–100 ensemble score.

---

## 7. Accessibility

Split fills must remain legible without hue: diagonal bisection + labels “B4” / “B12” in the panel, not only vermillion vs gray. High stress remains **outline**, not flood, so it does not collide with disagreement hatching.
