# Anomaly / change-detection event schema

**Date:** 2026-09-18  
**Status:** Schema only. No live writer. Fixtures in `fixture_events.csv` are the only instances.  
**Storage later:** one row (or JSON document) per event; kernel timestamps from `artifacts/geospatial_data_engineer/schemas/_ObservationKernel.schema.json` when a store exists. Do not fork a second identity system.

Privacy is a **write-time** property. Native lease GPS, farm KPIs, spawn waypoints, and listed-taxon pins never enter a PUBLIC table (`observatory/sensitive_location_policy.md`).

---

## 1. Identity and issuance

| Field | Type | Required | Notes |
|---|---|---|---|
| `event_id` | string | yes | Stable slug, e.g. `FIX-CD-2021-001`. Production: UUIDv7. |
| `record_status` | enum | yes | `FIXTURE_RESEARCH_ONLY` (only legal value in this pass). Future: `CANDIDATE_INTERNAL` \| `HUMAN_ACCEPTED` \| `HUMAN_REJECTED` \| `SUPERSEDED`. |
| `issued_as_operational_alert` | boolean | yes | **Must be `false`** for every current row. A true value would be a product alert and is forbidden until review gates pass. |
| `story_eligible` | boolean | yes | Whether a user-facing narrative may be drafted. Fixtures: `false`. |
| `product_claim_family` | enum | yes | `W1_OPS_STRESS` \| `OBSERVATORY_RESEARCH_NOT_W1` \| `SUPPRESSED_PRIVACY`. |
| `event_class` | enum | yes | Closed set in §2. Exactly one. |
| `event_class_secondary` | enum or empty | no | Optional confounder class (almost always `POSSIBLE_OBSERVATION_ARTIFACT` or `DATA_GAP`). Does not replace primary. |
| `issued_at_utc` | datetime | yes | When the *record* was written (fixtures: 2026-09-18). Not “when the ocean changed.” |
| `as_of_utc` | datetime | yes | Source cutoff; no post-cutoff revisions in the honest lane. |
| `window_start_utc` / `window_end_utc` | datetime | yes | Validity of the claimed anomaly. |
| `schema_version` | string | yes | `CD-EVENT-2026-09-18-v1` |

---

## 2. `event_class` (closed)

```
RANGE_SHIFT
DEPTH_SHIFT
PHENOLOGY_SHIFT
AGGREGATION_EVENT
DISPERSAL_EVENT
POSSIBLE_MORTALITY_EVENT
POSSIBLE_HAB_EVENT
POSSIBLE_OBSERVATION_ARTIFACT
DATA_GAP
NO_SIGNIFICANT_CHANGE
```

**Assignment rule:** run `bias_vs_biology.md` first. Do not assign a biological class to win a demo.

**W1 allowlist:** `POSSIBLE_MORTALITY_EVENT`, `POSSIBLE_HAB_EVENT`, `POSSIBLE_OBSERVATION_ARTIFACT`, `DATA_GAP`, `NO_SIGNIFICANT_CHANGE`.

---

## 3. Taxon, stage, space, depth

| Field | Type | Required | Notes |
|---|---|---|---|
| `taxon_aphia_id` | int | yes | WoRMS accepted. Pacific oyster **836033** (*Magallana gigas*). |
| `accepted_scientific_name` | string | yes | Dual-label *C. gigas* in notes if needed for joins; do not treat as a second species. |
| `life_stages[]` | enum list | yes | W1 typical: `farmed_spat`, `farmed_growout`, `farmed_market`. Not hatchery larvae unless the operator is a hatchery. |
| `population_unit` | string | yes | `lease_stock` \| `growing_area_cluster` \| `management_area` \| `not_partitioned`. |
| `geographic_scope` | string | yes | Human-readable, official units. |
| `official_unit_type` | string | yes | e.g. `WA_DOH_GROWING_AREA`, `NMFS_STATISTICAL_AREA`. |
| `official_unit_id` | string | yes | Fixture IDs allowed (`…-fixture`). **No lease-corner GPS.** |
| `spatial_cell_id` / `h3_res` | string / int | no | Internal only. Public products use official unit or a coarser parent. |
| `spatial_grain_public` | enum | yes | `official_unit` \| `basin` \| `1deg` \| `withheld`. |
| `depth_bin_id` | enum | yes | Align with twin bins when present: `INTERTIDAL_AIR`, `SURFACE_0_5`, `SUBSURFACE`, `BOTTOM`, `DEPTH_UNKNOWN`. |
| `privacy_tier` | enum | yes | `PUBLIC` \| `COARSENED` \| `DELAYED` \| `RESTRICTED` \| `PRIVATE` \| `NEVER_PUBLISH`. Farm mortality/workability: **PRIVATE**. Aggregations of spawn/nursery: **NEVER_PUBLISH**. |
| `ecological_sensitivity` | string | yes | e.g. `farm_kpi`, `not_listed_aquaculture`, `spawn_aggregation`. |

Default when unsure: one privacy tier stricter. Reverse-engineering tests in `sensitive_location_policy.md` §8 apply before any map.

---

## 4. State vector (conceptual)

All of these are required as text or coded enums. Numeric fits are **not** required in this pass and must not be invented.

| Field | Content |
|---|---|
| `baseline_period` | Inclusive years or “month×unit climatology, training cutoff …” |
| `climatology_method` | e.g. `B12_month_x_growing_area_shrinkage_hypothesis`, `literature_case_reconstruction`, `none_data_gap` |
| `current_state_summary` | What the index/indicator is now (rank or qualitative). Category A–E named. |
| `anomaly_summary` | Current vs climatology on the **same** scale |
| `rate_of_change_summary` | Slope / change-point / `not_identifiable` |
| `spatial_shift_summary` | Centroid/edge or `not_identifiable` / `not_applicable_sessile_lease` |
| `depth_shift_summary` | or `not_identifiable` |
| `seasonal_timing_shift_summary` | or `not_identifiable` |
| `effect_magnitude` | **Rank or qualitative only** until a human accepts calibration: `reduced` \| `typical` \| `elevated` \| `unknown` |
| `effect_magnitude_scale` | Named comparison set, e.g. `this_lease × comparable_June_tides` |
| `uncertainty_rationale` | Prose; no fake ±% |
| `confidence_category` | `high` \| `medium` \| `low` \| `none` — same rule family as `uncertainty_policy.md` |
| `observation_coverage` | `none` \| `low` \| `medium` \| `high` |
| `observation_coverage_note` | What was actually sampled at this grain/depth |
| `confounders[]` | Catchability, handling, ploidy, weather-workability, regulation, platform change, … |
| `related_env_anomalies[]` | Objects (§6); `emiv_id` from registry `v0.1-draft` |
| `evidence_source` | Citations, program names, `as_of`; **not** ingested payloads |
| `evidence_output_class` | Observatory output class (`OPERATIONALLY OBSERVED`, `SURVEY-DERIVED`, `MODEL-INFERRED`, `UNKNOWN/INSUFFICIENT DATA`, …) |
| `prediction_contract_category` | `A`–`E`. Public/W1 biology: **C or D**. `E` is never the biological claim. |
| `alternative_explanations[]` | Observation-process explanations **listed first** |
| `known_missing_inputs[]` | |
| `what_it_means` | One paragraph |
| `what_it_does_not_mean` | Required negatives (food safety, abundance, public map, …) |

**Magnitude ban:** no three-decimal probabilities, no “+18.4% abundance,” no bag-level % dead as a product number without a partner protocol. Literature percentages may be **cited** in notes as someone else’s published result, not as an observatory measurement.

---

## 5. Review and recommended observation task

| Field | Type | Required |
|---|---|---|
| `human_scientific_review_required` | boolean | yes |
| `review_gate_ids[]` | strings | yes | From `validation_and_review_gates.md` |
| `recommended_observation_task` | object | yes | §7; may be `task_type=SUPPRESS_NO_TASK` |

Human review is **required before any user-facing story** for every biological class except that `DATA_GAP`, `POSSIBLE_OBSERVATION_ARTIFACT`, and `NO_SIGNIFICANT_CHANGE` may appear as **internal** coverage/quiet flags. Promoting those three to a customer story still needs the story gate (`G-STORY`).

---

## 6. EMIV binding (`related_env_anomalies[]`)

Registry: [`../emiv/emiv_registry.csv`](../emiv/emiv_registry.csv) (`v0.1-draft`). Fixture event IDs (`EMIV-FIX-…`) are **record keys**, not catalog variables. The `variable` slot is a registry `emiv_id` when a row exists.

```text
env_anomaly_id          # fixture record key, e.g. EMIV-FIX-2021-AIR-TMAX-PNW
emiv_id                 # registry ID, e.g. EMIV-PHY-ATEMP-001
variable                # legacy slug; prefer emiv_id
mechanism_note          # causal sentence; not "SST killed oysters"
sign                    # high | low | timing_shift | unknown
grain                   # lease | growing_area | basin | region
depth_bin_id            # must match or be explicitly mismatched
baseline_period
confidence_category     # none if not actually computed
emiv_schema_ref         # observatory/emiv/emiv_catalog.md
```

CSV encoding (this pass): `env_anomaly_id|emiv_id|sign|grain`. W1: air T = `EMIV-PHY-ATEMP-001`; emersion = `EMIV-PHY-EMERS-001`; SST-only skin = `EMIV-PHY-SST-001` (**PROXY**, not bulk water T). Unmapped tokens (`other`) stay literal — see [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md).

**W1 rule:** an air-temperature anomaly **without** overlapping **daytime emersion** is not a complete oyster lethal pathway. A Hood Canal ORCA dissolved-oxygen anomaly (`EMIV-BGC-DOXY-001` in the wrong basin) is **not** a Willapa `related_env_anomaly` for a Willapa lease (that is a `DATA_GAP` / wrong-basin confounder).

---

## 7. Observation-task object (planner consumer contract)

`observatory/observation_planner/` consumer contract. This object is the field list `observation_planner` recommendations should accept without rename.

```text
task_id                         # optional until planner issues IDs
task_type                       # enum below
planner_schema_ref              # observatory/observation_planner/task_schema.md#ObservationTask
objective                       # what would reduce uncertainty
taxon_aphia_id
official_unit_id
depth_bin_id
horizon                         # e.g. next_72h | next_spring_tide_series | next_survey_season
effort_requirement              # what must be logged (visits, hauls, bag counts)
privacy_tier                    # usually PRIVATE for W1 farm tasks
not_for_public_map              # always true for aggregations, lease KPIs, listed taxa
success_criterion               # what would upgrade DATA_GAP or split HAB vs ops
explicitly_not                  # e.g. NSSP tissue test impersonation; spawn GPS
```

### 7.1 `task_type` enum (v1)

| `task_type` | Typical class it serves | W1? |
|---|---|---|
| `LEASE_MORTALITY_PROTOCOL_COUNT` | `POSSIBLE_MORTALITY_EVENT` | yes |
| `LEASE_WORKABILITY_LOG` | ops disruption / B5 analogue | yes |
| `INTERTIDAL_MICROCLIMATE_LOGGER` | air×emersion vs SST mismatch | yes |
| `IN_SITU_DO_AT_CULTURE_DEPTH` | hypoxia co-stressor | yes, **in the same basin** |
| `SOUNDTOXINS_ANIMAL_STRESS_TAXA` | `POSSIBLE_HAB_EVENT` (not NSSP) | yes |
| `EFFORT_AND_DETECTABILITY_AUDIT` | `POSSIBLE_OBSERVATION_ARTIFACT` | yes |
| `COVERAGE_STATION_GAP_FILL` | `DATA_GAP` | yes |
| `DEPTH_STRATIFIED_REPEAT_SURVEY` | `DEPTH_SHIFT` / occupancy | research |
| `PHENOLOGY_CALENDAR_AUDIT` | `PHENOLOGY_SHIFT` | research |
| `RANGE_EDGE_SURVEY_REPEAT` | `RANGE_SHIFT` | research |
| `SUPPRESS_NO_TASK` | quiet / suppressed privacy | yes |
| `DO_NOT_COLLECT_SENSITIVE_GPS` | `AGGREGATION_EVENT` | yes — refuse fine GPS |

Planner implementations must not create a task whose success criterion is “publish a public aggregation heatmap” or “authorize harvest.”

---

## 8. JSON shape (normative example, fixture)

Not issued. Not a live `/anomalies` payload. Illustrates required keys only.

```json
{
  "event_id": "FIX-CD-2021-001",
  "schema_version": "CD-EVENT-2026-09-18-v1",
  "record_status": "FIXTURE_RESEARCH_ONLY",
  "issued_as_operational_alert": false,
  "story_eligible": false,
  "product_claim_family": "W1_OPS_STRESS",
  "event_class": "POSSIBLE_MORTALITY_EVENT",
  "taxon_aphia_id": 836033,
  "accepted_scientific_name": "Magallana gigas",
  "life_stages": ["farmed_growout", "farmed_market"],
  "official_unit_id": "WA_DOH_GROWING_AREA:Willapa-Nahcotta-fixture",
  "depth_bin_id": "INTERTIDAL_AIR",
  "privacy_tier": "PRIVATE",
  "baseline_period": "comparable June daytime-emersion windows at intertidal culture (climatology not fitted)",
  "effect_magnitude": "elevated",
  "effect_magnitude_scale": "published_event_vs_typical_June_intertidal_reports",
  "confidence_category": "low",
  "observation_coverage": "low",
  "human_scientific_review_required": true,
  "recommended_observation_task": {
    "task_type": "LEASE_MORTALITY_PROTOCOL_COUNT",
    "planner_schema_ref": "observatory/observation_planner/task_schema.md#ObservationTask",
    "privacy_tier": "PRIVATE",
    "not_for_public_map": true
  }
}
```

Full fixture table: `fixture_events.csv`.

---

## 9. API note

Do **not** add a public `GET /anomalies` grid in v0 (`API_specification.md` forbids manufactured maps). If a research route is added later, it returns fixtures or `confidence_category=none`, never a slippy heatmap of aggregations or farm kills.
