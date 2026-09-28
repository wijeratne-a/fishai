# Field dictionary

Concise definitions for canonical fields. Types follow `schemas/*.schema.json`.

| Field | Meaning |
|---|---|
| `source_id` | Stable source slug |
| `protocol_id` | Named method; keep incompatible protocols separate |
| `record_kind` | Biological vs environmental vs taxonomy vs model |
| `presence_only` | Source cannot supply verified non-detections |
| `supports_survey_nondetection` | Complete frame can construct `SURVEY_NONDETECTION` |
| `coordinate_policy` | How native geometry may leave private storage |
| `event_id` | Sample unit / tow / transect / sampler event |
| `observed_at_utc` | Phenomenon time (UTC, ISO-8601) |
| `time_precision` | `SECOND`…`YEAR` or `UNKNOWN` — required, never implied |
| `spatial_support` | Point, tow, sample unit, cell, etc. |
| `spatial_cell_id` | Public/analytical cell (e.g. H3); globe uses this, not lat/lon |
| `privacy_tier` | `PUBLIC` / `COARSENED` / `RESTRICTED` / `PRIVATE` / `NEVER_PUBLISH` |
| `observation_state` | Presence, survey non-detection, presence-only, no survey, restricted, unknown |
| `evidence_class` / `evidence_label` | Globe/evidence vocabulary (see `GLOBE_DATA_CONTRACT.md`) |
| `effort_completed` | Search unit finished; required for non-detection |
| `taxon_id` / `aphia_id` | WoRMS-backed identity |
| `subject_kind` | `BIOLOGICAL` vs `ENVIRONMENTAL` (SST ≠ fish) |
| `measurement_type` / `_value` / `_unit` | Typed measured quantity |
| `provenance_id` | Lineage handle |
| `raw_payload_reference` | Immutable raw bytes URI/key |
| `published_at_utc` | Source availability time (as-of join) |
| `publish_status` | `NOT_PUBLISHED` / `INTERNAL_ONLY` / `PUBLISHED` |
| `output_class` | `INTERNAL_MODEL_OUTPUT` / `PUBLISHED_NOWCAST` / `PUBLISHED_FORECAST` / `UNKNOWN` |
| `prediction_target` | One of the six research targets; never “where the fish are” |
| `scientific_status` | What a drawn object may claim |
| `fishing_guidance` | Always `false` on public products |
| `minimum_sample_size` | Always `THRESHOLD_REQUIRES_POWER_ANALYSIS` |
