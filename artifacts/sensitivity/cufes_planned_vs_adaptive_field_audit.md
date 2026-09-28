# CUFES planned transect vs adaptive infill (PR #4 table audit)

Audit date: 2026-09-28 (FishAI PR #5 diagnostic pass).

## Processed `cufes_events` (bot1 / PR #4)

Columns written by `fishai.ingestion.biology.cufes.transform.row_to_event`:

- `event_id`, `time`, `lat`, `lon`, `stop_time`, `stop_lat`, `stop_lon`
- `volume_m3`, `pump_readings_used`, `duration_min`, `short_event`
- `implied_speed_kn`, `speed_review_flag`, `qc_flags`, `track_wkt`

**No** `planned_transect`, **no** `adaptive_infill`, **no** CalCOFI `line` / `station` columns.

`event_id` encodes ERDDAP keys: `CUFES:{cruise}:{ship_code}:{sample_number}`.

## Raw ERDDAP `erdCalCOFIcufes` fields fetched

`cruise`, `ship_code`, `sample_number`, positions/times, pump speeds, six egg count columns.

Standard CalCOFI line/station identifiers are **not** in the ERDDAP pull list. Separating planned-line from adaptive infill would require an external reference (e.g. published CalCOFI station positions matched by space/time or sample metadata). **FishAI does not invent a flag.**

## Optional sensitivity config

When a reference table is supplied:

```yaml
egg_split:
  test_event_filter:
    mode: planned_line_only
    planned_line_reference_path: path/to/planned_line_event_ids.csv
```

Reference CSV must include `event_id` or (`cruise`, `ship_code`, `sample_number`). Time-forward / test-window scoring can then use `filter_egg_test_period_scores()` or `filter_egg_split_scope(..., scope = "test")` with this filter.

Default `mode: all` (omit block) scores all test-period events.
