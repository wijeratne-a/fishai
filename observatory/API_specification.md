# Research API specification — evidence-typed observatory outputs

**Agents:** OCEAN_DATA_ARCHITECTURE_AGENT · DATA_ASSIMILATION_AND_DIGITAL_TWIN_AGENT  
**Date:** 2026-09-18  
**Status:** Design only. No public service. No ingest. Not a product API.  
**Audience:** internal research clients (notebooks, eval jobs, sibling agents). Commercial briefs remain email/SMS/PDF via product agents.

This API exposes **Layer 9** of `global_digital_twin_architecture.md` with the geospatial kernel, privacy tiers, as-of replay, and prediction-contract language intact. It is intentionally smaller than a “global ocean platform.”

---

## 1. Design principles

1. **Evidence-typed.** Every biological payload carries prediction category A–E, observation evidence tier, factory support tier T0–T6, confidence `high|medium|low|none`, data support, and limitations.  
2. **No manufactured maps.** Endpoints that would return empty-cell interpolations return `data_support=none` or omit the cell. There is **no** slippy-map tile route in v0.  
3. **Privacy at write-time.** PUBLIC/COARSENED responses cannot include lat/lon, lease ids, vessel ids, or PRIVATE feature dumps. Same rules as `security_and_access_model.md`.  
4. **Replay.** Forecast/nowcast GETs are by `forecast_id` and return the **issued** snapshot, not live tables.  
5. **Not a lake query API.** No “download all OBIS,” no bounding-box scrape of raw L0, no bulk NetCDF.  
6. **Auth.** v0: operator-local process on localhost. Pilot: signed requests + role (`redteam_ro`, `model_job`, `partner_owner`). No anonymous internet.  
7. **UTC** timestamps, ISO-8601 `Z`. WGS84 lon/lat **only** on PRIVATE/RESTRICTED roles.  
8. **Claims ceiling.** Public category C or D (red-team contract). Category A is refused unless `data_support` and factory tier allow it (v0: never). Category E is never a prediction.

**Base URL (not deployed):** `http://127.0.0.1:8741/obs/v0`

---

## 2. Common types

### 2.1 `EvidenceBadge`

```json
{
  "observation_evidence_tier": "T1_direct | T2_operational | T3_remote_or_modeled | T4_unverified",
  "prediction_contract_category": "A | B | C | D | E",
  "species_model_support_tier": "T0 | T1 | T2 | T3 | T4 | T5 | T6",
  "output_class": "DIRECTLY OBSERVED | REMOTELY DETECTED | SURVEY-DERIVED | TAG/TELEMETRY-DERIVED | OPERATIONALLY OBSERVED | MODEL-INFERRED | FORECAST | HYPOTHETICAL/RESEARCH MODE | UNKNOWN/INSUFFICIENT DATA",
  "confidence_category": "high | medium | low | none",
  "data_support": "none | low | medium | high",
  "extrapolation_risk": true,
  "extrapolation_dimensions": ["space", "depth", "season", "climate", "management_era", "platform"]
}
```

Rules (server-enforced):

- If `data_support` is `none` or `low` → `confidence_category` cannot be `high`.  
- If strongest label tier is T3_remote or weaker → cannot issue category C as High; SST/chl-only Chinook → `none`.  
- `T4_unverified` cannot appear as a prediction.  
- Factory `T0` → taxonomy only. `T2` is the ceiling for v0 oyster issuance until horizon tests exist.  
- `output_class` required on `/state` and `/forecasts` (see observatory README). v0 fixtures use `HYPOTHETICAL/RESEARCH MODE`.  
- `prediction_contract_category=E` allowed only on **covariate** resources, never `/state` or `/forecasts`.

### 2.2 `TwinState` (Layer 7/8)

Matches geospatial `ModelPrediction` plus observatory fields:

```json
{
  "forecast_id": "uuid",
  "wedge_id": "UNRESOLVED | oyster_wa_ops_72h | ...",
  "species_taxon_id": "urn:lsid:marinespecies.org:taxname:836033",
  "accepted_scientific_name": "Magallana gigas",
  "life_stage": "farmed_growout",
  "geographic_scope": "string",
  "spatial_cell_id": "h3",
  "h3_res": 8,
  "spatial_cell_id_public": "h3",
  "cell_area_km2": 0.737,
  "official_unit_id": "WA_DOH_GROWING_AREA:...",
  "depth_bin_id": "INTERTIDAL_AIR",
  "target_definition": "string",
  "predicted_state": { "value": 0, "unit": "{rank}", "label": "elevated_stress_indicator" },
  "uncertainty": { "interval": null, "rationale": "Unquantified: sparse events; category only" },
  "assumptions": ["Sessile planted stock", "SST ≠ tissue temperature"],
  "feature_freshness": { "coops.tides": "2026-09-18T10:00:00Z" },
  "known_missing_inputs": ["lease_do_sensor"],
  "validation": { "split_name": null, "status": "none" },
  "limitations": ["Not food-safety", "Not harvest authorization"],
  "user_visible_explanation": "string — official units only",
  "user_visible_action_options": "string — options, not commands",
  "model_type": "expert_rule_B4",
  "model_version": "B4-v0",
  "species_model_support_tier": "T2",
  "output_class": "HYPOTHETICAL/RESEARCH MODE",
  "issued_at_utc": "2026-09-18T12:00:00Z",
  "forecast_window_start_utc": "...",
  "forecast_window_end_utc": "...",
  "source_data_cutoff_utc": "...",
  "feature_snapshot_id": "uuid",
  "privacy_policy_applied": "public_growing_area_only",
  "is_retrospective": false,
  "suppressed": false,
  "evidence": { "$ref": "EvidenceBadge" }
}
```

No `latitude` / `longitude` on PUBLIC/COARSENED.

### 2.3 Error object

```json
{
  "error": "insufficient_evidence | rights_blocked | privacy_stripped | closed_universe | not_found | replay_divergence | not_implemented",
  "message": "human readable",
  "evidence": { "$ref": "EvidenceBadge" }
}
```

HTTP mapping: `404` not found; `403` rights/privacy; `409` replay divergence; `422` would require manufactured confidence (e.g. client asked for a dense grid); `501` sequential DA routes.

---

## 3. Endpoints

All JSON. All require `X-FishAI-Role` in pilot; localhost implicit `operator_local` in v0.

### 3.1 Taxonomy — Layer 0

`GET /taxa/{aphia_id}`

Returns cached WoRMS subset (accepted name, synonyms, LSID, citation). `404` if never cached. **Does not** query WoRMS live in a tight loop; cache refresh ≤ 90 days (`storage_and_retention_plan.md`).

`GET /taxa/{aphia_id}/ecology`

Layer 4 dossier pointer: envelope fields, citations, `cannot_predict[]`, food-web notes, `ecology_dossier_version`. Empty object + `species_model_support_tier=T0` if no dossier.

### 3.2 Observations — Layer 2 (metadata, not a dump)

`GET /observations`

Query: `taxon`, `entity_type`, `official_unit_id`, `depth_bin_id`, `time_start`, `time_end`, `privacy_tier`, `as_of` (defaults to now).

Returns **counts and freshness**, plus at most **N=50** PUBLIC/COARSENED example rows **without coordinates**. PRIVATE rows: `count` only unless role is `partner_owner` for that `partner_id`.

**Not provided:** `/observations/export.zip`, ERDDAP-style full scrape.

### 3.3 Habitat / env — Layer 3

`GET /habitat/cells/{spatial_cell_id}`

Query: `depth_bin_id`, `as_of`, `variables` (allowlist: `air_temperature`, `sea_water_temperature`, `dissolved_oxygen`, `salinity`, `sea_surface_wave_significant_height`, `emersion_hours`, …).

Returns latest as-of sample **if stored for the AOI**. `data_support=none` if the cell was never ingested (normal). Category E covariates permitted here with badge `prediction_contract_category=E` and text “covariate, not abundance.”

`GET /habitat/official-units/{official_unit_id}`

Polygon metadata, edition, `valid_from/to`. Growing-area geometry may be PUBLIC **as the agency publishes it**.

### 3.4 Features — Layer 5

`GET /features/{feature_snapshot_id}`

Role `model_job` or `operator_local`. PUBLIC role: allowlisted keys only (official unit, coarsened cell, env variable names — **no** private GPS, **no** neighbor farm ids). Includes `leakage_check_passed`, cutoff, hashes.

### 3.5 Twin state / forecasts — Layers 7–8

`GET /forecasts/{forecast_id}`

Issued `TwinState`. This is the **explain** path’s payload.

`GET /forecasts/{forecast_id}/explain`

Geospatial replay explain: inputs used/missing, fallbacks, regulatory snapshot, user-visible text as delivered. No recompute. No private coordinates.

`POST /forecasts/{forecast_id}/rebuild-features`  
Role `operator_local` only. Integrity check vs snapshot hash. On mismatch: `409 replay_divergence`. **Not implemented in v0** (`501`).

`GET /state`

Query: `taxon`, `official_unit_id` **or** `spatial_cell_id`, `depth_bin_id`, `at` (validity time), `as_of` (cutoff).

Returns the **latest issued** TwinState whose window contains `at` and whose cutoff ≤ `as_of`. If none: `404` or `200` with `confidence_category=none` and no `predicted_state` — **config choice: prefer 200+none so clients do not retry into interpolation.**

**No** `GET /state/grid?bbox=&res=` that fills the ocean.

### 3.6 Factory — Layer 6 metadata

`GET /models`

Lists registry entries (empty today): `model_version`, `model_type`, `taxon`, `aoi`, `target_definition`, `species_model_support_tier`, `training_data_cutoff_utc`, `validation.status`.

`GET /models/{model_version}`

Assumptions, limitations, baseline ids it must beat.

### 3.7 Evaluation — Layer 10 / eval

`GET /evaluations`

Query: `forecast_id`, `split_name=retrospective_asof|retrospective_corrected|prospective_pilot`.

Honest-lane metrics only in any payload marked `customer_claim_eligible=true`. Mixing lanes → `422`.

### 3.8 Feedback

`POST /feedback`

30-second outcome form (worked tide Y/N, mortality noticed Y/N, etc.). `PRIVATE`. Does not mutate the referenced forecast.

### 3.9 Explicitly absent routes (do not add in v0)

| Route | Why absent |
|---|---|
| `/map/tiles/{z}/{x}/{y}` | Public heatmap risk |
| `/abundance/{taxon}` | Category A not identified |
| `/eda/stream` | No bulk ingest |
| `/particles/{id}/geojson` public | Transport clouds can leak sources |
| `/ais/*` | Not abundance; privacy |
| `/whales/now` | NEVER_PUBLISH |
| `/harvest/safe` | Food-safety wall |
| `/chat` | Unbounded claims |

---

## 4. Example: v0 oyster nowcast (synthetic)

`GET /state?taxon=836033&official_unit_id=WA_DOH_GROWING_AREA:Willapa-Nahcotta-fixture&at=2026-09-18T20:00:00Z`

```json
{
  "forecast_id": "01800000-0000-7000-8000-000000000031",
  "wedge_id": "UNRESOLVED",
  "species_taxon_id": "urn:lsid:marinespecies.org:taxname:836033",
  "accepted_scientific_name": "Magallana gigas",
  "official_unit_id": "WA_DOH_GROWING_AREA:Willapa-Nahcotta-fixture",
  "depth_bin_id": "INTERTIDAL_AIR",
  "target_definition": "72h operational stress / disruption indicator (Category D), not harvest legality",
  "predicted_state": {
    "value": "elevated",
    "unit": "{indicator_rank}",
    "label": "elevated_operational_stress_indicator"
  },
  "uncertainty": {
    "interval": null,
    "rationale": "Unquantified: no partner mortality series; rule-based indicator only"
  },
  "assumptions": [
    "Planted sessile stock",
    "Air temperature × daytime emersion is a causal stressor (Raymond et al. 2022)",
    "Satellite SST is not tissue temperature"
  ],
  "feature_freshness": { "coops.9440910": "2026-09-18T18:00:00Z" },
  "known_missing_inputs": ["partner_outcomes_not_yet_collected", "lease_do_sensor"],
  "validation": { "status": "none" },
  "limitations": [
    "This is not a food-safety determination and not harvest authorization.",
    "Verify WA DOH growing-area and biotoxin status at the authority.",
    "Microclimate (bag color, elevation in cm) is unobserved."
  ],
  "model_type": "expert_rule_B4",
  "model_version": "none-design-stub",
  "species_model_support_tier": "T2",
  "output_class": "HYPOTHETICAL/RESEARCH MODE",
  "issued_at_utc": "2026-09-18T12:00:00Z",
  "source_data_cutoff_utc": "2026-09-18T11:00:00Z",
  "privacy_policy_applied": "growing_area_only_no_lease_gps",
  "evidence": {
    "observation_evidence_tier": "T3_remote_or_modeled",
    "prediction_contract_category": "D",
    "species_model_support_tier": "T2",
    "output_class": "HYPOTHETICAL/RESEARCH MODE",
    "confidence_category": "low",
    "data_support": "low",
    "extrapolation_risk": true,
    "extrapolation_dimensions": ["platform"]
  },
  "notes": "Fixture. No model trained. No data ingested."
}
```

---

## 5. Versioning and compatibility

- Path `/obs/v0` is frozen as **research**. Breaking changes increment to `/obs/v1` only after a human review.  
- Additive fields allowed. Removing a required evidence field is a breaking change.  
- Geospatial JSON Schemas under `artifacts/geospatial_data_engineer/schemas/` remain the storage contract; this API is a **view**. Category enum on storage schema currently lists C/D for product forecasts; observatory API may return B on survey-index research resources later, never A/E as predictions in v0.

---

## 6. What this API will not become

A commercial multi-tenant SaaS, a global data marketplace, an LLM tool-calling surface without the prediction contract, or a substitute for WA DOH / NMFS / DMR official systems.

Implementation is **out of scope** until wedge lock + rights. Until then, the JSON examples are fixtures only.
