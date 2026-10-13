#!/usr/bin/env python3
"""Attach lag columns using only cached GLORYS subsets (no Copernicus fetch)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def main() -> int:
    from fishai.ingestion.adult.constants import (
        DEFAULT_EVENTS_PATH,
        DEFAULT_PROCESSED_DIR,
        DEFAULT_TRAINING_TABLE_PATH,
    )
    from fishai.ingestion.physics.cufes_training_covariates import (
        new_glorys_field_store_for_live_build,
        plan_glorys_subset_batches,
        populate_store_days_from_cache,
    )
    from fishai.ingestion.physics.lagged_ocean_covariates import (
        DEFAULT_LAG_DAYS,
        attach_lagged_physics_columns,
        required_lagged_columns,
        rows_with_complete_lags,
        unique_event_days_with_lags,
    )
    from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
    from fishai.ingestion.sources import REPO_ROOT as REPO

    import pandas as pd

    cache_dir = REPO / "data" / "cache" / "glorys_adult_cps"
    table = pd.read_parquet(DEFAULT_TRAINING_TABLE_PATH)
    events = pd.read_parquet(DEFAULT_EVENTS_PATH)
    event_ids = set(table["event_id"].astype(str))
    events = events[events["event_id"].astype(str).isin(event_ids)].reset_index(drop=True)

    days = unique_event_days_with_lags(events, lag_days=DEFAULT_LAG_DAYS)
    batches = plan_glorys_subset_batches(days)
    cfg = load_overlap_config()
    store = new_glorys_field_store_for_live_build(cfg)
    populate_store_days_from_cache(store, days, batches, cache_dir)

    lag_frame = attach_lagged_physics_columns(events, store, lag_days=DEFAULT_LAG_DAYS)
    merged = table.merge(lag_frame, on="event_id", how="left", validate="many_to_one")
    lag_cols = required_lagged_columns(DEFAULT_LAG_DAYS)
    complete = rows_with_complete_lags(merged, lag_cols)
    out = merged.loc[complete].reset_index(drop=True)

    out_path = DEFAULT_PROCESSED_DIR / "adult_cps_training_table_lagged.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)

    summary = {
        "mode": "cache_only",
        "glorys_days_requested": len(days),
        "glorys_days_loaded_in_store": len(store.days),
        "input_training_rows": int(len(table)),
        "rows_dropped_incomplete_lags": int((~complete).sum()),
        "output_rows": int(len(out)),
        "lag_columns": lag_cols,
        "output_path": str(out_path),
    }
    summary_path = DEFAULT_PROCESSED_DIR / "adult_cps_lagged_build_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
