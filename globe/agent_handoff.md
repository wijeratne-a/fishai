# Agent handoff — USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT

**Date:** 2026-09-18  
**Write root:** `/Users/wijeratne/dev/fishai/globe/`  
**Did not write:** `fishai/artifacts/integration/**`, `fishai/project_state.json`, `fishai/observatory/**`  
**Did not ingest data.** Fixture language only.

---

## 1. What this globe is

The **long-term scientifically honest visual system** for a 4D, evidence-typed ocean interface. It is **not** the commercial MVP.

| Product | Surface | Status 2026-09-18 |
|---|---|---|
| Commercial FishAI | Email + PDF 72h **OPS-RISK** (recommended W1 Willapa Pacific oyster, **not** food-safety) | Paused 1×1×1×1; RECOMMENDED not DECIDED |
| Observatory | Blueprint, tiers, physics | Framework; no live twin |
| This globe | Visual contract + later local coarsened view | Spec complete; prototype is a sibling |

First **operational** visual (later): same chrome clipped to Willapa, serving W1 as a **local, coarsened, evidence-typed** ops-stress / coverage view — **not** a public global “fish are here” heatmap.

---

## 2. MVP mode list (recommended — not all 10)

**Ship / prototype these only:**

1. **Mode 1 — Earth surface** with named water body + **bathymetry (not-for-navigation)**  
2. **Mode 8 — Evidence / provenance** (16-field Evidence Explorer on click)  
3. **Mode 9 — Unknown / data-gap** (ignorance as a feature; hatch ≠ zero animals)  
4. **Persistent time readout:** issued_at · valid_for · inputs_through · last_direct_obs · confidence · model version · data coverage  

**AOI:** Willapa Bay, public geography, fixture cells.  
**W1 bind later:** Category D OSI-72 on coarsened cells; sticky **NOT FOOD-SAFETY / NOT HARVEST AUTH**.

**Explicitly later (do not build as v1):** Mode 2 subsurface volume, Mode 3–4 pelagic slices (W1 may stub an **emersion curtain panel**), Mode 5 seafloor habitat atlas, Mode 6 forecast playback, Mode 7 split compare, Mode 10 food-web, story mode, volumetric cloud, climate scenarios, species arcade.

---

## 3. Visual-truth encoding table (summary)

Never **red = fish-here**. Each quantity keeps its own legend.

| State / quantity | Encoding (color + required texture) |
|---|---|
| `DIRECT_OBSERVATION` | Black **solid** stamp/track |
| `REMOTE_DETECTION` | Sky `#56B4E9` solid + “skin/beam” chip |
| `SURVEY_INDEX` | Green `#009E73` **light hatch** · index units |
| `TAGGED_INDIVIDUAL` | Purple `#CC79A7` solid · **n individuals ≠ population** |
| `EDNA_DETECTION` | Yellow stipple · molecules, not GPS |
| `ACOUSTIC_DETECTION` | Blue `#0072B2` **wave hatch** |
| `SONAR_BIOMASS_ESTIMATE` | Orange **cross-hatch** · “index, not census” |
| `OPERATIONAL_CATCH_OR_EFFORT` | Olive-brown · **PRIVATE** default · CPUE ≠ stock |
| `MODEL_INFERENCE` | Sky 25–40% **dotted** outline |
| `FORECAST` | Amber 25–40% **dashed** + clock |
| `HISTORICAL_RANGE` | Muted blue · date range · not current |
| `HABITAT_SUITABILITY` | **Teal sequential** · not presence, not abundance |
| Occurrence *p* | **Purple sequential** · not a count (later) |
| Abundance / biomass | Orange hatch or graduated **symbols** · protocol required |
| CPUE | Olive · effort units · not abundance |
| `OPS_STRESS` (W1) | Gray Typical / amber Elevated / **red-outline** High / B/W Cannot-issue |
| `UNKNOWN` | Black/white **diagonal hatch** · insufficient evidence |
| `DATA_GAP` | Wider hatch · no samples · **not absence** |
| `RESTRICTED_OR_COARSENED` | Parent cells + lock/delay badge |

Confidence High/Med/Low/None modulates opacity + extra hatch. Extrapolation = magenta edge ticks. No 3-decimal biological *p* until prospective calibration is accepted.

---

## 4. What must never ship

**Universal**

- Public global “fish / life / hotspot” heatmap as commercial or observatory v1  
- One red (or red–green) scale meaning presence  
- Smooth interpolation or climatology fill across UNKNOWN without an explicit labeled layer  
- Live tracking of marine life; fish sprites; glow schools  
- AIS / VMS / GFW as abundance  
- SST or chlorophyll as animals, body temperature, safety, or legality  
- Three-decimal biological probabilities; 100 m hotspot maps as truth  
- Silent edits of issued forecasts; future leakage in replay  
- Unconstrained chat that will “just estimate”  
- Raw records in the browser; CSS-only privacy  
- Random jitter “for privacy”  
- Deceptive animation (invented mid-frames, chase-cam)  
- Volumetric cloud / food-web / story / climate scenario presented as MVP  

**Sensitive / legal**

- Native lease corners, farm KPIs, trap GPS, charter waypoints  
- Spawning / nesting / haul-out / listed-taxon precision; PAM bearings  
- TEK; vessel identity; competitor tracking  
- Model-colored harvest open/closed; combined OSI + DOH traffic light  
- Commands: fish here, harvest now, eat these, it is safe to go  

**Oyster / W1**

- Safe to eat / safe or legal to harvest / NSSP / toxin-free / no Vibrio  
- Green = harvest OK  
- SST ≥ 19 °C as a kill/harvest law  
- Totten / Vp Category 3 as demo geography  
- Percent mortality or abundance of wild set as the product  

**Claims ceiling:** no output stronger than the strongest evidence tier; Category C not issued from Tier-3-only inputs; High confidence not allowed when density is low.

---

## 5. Files written

| File | Role |
|---|---|
| `README.md` | Globe vs commercial email vs observatory |
| `visual_truth_states.md` | Mandatory states + language |
| `globe_modes.md` | 10 modes; MVP subset |
| `volume_4d_spec.md` | P(present\|x,y,z,t,env); depth unknown vs integrated |
| `time_and_forecast_ui.md` | Clocks and timeline states |
| `layer_stack.md` | Physical / BGC / habitat / biological / operational |
| `movement_visualization.md` | Tags vs corridors vs plumes |
| `abundance_encoding.md` | Separate legends/units |
| `evidence_explorer.md` | 16 fields; why/trust/missing/class |
| `unknown_map.md` | Ignorance as feature; required Low copy |
| `ecological_network_view.md` | Relationship classes; no fake causality |
| `story_mode.md` | Later explainer |
| `accessibility_and_trust.md` | Colorblind, SR, tables, no deceptive smooth |
| `sensitive_display_rules.md` | Six publish classes |
| `biological_variables_visual.md` | DVM, stages, bias, absent vs ND vs no obs |
| `user_output_contract_visual.md` | 14 fields on chrome+panel |
| `wireframes.md` | ASCII: chrome, panel, unknown, W1 stress view |
| `agent_handoff.md` | This file |

**Sibling-owned (do not conflict):** `visual_performance_architecture.md`, `technology_evaluation.md`, `stack_recommendation.md`, `tile_and_lod_design.md`, `api_for_globe.md`, `prototype/`. Sections L–M of the parent visual brief are the stack agent’s.

---

## 6. Recipients

| Recipient | Ask |
|---|---|
| Prototype agent | Implement M1+M8+M9+time readout only; fixture Willapa; banner honesty |
| Stack agent | 2D fallback OK; coarsen at zoom; do not send raw GPS to client; curtain = 2D plot |
| Commercial wedge | Do **not** expand SKU; do not make the globe the v1 product; email/PDF remain primary |
| Observatory architecture | Depth bins and as-of clocks already match; keep P0 twin tiny |
| Rights / safety | Licence UNKNOWN; no ingest; NEVER_PUBLISH list is a display block |
| Validation / red team | No user-facing model; fixture ranks; contract language unchanged |
| Founder | Lock W1/W2/W3; globe is not a decision to go global |

---

## 7. Confidence

| Claim | Confidence |
|---|---|
| MVP mode subset is the honest first visual | **High** |
| W1 as local coarsened ops-stress view can reuse this chrome later | **High** |
| A public global life globe is unsafe/unscientific as v1 | **High** (policy + physics + red team) |
| Commercial WTP for any map vs email | **Low** (no interviews); therefore globe is not the paid v1 |

---

## 8. Prohibited follow-ups

Do not treat this handoff as approval to ingest, train, publish tiles, contact farms, or overwrite `project_state.json` / commercial `artifacts/` / running observatory catalogs.
