# Globe data API — what the visual client may ask for

**Agent:** VISUAL_PERFORMANCE / TECHNOLOGY-EVALUATION  
**Date:** 2026-09-18  
**Status:** Contract for the visual client. No live service. Prototype may implement with **static JSON** under `globe/prototype/`. Aligns with as-of replay (`artifacts/geospatial_data_engineer/as_of_replay_design.md`) and the 14-field product contract (`artifacts/scientific_red_team/prediction_contract.md`).

The globe is an **L9/L5 consumer**. If the panel disagrees with L3 `ModelPrediction`, **L3 wins**.

---

## 0. Laws (no future leakage)

1. Every read is scoped by a **snapshot key**: `forecast_id` **or** (`as_of_utc` + `model_version` + `privacy_tier`). There is no unversioned `/latest`.  
2. Server (or static file set) only includes rows with `published_at_utc ≤ source_data_cutoff_utc` and `ingested_at_utc ≤ cutoff` (v1 strict rule).  
3. Outcomes whose `observed_at` falls **inside** that forecast window are **labels for eval**, never features, never map fills for that issuance.  
4. Time slider cannot request a clock after the newest **issued** snapshot. No client-side “nowcast” from live SST.  
5. `retrospective_corrected` data **must not** appear on the partner-facing globe. Research lane = separate flag, default off.  
6. PUBLIC responses drop lat/lon, partner ids, lease ids, vessel ids, raw GPS.  
7. Numeric precision follows the contract: ranks/terciles/indicators, not three-decimal biological probabilities, unless a human reviewer accepted calibration.

---

## 1. Snapshot metadata (required chrome)

`GET /globe/v0/snapshots/{forecast_id}`

```json
{
  "forecast_id": "01800000-0000-7000-8000-000000000031",
  "wedge_id": "UNRESOLVED",
  "aoi_id": "willapa_bay_public_waterbody_fixture",
  "privacy_tier": "PUBLIC",
  "privacy_policy_applied": "public_growing_area_or_h3_parent_res5; no exact coordinates",
  "issued_at_utc": "2026-09-18T23:00:00Z",
  "forecast_window_start_utc": "2026-09-18T23:00:00Z",
  "forecast_window_end_utc": "2026-09-21T23:00:00Z",
  "source_data_cutoff_utc": "2026-09-18T22:00:00Z",
  "training_data_cutoff_utc": null,
  "feature_snapshot_id": "01800000-0000-7000-8000-000000000032",
  "model_version": "none-design-stub",
  "model_type": "baseline.none",
  "species_scope": "Magallana gigas (AphiaID 836033) — fixture",
  "geographic_scope": "Willapa Bay named water body (not a lease map)",
  "time_mode": "FORECAST",
  "is_retrospective": false,
  "is_retrospective_corrected": false,
  "feature_freshness_summary": {
    "nws.air": "2026-09-18T21:00:00Z",
    "coops.tides": "2026-09-18T00:00:00Z"
  },
  "known_missing_inputs": ["on_lease_sensors", "partner_outcomes_not_yet_collected"],
  "last_direct_observation_at_utc": null,
  "data_coverage": "fixture_sparse",
  "confidence_category": "low",
  "prediction_contract_category": "D",
  "tile_manifest_uri": "./tiles/PUBLIC/01800000-0000-7000-8000-000000000031/manifest.json",
  "user_visible_limitations": "SAMPLE / NOT A LIVE FORECAST. Not food-safety. Not harvest authorization."
}
```

Map chrome binds:

| Label | Field |
|---|---|
| Forecast issued at | `issued_at_utc` |
| Valid for | `forecast_window_start_utc` … `end` |
| Environmental inputs current through | min of `feature_freshness_summary` **or** `source_data_cutoff_utc` |
| Last direct observation in this area | `last_direct_observation_at_utc` (null → “none in snapshot”) |
| Forecast confidence | `confidence_category` |
| Model version | `model_version` |
| Data coverage | `data_coverage` |

`GET /globe/v0/snapshots?aoi=&privacy_tier=` returns the **list of issued ids** the slider may tick. Sorted by `issued_at_utc`. Prototype: a static `snapshots.json`.

---

## 2. Viewport tiles (not an observation API)

The visual client should **prefer tiles** (`tile_and_lod_design.md`):

```text
GET /globe/v0/tiles/{privacy_tier}/{forecast_id}/cells/{z}/{x}/{y}.mvt
GET /globe/v0/tiles/{privacy_tier}/{forecast_id}/env/{layer}/{z}/{x}/{y}.png
```

Prototype: MapLibre `pmtiles://` or a GeoJSON source. **No** `GET /observations?bbox=` that returns points.

If a JSON bbox API is ever added for debugging:

- `max_h3_res` clamped by privacy  
- hard cap (e.g. 5 000 features)  
- same snapshot key  
- reject if `privacy_tier=PUBLIC` and requested res &gt; 5 (fish) or non-polygon farm grain  

---

## 3. Cell pick payload (Evidence Explorer)

`GET /globe/v0/cells/{spatial_cell_id}?forecast_id=&depth_bin_id=`

`spatial_cell_id` is the **PUBLIC** id (`spatial_cell_id_public` or `official_unit_id`). Unknown id → 404 with `DATA_GAP` body, not an interpolated neighbor.

### 3.1 Required fields (every cell, every truth state)

| Field | Why |
|---|---|
| `spatial_cell_id` / `h3_res` / `cell_area_km2` | Index; area-honest |
| `official_unit_id` / `official_unit_type` | Operator geography |
| `truth_state` | Visual language (spec B) |
| `depth_bin_id` | Observatory registry |
| `depth_representation` | `bin` \| `integrated` \| `unknown` \| `intertidal_air` |
| `depth_uncertainty` | `known` \| `unknown` \| `integrated_due_to_data_limits` |
| `privacy_tier` | Publish class badge |
| `privacy_policy_applied` | Short explanation string |
| `units` | UCUM-like; **required even if value is null** |
| `value` | Rank/tercile/indicator or null |
| `value_display` | User string (“upper tercile”; “cannot issue”) |
| `prediction_contract_category` | A–E |
| `confidence_category` | `high` \| `medium` \| `low` \| `none` |
| `confidence_flags` | `stale` \| `extrapolated` \| `disputed` \| `data_sparse` (subset) |
| `data_support` | Observation density class |
| `model_version` | Replay |
| `feature_snapshot_id` | Replay |
| `issued_at_utc` / `forecast_window_*` / `source_data_cutoff_utc` | As-of |
| `published_inputs[]` | `{source_id, published_at_utc, role}` with `published_at ≤ cutoff` |
| `known_missing_inputs[]` | Honesty |
| `user_visible_explanation` | Why (allowed features only) |
| `user_visible_limitations` | What it is not |
| `user_visible_action_options` | Options, not commands |
| `what_would_reduce_uncertainty` | Spec H.16 |
| `source_attribution_bundle` | Licenses / links |
| `regulatory_context_snapshot` | Official module; **not** a model color |
| `last_verified_at_utc` | Closures/seasons |
| `species_taxon_id` | WoRMS LSID |
| `target_definition` | Named target |

Optional: `uncertainty_interval` only if a declared method produced it (no fake ±).

### 3.2 `truth_state` enum (canonical for globe)

Align with spec B / UI agent. Exactly one per visual object:

```text
DIRECT_OBSERVATION
REMOTE_DETECTION
SURVEY_INDEX
TAGGED_INDIVIDUAL
EDNA_DETECTION
ACOUSTIC_DETECTION
SONAR_BIOMASS_ESTIMATE
OPERATIONAL_CATCH_OR_EFFORT_OBSERVATION
MODEL_INFERENCE
FORECAST
HISTORICAL_RANGE
HABITAT_SUITABILITY
UNKNOWN
DATA_GAP
RESTRICTED_OR_COARSENED
```

Map from observatory UI codes when both exist:

| Observatory evidence class | Globe `truth_state` (typical) |
|---|---|
| `DIRECTLY_OBSERVED` | `DIRECT_OBSERVATION` |
| `REMOTELY_DETECTED` | `REMOTE_DETECTION` |
| `SURVEY_DERIVED` | `SURVEY_INDEX` |
| `TAG_TELEMETRY_DERIVED` | `TAGGED_INDIVIDUAL` |
| `OPERATIONALLY_OBSERVED` | `OPERATIONAL_CATCH_OR_EFFORT_OBSERVATION` |
| `MODEL_INFERRED` | `MODEL_INFERENCE` |
| `FORECAST` | `FORECAST` |
| `HYPOTHETICAL_RESEARCH` | do not paint on partner globe; research flag |
| `UNKNOWN_INSUFFICIENT` | `UNKNOWN` or `DATA_GAP` |

SST-as-layer is `REMOTE_DETECTION` **of temperature**, never `DIRECT_OBSERVATION` of oysters.

### 3.3 Depth

`depth_bin_id` from observatory registry (`INTERTIDAL_AIR`, `SURFACE_0_5`, `UPPER_5_25`, `SHELF_25_100`, … `BOTTOM_CONTACT`, `THERMAL_BAND:8_12C`, or `unknown`).

Click payload includes `depth_bins[]` for the Plotly curtain:

```json
"depth_bins": [
  {
    "depth_bin_id": "INTERTIDAL_AIR",
    "value": "elevated",
    "units": "{ops_stress_tercile}",
    "truth_state": "FORECAST",
    "confidence_category": "low"
  },
  {
    "depth_bin_id": "SURFACE_0_5",
    "value": null,
    "units": "Cel",
    "truth_state": "DATA_GAP",
    "confidence_category": "none"
  }
]
```

Do not interpolate missing bins into a continuous profile.

### 3.4 W1 oyster cell (contract language)

If `target_definition` is ops-stress:

- `prediction_contract_category`: **D**  
- `units`: `{ops_stress_tercile}` or similar — **not** `% dead`, **not** NSSP class  
- `user_visible_limitations` **must** include: not food-safety; not harvest authorization; SST is not body temperature; verify WA DOH  
- `regulatory_context_snapshot` is a **separate** object (`authority`, `last_verified_at_utc`, `stale`). Missing ≠ open.  
- `truth_state` for the score: `FORECAST` or `MODEL_INFERENCE`, never `DIRECT_OBSERVATION` of legality.

---

## 4. Evidence Explorer mapping (spec H, 16 fields)

| # | Panel | API |
|---|---|---|
| 1 | Current estimate | `value_display` + `units` + `time_mode=CURRENT_ESTIMATE` if issued as nowcast |
| 2 | Forecast estimate | same for `time_mode=FORECAST` (may be the only object in P0) |
| 3 | Confidence | `confidence_category` + flags |
| 4 | Last direct observation | `last_direct_observation_at_utc` + method |
| 5 | Observation count | `data_support.n` **if** PUBLIC-safe; else “withheld” |
| 6 | Observation types | `observation_types[]` enums |
| 7 | Environmental inputs | `published_inputs[]` |
| 8 | Key model drivers | `user_visible_explanation` allowlisted names only |
| 9 | Comparable historical conditions | `comparison_set` string |
| 10 | Model version | `model_version` |
| 11 | Validation | `validation_pointer` or `none` |
| 12 | Known limitations | `user_visible_limitations` |
| 13 | Source links / licenses | `source_attribution_bundle` |
| 14 | Data freshness | `feature_freshness_summary` |
| 15 | Privacy / coarsening | `privacy_tier` + `privacy_policy_applied` |
| 16 | What would reduce uncertainty | `what_would_reduce_uncertainty` |

Plus red-team: evidence tier of strongest label; category A–E; extrapolation flag; official last-verified.

---

## 5. Time modes

`time_mode` on snapshot **and** on cell (must match the tiles loaded):

```text
OBSERVED_HISTORY
CURRENT_ESTIMATE
FORECAST
CLIMATOLOGY
ANOMALY
SCENARIO
```

`SCENARIO` is research-only; not in partner MVP. `ANOMALY` requires a named reference period in `comparison_set`.

Playback: client sets `forecast_id`; **does not** send `valid_time` in the future of the last issuance.

---

## 6. As-of query parameters

| Param | Rule |
|---|---|
| `forecast_id` | Preferred. Implies cutoff + model + window. |
| `as_of_utc` | Allowed for research replay **of issued snapshots with issued_at ≤ as_of**. Must not pick unpublished revisions. |
| `split_name` | Default `prospective_pilot` / `retrospective_asof`. `retrospective_corrected` rejected on PUBLIC. |
| `privacy_tier` | Server ignores upward privilege from the client. Uses session. |

Illegal client requests (examples):

- `as_of_utc` in the future of server clock  
- env layer `published_at` &gt; cutoff  
- “include_labels=true” on the issuance that those labels evaluate  
- `h3_res=8&privacy_tier=PUBLIC`

Return **403** with a machine code (`FUTURE_LEAKAGE`, `PRIVACY_CLAMP`, `CORRECTED_LANE_FORBIDDEN`) rather than silently coarsening in a way that looks like data.

---

## 7. Units, versions, taxonomy

- `units` always present (use `{unknown}` if truly unknown — then confidence cannot be high).  
- `model_version` + `feature_snapshot_id` + `transform_hash` (optional) for explain.  
- `species_taxon_id` = `urn:lsid:marinespecies.org:taxname:{AphiaID}`.  
- Do not emit IUCN/GBIF geometries that fail harm review.

---

## 8. Prototype static mapping

No backend required:

```text
/fixtures/snapshots.json
/fixtures/snapshots/{forecast_id}.json
/fixtures/cells/{spatial_cell_id}.json
/fixtures/willapa_cells.geojson
```

Each cell JSON is a full §3 payload with **synthetic** values, mixed `truth_state`s, and W1 limitations text. Filenames are public ids only.

---

## 9. Out of scope for this API

- Chat that “just estimates.”  
- Reverse geocode of partner holes.  
- Vector tiles of PRIVATE GPS.  
- Streaming “live bite.”  
- Combining AIS with cells.  
- Food-safety or navigation endpoints.
