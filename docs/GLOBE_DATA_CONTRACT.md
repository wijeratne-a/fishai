# Globe data contract

**Schemas:** `schemas/globe-evidence.schema.json`, `schemas/globe-model-output.schema.json`.  
**Aligns with:** `RESEARCH_PROBLEM.md`, `globe/prototype/docs/layer_semantics.md`.

## Evidence labels (exactly one)

| Label | May claim |
|---|---|
| `DIRECT_OBSERVATION` | Measured/seen under a named method (not SST-as-fish) |
| `STRUCTURED_SURVEY_DETECTION` | Detection inside a structured survey protocol |
| `SURVEY_NONDETECTION` | Completed effort, taxon in frame, no detection — **not ecological absence** |
| `HISTORICAL_OCCURRENCE` | Compiled past report — **not here now** |
| `RECENT_PRESENCE_EVIDENCE` | Recent presence signal short of a published nowcast |
| `ENVIRONMENTAL_CONDITION` | Ocean/habitat state — **not a fish observation** |
| `INTERNAL_MODEL_OUTPUT` | Research/internal score — **not a published nowcast** |
| `PUBLISHED_NOWCAST` | Only if card `publish_status=PUBLISHED` and nowcast issued |
| `PUBLISHED_FORECAST` | Only if card `publish_status=PUBLISHED` and forecast issued |
| `UNKNOWN` | Insufficient evidence; empty ocean default |

## Model output rules

1. `INTERNAL_ONLY` / `NOT_PUBLISHED` → `output_class` ∈ {`INTERNAL_MODEL_OUTPUT`, `UNKNOWN`}.  
2. `PUBLISHED` → `output_class` ∈ {`PUBLISHED_NOWCAST`, `PUBLISHED_FORECAST`}.  
3. Name one `prediction_target` and one `scientific_status`; do not collapse to “where the fish are.”  
4. **`fishing_guidance` must be false.**  
5. **No `latitude` / `longitude` fields** — `spatial_cell_id` only.  
6. **`time_precision` required.**  
7. **`minimum_sample_size` = `THRESHOLD_REQUIRES_POWER_ANALYSIS`** (no invented *n*).

## Cold-load honesty

Empty globe + `UNKNOWN` is a valid product state. Do not invent `PUBLISHED_*` layers to fill the map.
