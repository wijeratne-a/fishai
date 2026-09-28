# Step 3 — CUFES event count report (bot1 tables, unfiltered)

Source tables (no duration filter, no covariate-join filter):

| Table | Path | Rows |
| --- | --- | --- |
| Events | `data/processed/calcofi_cufes/cufes_events.parquet` | **14,592** |
| Counts (long) | `data/processed/calcofi_cufes/cufes_counts.parquet` | 82,426 |

Event time span on the full table: **1996-03-16** through **2022-04-19** (UTC timestamps on `time`).

## Full `cufes_events` table (QC columns only; no modeling drops)

| Metric | Value |
| --- | --- |
| Total events | 14,592 |
| `short_event == FALSE` | 13,326 |
| `short_event == TRUE` | 1,266 |

Each event has exactly one row in `cufes_events` (`event_id` unique).

## Egg-split test window (aligned with production model YAML)

Window: **2018-01-01** through **2022-04-27** (`egg_split.test_start` / `test_end`).

| Metric | Value |
| --- | --- |
| Events in test window (full events table) | **1,336** |

Per-species positives use the full `cufes_counts` table joined by `event_id` (taxon row present; positive = `count > 0`). No duration or covariate filtering.

| Taxon | Count rows in test window | Positive events (`count > 0`) |
| --- | ---: | ---: |
| sardine | 1,336 | **84** |
| anchovy | 1,336 | **538** |

## Spring seasons with events (Feb–May, test window only)

A spring season is calendar **year** with at least one event whose `time` falls in **February–May** and within the test window above.

| Metric | Value |
| --- | --- |
| Distinct spring seasons with ≥1 event | **4** |
| Years | 2018, 2019, 2021, 2022 |

(No Feb–May events appear in **2020** in this window on the full events table.)

---

Generated from local parquets in-repo; recomputed with:

```bash
python3 scripts/report_step3_cufes_event_counts.py
```
