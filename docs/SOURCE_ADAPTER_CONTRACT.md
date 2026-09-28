# Source adapter contract

**Status:** Binding for any future normalizer. No ingest is authorized by this document alone.

An adapter maps one `source_id` + `protocol_id` into canonical entities (`source`, `event`, `observation`, `effort`, `taxon`, `measurement`, `provenance`).

## Required adapter outputs

| Output | Rule |
|---|---|
| `source` | Rights, license, `record_kind`, `presence_only`, `supports_survey_nondetection`, `coordinate_policy` |
| `event` | Stable `event_id`, `protocol_id`, `observed_at_utc`, **`time_precision`**, spatial support, privacy tier |
| `effort` | Emitted when the protocol completed a search unit; currencies are not interchangeable across protocols |
| `observation` | Only for biological taxon results; never for SST/chl/currents |
| `measurement` | `subject_kind` distinguishes `BIOLOGICAL` vs `ENVIRONMENTAL` |
| `provenance` | Immutable raw reference, checksums, transform version/hash, as-of `published_at_utc` |

## Adapter must refuse

- Treating missing species rows as absences without a proven frame rule
- Merging distinct `protocol_id` values into one likelihood without a bridge
- Labeling environmental rasters as fish observations
- Emitting presence-only gaps as zeros
- Promoting internal model scores to `PUBLISHED_NOWCAST`
- Writing fishing guidance or public raw coordinates
- Inventing numeric minimum-n thresholds (use `THRESHOLD_REQUIRES_POWER_ANALYSIS`)

## Pass criteria (conceptual)

1. Event keys collide only when the source says they are the same unit.  
2. Non-detections require `effort_completed=true` and taxon-in-frame.  
3. Every timestamp carries `time_precision`.  
4. Public materializations strip lat/lon.
