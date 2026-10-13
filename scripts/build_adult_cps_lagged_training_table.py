#!/usr/bin/env python3
"""Augment adult CPS training table with 7d/14d GLORYS physics lags (same join geometry)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.adult.constants import (
        DEFAULT_EVENTS_PATH,
        DEFAULT_PROCESSED_DIR,
        DEFAULT_TRAINING_TABLE_PATH,
    )
    from fishai.ingestion.physics.cufes_training_covariates import (
        _subset_batch_live,
        new_glorys_field_store_for_live_build,
        plan_glorys_subset_batches,
        populate_store_days_from_cache,
    )
    from fishai.ingestion.physics.glorys_cufes_subset import enforce_subset_request_budget
    from fishai.ingestion.physics.glorys_training_build import (
        assert_copernicus_env_credentials,
        assert_store_ready_for_copernicus_export,
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

    parser = argparse.ArgumentParser(description="Build lag-augmented adult CPS training table")
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS_PATH)
    parser.add_argument("--training-table", type=Path, default=DEFAULT_TRAINING_TABLE_PATH)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PROCESSED_DIR / "adult_cps_training_table_lagged.parquet",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=DEFAULT_PROCESSED_DIR / "adult_cps_lagged_build_summary.json",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=REPO / "data" / "cache" / "glorys_adult_cps",
    )
    parser.add_argument(
        "--lag-days",
        type=int,
        nargs="+",
        default=list(DEFAULT_LAG_DAYS),
        help="Operational lags in days before event mid-time (default: 7 14)",
    )
    args = parser.parse_args(argv)

    import pandas as pd

    if not args.training_table.is_file():
        print(json.dumps({"error": f"missing training table: {args.training_table}"}, indent=2))
        return 1
    if not args.events.is_file():
        print(json.dumps({"error": f"missing events: {args.events}"}, indent=2))
        return 1

    table = pd.read_parquet(args.training_table)
    events = pd.read_parquet(args.events)
    event_ids = set(table["event_id"].astype(str))
    events = events[events["event_id"].astype(str).isin(event_ids)].reset_index(drop=True)

    assert_copernicus_env_credentials()
    days = unique_event_days_with_lags(events, lag_days=args.lag_days)
    batches = plan_glorys_subset_batches(days)
    enforce_subset_request_budget(batches)
    cfg = load_overlap_config()
    store = new_glorys_field_store_for_live_build(cfg)
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    log_path = REPO / str(cfg["pull_logs"]["glorys"])
    for batch in batches:
        _subset_batch_live(batch, args.cache_dir, log_path=log_path)
    populate_store_days_from_cache(store, days, batches, args.cache_dir)
    assert_store_ready_for_copernicus_export(store, days)

    lag_frame = attach_lagged_physics_columns(events, store, lag_days=args.lag_days)
    merged = table.merge(lag_frame, on="event_id", how="left", validate="many_to_one")
    lag_cols = required_lagged_columns(args.lag_days)
    complete = rows_with_complete_lags(merged, lag_cols)
    out = merged.loc[complete].reset_index(drop=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(args.output, index=False)

    summary = {
        "input_training_rows": int(len(table)),
        "events_with_lags_computed": int(len(lag_frame)),
        "lag_days": [int(x) for x in args.lag_days],
        "lag_columns": lag_cols,
        "rows_dropped_incomplete_lags": int((~complete).sum()),
        "output_rows": int(len(out)),
        "output_path": str(args.output),
        "events_path": str(args.events),
        "source_training_table": str(args.training_table),
        "glorys_days_loaded": len(days),
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
