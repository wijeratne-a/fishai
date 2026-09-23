# 4D volume specification

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/volume_4d_spec.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Visual contract for depth-aware views. No global volume is computed. Volumetric cloud = **later**.

---

## 1. The mathematical object (long-term)

When a species × life-stage × AOI has enough evidence, the observatory may estimate:

```text
P(present | longitude, latitude, depth, time, environmental state)
```

or another **named** state variable (occupancy, relative index, CPUE rank, ops-stress rank) with the same coordinates.

**Honesty constraints:**

- This is a **belief**, not a census and not a tracker.
- If any of lon, lat, depth, time, env, or the observation operator is missing, **do not** fill a pretty volume.
- Ceiling: prediction-contract category A–E cannot exceed the strongest evidence on that output.
- Most taxa remain T0–T2: **no** current 4D posterior. Show range/suitability/UNKNOWN instead.

**W1 / P0 does not use P(oyster present).** Farm oysters are planted. Estimate **operational stress / workability** on `INTERTIDAL_AIR` + `SURFACE_0_5` only (`../observatory/global_digital_twin_architecture.md` §4).

---

## 2. Depth status (mandatory chip)

Every biological or operational field carries exactly one:

| `depth_status` | Meaning | Visual |
|---|---|---|
| `known_band` | Assigned to a registry bin or species band | Chip: bin id + meters (positive down) |
| `surface_skin` | Valid at skin / first optical depth only | Chip: `SURFACE SKIN — not the column` |
| `seafloor` | Bottom-contact / benthic | Chip: `BOTTOM_CONTACT` + bathymetry source |
| `intertidal_air` | Emersed | Chip: `EMERSION` (not an ocean z) |
| `unknown` | No usable z | **Hatch on the z widget**; no volume fill; confidence cannot be High |
| `integrated` | Collapsed over a stated band because data cannot resolve z | Chip: `DEPTH-INTEGRATED over {band} — not a depth claim` |

**Distinguish in copy (required):**

| User might think | Honest sentence |
|---|---|
| “Likely near this lat/lon” | Surface projection of a **named** band or integrated field |
| “Likely at this depth” | Slice/curtain with `known_band` |
| “Likely near the seafloor” | `BOTTOM_CONTACT` only |
| “We don’t know how deep” | `depth_status=unknown` |
| “This map summed the column” | `depth_status=integrated` |

Never fade a surface field down a fake gradient to look 3D.

---

## 3. Depth-bin registry (display names)

Align with architecture bins. UI labels:

| `depth_bin_id` | UI label | MVP Willapa |
|---|---|---|
| `INTERTIDAL_AIR` | Emersion (air exposure) | **Yes** |
| `SURFACE_0_5` | 0–5 m / surface water | **Yes** (station, not bed) |
| `UPPER_5_25` | 5–25 m | Later |
| `SHELF_25_100` | 25–100 m | Later |
| `SHELF_100_200` | 100–200 m | Later |
| `MESO_200_500` | 200–500 m | Later |
| `MESO_500_1000` | 500–1,000 m | Later |
| `BATHY_1000_4000` | 1,000–4,000 m | Catalog |
| `ABYSS_4000_PLUS` | ≥4,000 m | Catalog |
| `BOTTOM_CONTACT` | Seafloor − 20 m to seafloor | Later (lobster-class) |
| `MIXED_LAYER` | 0–MLD(t) | Later, derived |
| `THERMAL_BAND:{lo}_{hi}C` | Thermal habitat {lo}–{hi} °C | Later; **habitat volume, not count** |
| `UNASSIGNED` | Depth unknown | **Yes** (control stub) |

Parent brief slices (0–10, 10–50, 50–200, 200–1,000, 1,000+) may be **aliases** of unions of bins. Do not interpolate empty members of a union.

**Do not interpolate empty bins to make a continuous profile.**

---

## 4. Seven visual operations

### 4.1 Surface projection — **MVP**

A 2D map of either:

- a **selected** depth band, or
- a **declared** integrated band.

Legend must include `depth_status`. Default Willapa: show **emersion ops-stress** and/or **surface env**, never a column-integrated “oyster probability.”

### 4.2 Depth curtain — **later** (W1 panel stub)

Vertical section along a transect.

| Axis | Pelagic | W1 stub |
|---|---|---|
| Horizontal | Distance along transect | Hour (tide clock) |
| Vertical | Depth (m down) | Emersion vs water |
| Fill | Truth-stated field | Tide / air / water / OSI |

Unobserved z = hatch. SST may only paint the **top** row, labeled skin.

### 4.3 Depth slice — **later** (control stub in MVP)

Horizontal slice at one band. MVP control:

```text
Depth: (•) Emersion  ( ) Surface 0–10 m  ( ) Unknown depth  ( ) Integrated [disabled]
```

Unknown-depth observations are **not** placed on 0–10 m.

### 4.4 Volumetric cloud — **later** (scientist stack)

Semi-transparent 3D probability volume.

**Ship rules if ever built:**

- Opacity encodes **confidence × data support**, not “more fish.”
- UNKNOWN voxels are hatch or omitted, never climatology smoke.
- Not in commercial MVP. Not in globe fixture prototype.
- Cesium/globe ≠ CT scanner; sibling stack may use a 2D plot instead of GPU volume for a long time.

### 4.5 Depth distribution curve — **later** (panel stub ok)

At a clicked cell: relative index or occurrence *p* **by bin**, with n and method.

W1 stub:

```text
Emersion window: FORECAST air × tide
Water @ station 3.2 km: REMOTE/IN SITU supporting only
On-lease bag microclimate: UNKNOWN
Column below 5 m: not in target
```

### 4.6 Time–depth animation (DVM) — **later**

Show vertical migration across hours.

Rules: `biological_variables_visual.md`. Solid stamps for observations; dashed inferred DVM. Do not animate a sinusoidal fish icon as if every individual migrates. Uncertainty = vertical envelope, not a single depth line.

**Not MVP.** Willapa oysters do not DVM.

### 4.7 Split confidence: xy vs z

The panel always separates:

| Confidence | Question |
|---|---|
| Horizontal | Is the **cell** the right place? |
| Vertical | Is the **depth band** identified? |
| Temporal | Is the **window** identified? |

High xy + unknown z → **overall cannot be High** for a depth-specific claim. Surface-only products (SST skin) must not inherit High for subsurface biology.

---

## 5. What each view is allowed to claim

| View | Allowed claim shape | Forbidden |
|---|---|---|
| Surface, selected band | Rank or *p* **in that band** | “Fish are here” with no z |
| Surface, integrated | Rank or *p* **integrated over {band}** | Looking like a single depth |
| Curtain | Structure along transect | Filling gaps between stations with animals |
| Slice | Structure at z | Showing unassigned-depth points |
| Volume | Scientist posterior | Public life cloud |
| Depth curve | 1D profile with n | Smooth spline through empty bins |
| DVM animation | Time–depth **index** | Live tracking |

---

## 6. Environmental state in the conditioner

`P(· | env)` does not license painting env as biology.

| Env shown | Vertical validity |
|---|---|
| IR SST | Micrometres–skin |
| Microwave SST | Near-surface, still not bottom |
| Ocean color | First optical depth (often **<1–10 m** in Willapa-class water) |
| Air temperature | Emersion / meteorology |
| Tide / elevation | Emersion clock |
| Bottom T | Only if a bottom product or sensor exists |
| 3D model T/S/u/v | Model-inferred; dashed; named model/version |

Animating SST with a species field is **Mode 7 later**, and the species field keeps its own truth state.

---

## 7. MVP implementation (Willapa fixture)

Build:

1. Surface map of coarsened cells.
2. Depth control stub (emersion / surface / unknown).
3. Optional 2D emersion curtain in the evidence panel.
4. Copy when user picks “integrated”: *Disabled — no depth-integrated biological field in this AOI.*

Do **not** build a 3D oyster cloud. Planted bags are not a probability volume.
