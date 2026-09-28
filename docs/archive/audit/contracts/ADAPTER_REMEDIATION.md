# Adapter remediation (contracts audit)

**Status:** Guidance only. **Do not rewrite adapters in this workstream.** Schemas under `schemas/` are read-only here.

Synthetic conformance for tiny canonical objects is recorded in `CONFORMANCE_RESULTS.csv`. Field-level traps are listed in `FIELD_SEMANTIC_CONFLICTS.csv`.

## Priority remediations (when adapters are next touched)

1. **NUM average vs integer count (`C-NUM-01`)**  
   Atlantic RVC `NUM` must land as a real-valued index (`measurement_type` / `count_or_index_unit` = average), never coerced to `int`. Detection after length-bin collapse remains a separate boolean from the raw average.

2. **OBIS presence vs RVC non-detection (`C-OBIS-RVC-01`)**  
   OBIS rows → `PRESENCE_ONLY_NO_ABSENCE` (or historical/recent presence evidence). Never contribute to an RVC Bernoulli/detection table. Missing OBIS taxa must not mint `SURVEY_NONDETECTION`.

3. **Survey zero ≠ ecological absence (`C-ZERO-ABSENCE-01`)**  
   Keep `is_absence_claim=false`. Globe copy for `SURVEY_NONDETECTION` must state protocol miss only.

4. **SST ≠ fish sighting (`C-SST-FISH-01`)**  
   Environmental products stay on `measurement` with `subject_kind=ENVIRONMENTAL` or globe `ENVIRONMENTAL_CONDITION`. Refuse any path that writes SST into biological `observation` entities.

5. **Internal baseline ≠ published nowcast (`C-INTERNAL-NOWCAST-01`)**  
   Prevalence and holdout scores are `INTERNAL_MODEL_OUTPUT` / `NOT_PUBLISHED`. Adapters and materializers must refuse `PUBLISHED_NOWCAST` until `publish_status=PUBLISHED`.

6. **Pacific presence-only (`C-PACIFIC-ZERO-01`)**  
   Sources without constructible zeros must set `presence_only=true` and `supports_survey_nondetection=false`.

7. **Forecast times (`C-TIME-FORECAST-01`)**  
   Refuse `PUBLISHED_FORECAST` (and any probability layer derived from it) unless `issued_at_utc`, `valid_from_utc`, and `valid_to_utc` are all present.

## Public geometry

Globe and public rows use `spatial_cell_id` only. Native coordinates stay private; this audit never prints coordinates.

## Out of scope

- Rewriting existing adapter code  
- Touching `data/raw`, `globe/prototype`, `scripts/acquisition`, `labels/`, or `schemas/`  
- Running real model experiments or publishing layers
