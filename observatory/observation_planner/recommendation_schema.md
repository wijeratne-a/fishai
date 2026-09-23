# Recommendation schema

**Date:** 2026-09-18  
**Status:** Contract for planner outputs. Every recommendation — including FIXTURE rows — must be instantiable as this object.  
**Privacy:** geography is H3 res **5–6** or a **named water-body / official unit**. No secret-spot GPS.

---

## 1. Object

```text
ObservationRecommendation
```

Machine analogue: one row of `fixture_recommendations.csv` plus the JSON fields below for APIs that do not exist yet.

---

## 2. Required fields

| Field | Type | Rules |
|---|---|---|
| `recommendation_id` | string | Stable; W1 fixture prefix `W1-FIX-R##` |
| `fixture_flag` | bool | `true` in this pass. Real tasking forbids `true` silently becoming an order |
| `status` | enum | `DESIGN_FIXTURE` \| `SCORED` \| `HUMAN_APPROVED` \| `KILLED` \| `SUPERSEDED` |
| `issued_at_utc` | datetime | Design date 2026-09-18 for fixtures |
| `wedge_id` | enum | `W1_OYSTER_WILLAPA` \| `W2_CHINOOK` \| `W3_LOBSTER` \| `GLOBAL_RESEARCH` |
| `target_taxa[]` | list | Scientific name + WoRMS AphiaID. W1: *Magallana gigas* `836033` (+ synonym 140656 for joins). Do not mix *Ostrea lurida* |
| `life_stage` | string | W1: farmed grow-out / seed-as-stated. Not larvae unless hatchery wedge |
| `geography_named` | string | Water-body or official unit (`Willapa Bay, Pacific County, WA DOH growing-area cluster (FIXTURE)`) |
| `official_unit_id` | string or null | Growing area / PFMC area / NEFSC SA — **not** a lease corner |
| `h3_res` | int | **5 or 6** for anything that could leave the partner ACL. Res 8 only inside `PRIVATE` and never in this public fixture CSV |
| `h3_cell_fixture_id` | string | **Synthetic** ID (`FIXTURE-H3R5-WILLAPA-CENTRAL`). Not a real H3 index in this pass |
| `depth_bin` | enum | `INTERTIDAL_AIR` \| `SURFACE_0_5` \| `BOTTOM` \| `WATER_COLUMN` \| `NA_METADATA` |
| `time_window` | string | Horizon the obs should cover (W1: next 72 h and/or next heat×emersion window) |
| `modality` | enum | See `modalities.md` |
| `ladder_stage` | enum | `PUBLIC_DATA` \| `PARTNER_EXPORT` \| `EXISTING_SENSORS` \| `MANUAL_STRUCTURED` \| `MOBILE_CAPTURE` \| `INTEGRATION` \| `NEW_HARDWARE` |
| `expected_ig` | object | `{eur, method, implementable_now}` |
| `cost` | object | `{band, label: ESTIMATE\|UNKNOWN\|CITED, note}` — no fake USD quotes |
| `validation_objective` | string | Which label/baseline/confidence this obs is for |
| `ecological_risk` | string | Residual disturbance / dual-use |
| `operational_constraints` | string | Weather, DUA, staff time, no auto-task |
| `fallback_modality` | string | If primary infeasible |
| `model_uncertainty_reduced` | string[] | Named uncertainties (e.g. `LABEL_SUPPORT`, `air_vs_tissue`, `B4_threshold`) |
| `emiv_ids[]` | list | Registry IDs from `observatory/emiv/` (`v0.1-draft`). Unresolved planner stubs allowed only if listed in `engine_id_crosswalk.md` |
| `privacy_tier` | enum | `PUBLIC` \| `COARSENED` \| `DELAYED` \| `RESTRICTED` \| `PRIVATE` \| `NEVER_PUBLISH` |
| `harm_review` | enum | `NOT_REQUIRED_NON_BIO_PUBLIC` \| `PASS` \| `FAIL` \| `PENDING` \| `FIXTURE_PENDING_HUMAN` |
| `ovs_components` | object | All 0–1 inputs + penalties |
| `ovs` | float | After penalties |
| `kill_flag` | bool | |
| `kill_rule` | string or null | Code from `scoring_spec.md` §4 |
| `human_approval_required` | bool | **Always true** before field tasking |
| `what_it_does_not_mean` | string | Contract exclusions |

---

## 3. Scoring sub-object (`ovs_components`)

Required keys: `eur`, `ecological_importance`, `conservation_priority`, `decision_value`, `forecast_disagreement`, `feasibility`, `cost_efficiency`, `harm_penalty`, `legal_privacy_penalty`, `ovs`.

Optional: `eur_method` (`RULE_MISSING_CRITICAL` \| `ENSEMBLE_SPREAD` \| `EVSI_DISCRETE` \| `NOT_IDENTIFIABLE`).

---

## 4. Detection ternary (required when the rec is biological presence)

| Field | Enum |
|---|---|
| `detection_state_targeted` | `SPECIES_ABSENT` \| `NOT_DETECTED` \| `NO_OBSERVATIONS` \| `NOT_APPLICABLE` |

W1 farm outcomes: `NOT_APPLICABLE` (stock presence is operator-known). Do not encode unstocked leases as biological absence of the species in the Pacific.

---

## 5. Privacy and harm (required)

| `privacy_tier` | Allowed in fixture CSV? | Notes |
|---|---|---|
| `PUBLIC` | Only non-biological pairing (tide × NWS air) after harm review | No animal pins |
| `COARSENED` | Yes, H3 5–6 / named bay | Default research grain |
| `PRIVATE` | Yes as **action class**, not as lease GPS | Farm logs |
| `NEVER_PUBLISH` | Only as **killed examples** | Must have `kill_flag=true` if the rec would *target* that class |

`harm_review=FAIL` ⇒ `kill_flag=true`. `FIXTURE_PENDING_HUMAN` is allowed on design rows; it does **not** authorize publication.

---

## 6. EMIV IDs (registry `v0.1-draft`)

Source of truth: [`../emiv/emiv_registry.csv`](../emiv/emiv_registry.csv). Old `EMIV-ENV-*` / `EMIV-OUT-*` stubs → registry map: [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md). Do not invent a parallel ontology.

| ID | Meaning | Status |
|---|---|---|
| `EMIV-PHY-ATEMP-001` | Near-surface air temperature | **W1_CORE** |
| `EMIV-PHY-TIDE-001` | Tide stage / water level | **W1_CORE** |
| `EMIV-PHY-EMERS-001` | Intertidal emersion duration and timing | **W1_CORE** |
| `EMIV-PHY-SOLAR-001` | Incoming solar / insolation during emersion — **not chlorophyll** | **W1_CORE** |
| `EMIV-PHY-TISST-001` | Tissue or bag/bed thermistor temperature | CANDIDATE; **W1_CORE** when partner sensor exists |
| `EMIV-PHY-WTEMP-001` | Near-surface bulk water temperature | **W1_CORE** |
| `EMIV-PHY-SST-001` | Satellite SST (skin or foundation) — supporting **proxy** only | **W1_PROXY** |
| `EMIV-BGC-DOXY-001` | Dissolved oxygen | **W1_CORE** |
| `EMIV-PHY-SALIN-001` | Practical salinity | **W1_CORE** |
| `EMIV-PHY-WIND-001` | Surface wind | **W1_CORE** |
| `EMIV-PHY-WAVE-001` | Sea state / waves | **W1_CORE** |
| `EMIV-ECO-OPSOUT-001` | `ops_disruption_72h` partner outcome (mortality, workability, intervention) | **W1_CORE** |
| `EMIV-HUM-CULT-001` | Culture method / tidal elevation | required W1 metadata |
| `EMIV-HUM-HARV-001` | Official harvest / closure status — **constraint, not ops label** | must-show |
| `EMIV-BIO-EDNA-001` | eDNA occupancy (not abundance) | CANDIDATE |
| `EMIV-QUA-PDETECT-001` | Detection probability | CANDIDATE |

**Unresolved planner keys (no registry row; engine internals / geography / taxon — do not mint EMIVs):** `EMIV-TAX-MGIG-001` (*M. gigas* Aphia 836033), `EMIV-GEO-WBAY-001`, `EMIV-GEO-H3C-001`, `EMIV-MOD-B4-001`, `EMIV-MOD-B12-001`, `EMIV-UNC-EUR-001`, `EMIV-UNC-OVS-001`, `EMIV-DET-TRI-001`, `EMIV-DET-OCC-001` (occupancy ψ as a score, not eDNA), `EMIV-POL-HARM-001`, `EMIV-POL-PRIV-001`. Solar geometry is `EMIV-PHY-SOLAR-001`. Bag/tissue T is `EMIV-PHY-TISST-001`.

A recommendation lists **all** registry EMIVs it would write or constrain, plus any unresolved local keys still in force.

---

## 7. Forbidden field contents

- Latitude/longitude at native farm, nest, haul-out, or aggregation grain  
- MMSI / vessel name  
- Another farm’s mortality  
- “Safe to harvest,” “open/closed” as model output  
- Real H3 indexes chosen to hug a known lease (this pass uses obviously fake `FIXTURE-H3R*` strings)  
- Commands: “sample this GPS,” “task glider to waypoint”

---

## 8. Minimal JSON example (FIXTURE, truncated)

```json
{
  "recommendation_id": "W1-FIX-R01",
  "fixture_flag": true,
  "status": "DESIGN_FIXTURE",
  "wedge_id": "W1_OYSTER_WILLAPA",
  "target_taxa": [{"scientific_name": "Magallana gigas", "aphia_id": 836033}],
  "geography_named": "Willapa Bay, Pacific County, WA (named growing waters, FIXTURE)",
  "h3_res": 5,
  "h3_cell_fixture_id": "FIXTURE-H3R5-WILLAPA-CENTRAL",
  "depth_bin": "NA_METADATA",
  "modality": "MANUAL_STRUCTURED_OUTCOME_FORM",
  "ladder_stage": "PARTNER_EXPORT",
  "privacy_tier": "PRIVATE",
  "harm_review": "FIXTURE_PENDING_HUMAN",
  "ovs": 0.658,
  "kill_flag": false,
  "human_approval_required": true,
  "emiv_ids": ["EMIV-ECO-OPSOUT-001", "EMIV-UNC-EUR-001"],
  "what_it_does_not_mean": "Not harvest legality, not food safety, not a public map."
}
```
