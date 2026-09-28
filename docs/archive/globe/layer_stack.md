# Layer stack

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/layer_stack.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Catalog of layer **groups**. MVP enables a tiny subset. Fusion does not change truth state.

Users overlay drivers. **SST, chlorophyll, and vessel density never become abundance** by sharing a canvas with a biological layer.

---

## 1. Interaction rules (all groups)

| Action | Rule |
|---|---|
| Toggle | Each layer keeps its own legend, units, truth state, depth validity. |
| Opacity | Does not mix legends; 0% is off. |
| Split / compare | Mode 7 later; MVP = inspect numbers, not a swipe that blends OSI with DOH. |
| Inspect cell | Numeric values + units + as-of + source in Evidence Explorer. |
| Animate driver with species field | Later; species field stays dashed/dotted; env stays env. |
| “What influences the model here?” | Named **inputs** list. No unvalidated SHAP theater. W1: air × emersion, wind/wave; water T/DO/S supporting. Phrase as inputs, not “caused by SST.” |

**Stacking ceiling:** the **displayed biological claim** cannot exceed the strongest biological evidence. A stack of `REMOTE_DETECTION` SST under a suitability layer is still suitability (T2), not presence.

**Z-order (back → front):**

1. Earth / bathymetry (not-for-navigation)
2. Physical ocean
3. BGC
4. Habitat structure
5. Official context outlines (MPA, DOH growing area — labeled)
6. Biological / operational **estimate** (if any)
7. Observation stamps (solid)
8. UNKNOWN / DATA_GAP hatch (must remain visible; do not bury)
9. Restricted/coarsened lock badges
10. Chrome (banners, readout)

Hatch is **not** allowed to be covered by a pretty fill.

---

## 2. Group A — Physical ocean

| Layer | Typical truth | Vertical validity | MVP Willapa |
|---|---|---|---|
| Sea-surface temperature | `REMOTE_DETECTION` or model analysis | **Skin / near-surface** | Stub optional; **never** body T or oysters |
| Depth-resolved temperature | Model or profiles | Named bins | Later |
| Salinity | In situ / model | Sensor or model depth | Supporting if station exists |
| Currents | Model / HF radar | Surface unless 3D model | Later |
| Eddies / fronts | Derived | Surface | Later |
| Upwelling index | Derived / official | Regional | Later / Chinook context |
| Sea-surface height | Remote | Geostrophic context | Later |
| Mixed-layer depth | Model-derived | Derived | Later |
| Wave height | Forecast / buoy | Surface | **W1 driver** (workability) |
| Wind | Forecast / station | 10 m met | **W1 driver** |
| Tides / water level | Harmonic + residuals | Emersion clock | **W1 primary** |
| River discharge | Gauge | Watershed→estuary | Conditional freshwater |
| Ice | Remote | Surface | Out of AOI |

**W1 primary physical stack:** forecast **air** × **tide/emersion** × **wind/wave**. Water T is supporting. Satellite SST is **not** the headline layer.

---

## 3. Group B — Biogeochemical

| Layer | Typical truth | Honest caption | MVP |
|---|---|---|---|
| Chlorophyll-a | Remote / in situ | Pigment / biomass proxy for **phytoplankton**, not fish or oysters | Off (wrong 72h target) |
| Primary productivity | Model | Model-inferred | Later |
| Dissolved oxygen | In situ (no satellite DO) | Station depth; UNKNOWN on lease if unsensed | Supporting / often UNKNOWN |
| pH / aragonite | In situ / OA products | Larval/hatchery scale; weak for adult 72h | Off for W1 adult |
| Nutrients | Discrete samples | Sparse | Later |
| Turbidity / TSS | In situ / remote | Storm/runoff co-stressor | Conditional |
| Light attenuation Kd | Remote | First optical depth context | Later (explains why satellites miss animals) |
| CDOM | Remote | Case-2 water | Later |

HAB **cell** indicators (animal stress) ≠ NSSP **toxin** lists. If a HAB layer exists later, it is **not** food-safety and not mixed into OSI color.

---

## 4. Group C — Habitat

| Layer | Caption | Sensitivity |
|---|---|---|
| Bathymetry | Depth of seafloor · **not for navigation** | PUBLIC if licensed (GEBCO-class) |
| Slope / complexity | Derived from bathy | PUBLIC |
| Substrate | Geological map grain | As published |
| Coral / kelp / seagrass / mangrove | Official or published habitat maps | Unpublished remnants often `NEVER_PUBLISH` / coarsen |
| Estuary mask | Named water body | PUBLIC |
| MPA / critical habitat | **Exactly** authority polygon | Link out |
| Spawning / nursery | Default **withhold** | See `sensitive_display_rules.md` |

Habitat fill uses **teal suitability encoding only when the quantity is suitability**. A kelp polygon is a **presence of habitat structure** (remote or survey), not a fish count.

---

## 5. Group D — Biological

| Layer | Quantity class | Default publish |
|---|---|---|
| Prey field / plankton | Suitability or remote chl — **labeled** | Coarsen |
| Predator distribution | Usually withhold / delay / coarse | Listed taxa `NEVER_PUBLISH` fine |
| Larval transport | Model particles · `FORECAST`/`MODEL_INFERENCE` | Research |
| Disease / HAB **stress** indicators | Named taxon; not toxin legality | Careful split from NSSP |
| eDNA detections | Occupancy of molecules | Rare/listed: withhold GPS |
| Acoustic activity | Detections, not census | No mammal localization |
| Survey density | Effort of sampling | PUBLIC as coverage |
| Observed richness | Count of **taxa records**, effort-biased | Not biodiversity truth |

**MVP biological layer:** **none** as a life heatmap. W1 shows **ops-stress**, which is operational/environmental, not oyster abundance.

---

## 6. Group E — Operational (coverage & health)

These are **first-class MVP layers**.

| Layer | Shows |
|---|---|
| Data-collection density | Independent samples per cell × depth × window |
| Vessel/sensor coverage | Where **permitted**; not AIS-as-fish; partner vessels PRIVATE |
| Direct-observation recency | Time since last `DIRECT_OBSERVATION` |
| Forecast confidence | High/Med/Low/None field |
| Data-source health | Outage / fallback |
| Model extrapolation zones | Magenta ticks |
| Official-status freshness | DOH/NMFS last-verified (module B) |

---

## 7. MVP layer menu (implement)

```text
BASE
  [x] Earth + coastline
  [x] Bathymetry (not for navigation)
  [x] Willapa water-body mask
  [ ] DOH growing-area outline (context — harvest geography, not biology)

DRIVERS (pick ≤2 in MVP)
  [x] Tide / emersion (fixture)
  [ ] Forecast air (fixture)
  [ ] Wind / wave workability (fixture)
  [ ] SST skin (fixture) — labeled NOT oyster body temperature

ESTIMATE
  [x] OSI-72 ops-stress tercile (fixture, Category D) · NOT food-safety
  [ ] Occurrence p          [later]
  [ ] Habitat suitability   [later]
  [ ] Abundance / CPUE      [later / private]

COVERAGE (recommended on)
  [x] Unknown / data-gap
  [x] Observation density (synthetic)
  [ ] Source outages        [later]

LOCKED OFF
  AIS / GFW, public CPUE, live tags, harvest open/closed as model, food-web
```

---

## 8. Inspect payload (cell)

Minimum numeric inspect (in addition to 16 evidence fields):

- Layer id, quantity class, units  
- Value or rank or `UNKNOWN`  
- Truth state  
- Depth status  
- As-of timestamps  
- Distance to nearest in-situ (km) if env  
- `known_missing_inputs[]`

No “AI score 82.”
