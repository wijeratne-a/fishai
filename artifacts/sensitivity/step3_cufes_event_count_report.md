# Step 3 — CUFES event count report

## Event table (PR #4 quality-checked ingest)

This report uses the **quality-checked CUFES event table** produced by bot1 calcofi CUFES ingest (merged in **PR #4**): one row per `event_id` after ERDDAP pull and biology QC (`pump_readings_used`, `short_event`, speed review flags, etc.). It is **not** the raw ERDDAP event download (~15,969 rows pre-QC).

| Field | Value |
| --- | --- |
| File path (repo-relative) | `data/processed/calcofi_cufes/cufes_events.parquet` |
| Git commit (checkout used to read the file) | `0358c71a259df4479cf80c7bcff712ec45be3c40` |
| Row count | **14,592** (confirmed; matches `event_count_guard.n_events` in `configs/sensitivity_short_samples.yaml`) |

No additional filters were applied for the counts below: **no** `duration_min` threshold, **no** `short_event` exclusion, and **no** ocean-covariate / GLORYS availability filter.

Companion long table for per-species counts: `data/processed/calcofi_cufes/cufes_counts.parquet` (82,426 rows; one row per event × taxon for events in the QC table).

Event `time` span on the full QC table: **1996-03-16** through **2022-04-19** (UTC on `time`).

| Metric (full QC table) | Value |
| --- | ---: |
| Events | 14,592 |
| `short_event == FALSE` | 13,326 |
| `short_event == TRUE` | 1,266 |

`event_id` is unique (14,592 distinct keys).

## Egg-split test window (date filter only)

Production YAML window: **2018-01-01** through **2022-04-27** (`egg_split.test_start` / `test_end`). Only this **calendar** filter is applied on the PR #4 event table; still no duration or ocean-data filtering.

| Metric | Value |
| --- | ---: |
| Events in test window | **1,336** |

Per-species positives: `cufes_counts` rows for each taxon whose `event_id` is in the test-window event set; positive = `count > 0`.

| Taxon | Count rows in test window | Positive events (`count > 0`) |
| --- | ---: | ---: |
| sardine | 1,336 | **84** |
| anchovy | 1,336 | **538** |

## Spring seasons with events (Feb–May, test window only)

Among the **1,336** test-window events, a spring season is a calendar **year** with at least one event in **February–May** (still no duration or ocean-data filter).

| Metric | Value |
| --- | ---: |
| Distinct spring seasons with ≥1 event | **4** |
| Years | 2018, 2019, 2021, 2022 |

No Feb–May events fall in **2020** within this test window on the QC table.

---

Recompute (aborts if the QC table row count ≠ 14,592):

```bash
python3 scripts/report_step3_cufes_event_counts.py
```
