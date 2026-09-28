# Globe modes

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/globe_modes.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding mode list. MVP is a **subset**. Shipping all ten as v1 is a product failure.

The parent brief lists twenty chrome capabilities and ten modes. This file ranks them. **Commercial v1 is still email/PDF.** The globe’s first useful job is an **honest local instrument** (Willapa fixture), not a planetary arcade.

---

## 1. Recommended MVP (do this)

| ID | Mode | Why it is MVP | AOI |
|---|---|---|---|
| **M1** | Earth surface view | Geography, named water body, **bathymetry (not-for-navigation)**, coarsened cells | Willapa only |
| **M8** | Evidence / provenance view | Makes “why / trust / missing / observed–inferred–forecast” unavoidable | Same |
| **M9** | Uncertainty / data-gap view | Ignorance as a feature; default complementary toggle | Same |
| **Chrome** | Time readout | `issued_at` / `valid_for` / `inputs_through` / `last_obs` / confidence / model version / coverage | Always on |

**Fixture quality:** synthetic cells with mixed truth states. No OBIS/GBIF/AIS. No real leases. Banner: **NOT A LIVE ANIMAL MAP · FIXTURE DATA**.

**W1 later bind:** M1+M8+M9 clipped to Willapa, with Category D ops-stress on permissioned coarsened geography — still not a harvest map.

---

## 2. Later (specify now, do not build as v1)

| ID | Mode | Earliest honest home | Blockers if shipped early |
|---|---|---|---|
| **M2** | Semi-transparent ocean / subsurface | After a real depth-binned field exists | Fake blue volume implying fish in the column |
| **M3** | Vertical depth slice (curtain) | Pelagic cell; W1 may stub **emersion vs water** only | 50-layer implied animals |
| **M4** | Horizontal depth slice | Same as M3 | Empty bins interpolated |
| **M5** | Seafloor / habitat view | When benthic layers are licensed and coarsened | Spawning/nursery at capture grain |
| **M6** | Time-lapse forecast view | After append-only forecasts exist | Playback that looks like live tracking |
| **M7** | Side-by-side comparison | After two comparable issuances or layers | Pairing DOH closures with OSI as one score |
| **M10** | Ecosystem / food-web | Research, after relationship classes exist | Fake causality |
| **Story** | Story mode (`story_mode.md`) | Education / event recap | Mixing hypothesis with observation |
| **Volume** | Volumetric probability cloud | Scientist stack, GPU optional | CT-scan theater of UNKNOWN |
| **Climate** | Scenario / anomaly climate | Multi-year research | 72h product dressed as RCP |

---

## 3. Mode specifications

### MODE 1 — Earth surface view — **MVP**

**Purpose:** Locate the user in a **named** geography without pretending the ocean is a census.

**Shows:**

- Global or regional 3D/2D Earth (2D MapLibre fallback is acceptable for MVP).
- Land, coastline, **named** water body (Willapa Bay).
- Bathymetry / terrain as **physical context**, caption **not for navigation**.
- Coarsened analytical cells (H3 parent or equal-area analogue). Empty cells = `DATA_GAP` hatch, not white-as-zero.
- Official polygons **as context** (e.g. WA DOH growing-area outline) with caption *harvest geography, not biology*.
- Persistent banners and time readout.

**Does not show:** animal sprites, vessel tracks, farm performance, lease corners, species arcade.

**Selection in MVP:** AOI is **locked** to Willapa. Species search, taxon group, life-stage, climate comparison = **disabled, labeled later**.

---

### MODE 2 — Semi-transparent ocean / subsurface — **later**

**Purpose:** See that the ocean has **volume**, and that most of that volume is unobserved.

**Shows:** translucent water column; depth-bin occupancy of **evidence** (where samples exist); UNKNOWN hatch in unsampled z.

**Does not show:** a continuous biological cloud. If only surface SST exists, the column below is hatch, not a fade.

**W1 note:** oysters need **emersion vs immersion**, not a pretty subsurface globe. Prefer M3 stub over M2 for P0.

---

### MODE 3 — Vertical depth slice (curtain) — **later** (W1 stub allowed)

**Purpose:** A user-selected transect: environment and/or biological **index** vs depth vs along-track distance.

**W1 stub (allowed in MVP chrome as a panel, not a globe mode):**

```text
Y: emersion (air) | water (station, not bed)
X: hour
Layers: tide (observed/harmonic), air T (forecast), water T (station or UNKNOWN), OSI rank (forecast)
```

**Pelagic later:** bins from `volume_4d_spec.md`. Unobserved bins hatch. No interpolation down the column.

---

### MODE 4 — Horizontal depth slice — **later**

**Purpose:** One z-band at a time (0–10 m, 10–50 m, …, benthic, or species band).

**Rule:** switching slice must **not** carry color from another band. Depth-unknown observations do not appear in a numeric slice; they appear in an **unassigned-depth** overlay.

---

### MODE 5 — Seafloor / habitat view — **later**

**Purpose:** Bathymetry, slope, substrate, structured habitat (kelp, seagrass, coral **at published official grain**).

**Spawning / nursery:** only if `sensitive_display_rules.md` allows. Default **withhold**. Caption: habitat is not current presence.

---

### MODE 6 — Time-lapse forecast view — **later**

**Purpose:** Playback of **issued** forecast fields, not a live tracker.

**Rules:**

- Frame metadata always visible (`issued_at`, `valid_for`, model version).
- Speed capped; no eased interpolation that invents mid-frames biologically (`accessibility_and_trust.md`).
- Forecast frames use **dashed** encoding; observed stamps stay solid and **do not move**.

MVP substitute: **static** forecast window on the time readout, no playback.

---

### MODE 7 — Side-by-side comparison — **later**

**Purpose:** then vs now; now vs forecast; two layers; two model versions (replay).

**Allowed pairs:** env vs env; coverage vs coverage; issued forecast vs verifying observation **after** the window (labeled evaluation, not a rewrite).

**Forbidden pairs:** OSI-72 vs DOH open/closed as a merged score; SST vs “oysters”; AIS vs lobster.

MVP substitute: evidence panel lists drivers as numbers, not a split map.

---

### MODE 8 — Evidence / provenance view — **MVP**

**Purpose:** Click/tap a cell → Evidence Explorer (`evidence_explorer.md`, 16 fields).

**Shows:** truth state, quantity class, sources, licenses (or UNKNOWN license), as-of clocks, what-it-does-not-mean, privacy class.

**Default for MVP:** this mode can be a **persistent side panel** rather than a separate camera. Selecting M8 highlights provenance chips and opens the panel; the map stays M1.

---

### MODE 9 — Uncertainty / data-gap view — **MVP**

**Purpose:** The Unknown map (`unknown_map.md`). Coverage, recency, depth coverage, extrapolation, outages.

**Default:** available as a **toggle** that replaces biological/ops fills with hatch density. Recommended **on** for first-run fixture so users see ignorance first.

---

### MODE 10 — Ecosystem / food-web — **later**

See `ecological_network_view.md`. Graph + optional spatial join. Relationship class mandatory (observed / literature / inferred / speculative). No fake causality. Not in prototype.

---

## 4. Chrome capabilities (parent list of 20) — MVP vs later

| # | Capability | MVP | Notes |
|---|---|---|---|
| 1 | Global 3D Earth | Optional | 2D regional map is enough; globe camera later |
| 2 | Interactive ocean surface | **Yes** | Willapa water body |
| 3 | Bathymetry / seafloor terrain | **Yes** | Not-for-navigation |
| 4 | Vertical cross-sections | Stub | Emersion curtain panel |
| 5 | Depth slicing | Stub | Surface / intertidal / 0–10 m / unknown |
| 6 | Time slider + animated forecast | Readout only | No animation in MVP |
| 7 | Species selection/search | **No** | Locked *M. gigas* context / ops-stress; search later |
| 8 | Taxonomic group selection | **No** | |
| 9 | Life-stage selection | **No** | Grow-out implied; chip static |
| 10 | Observation-type selection | Filter stub | Direct vs remote vs gap |
| 11 | Evidence/confidence selection | **Yes** | Filter hatch vs solid |
| 12 | Environmental layer selection | **One** driver stub | Air or SST labeled correctly |
| 13 | Historical/current/forecast comparison | Panel text | Not split-screen |
| 14 | Climate anomaly comparison | **No** | |
| 15 | Region/polygon selection | Locked AOI | |
| 16 | Data provenance inspection | **Yes** | M8 |
| 17 | Model-explanation inspection | Drivers list | Full SHAP-like later; W1 = named inputs |
| 18 | Sensitive-location protection | **Yes** | No native leases; lock badge |
| 19 | LOD / performance | Sibling stack | Coarsen at zoom |
| 20 | Mobile and desktop fallback | **Yes** | 2D + static report path |

---

## 5. Mode switcher copy (implement)

```text
View
  (•) Earth + bathymetry
  ( ) Evidence panel          ← always available as panel
  ( ) Unknown / data-gap      ← toggle
  ( ) Subsurface              [later]
  ( ) Depth curtain           [later]
  ( ) Depth slice             [later]
  ( ) Seafloor habitat        [later]
  ( ) Forecast playback       [later]
  ( ) Compare                 [later]
  ( ) Food web                [later]
  ( ) Story                   [later]
```

Disabled modes stay **visible** so the product does not pretend they exist behind a mystery meat icon.

---

## 6. What “global” means in Mode 1

A camera that can look at the planet is allowed. A **global biological layer** is not v1 (`sensitive_location_policy.md` §12). Zooming out of Willapa in MVP shows **empty hatch + “no AOI loaded”**, not a world of interpolated life.
