#!/usr/bin/env python3
"""Build market squid CPS encounter × GLORYS table (all sizes; not an adult model)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

SQUID_EVENTS = REPO_ROOT / "data" / "processed" / "adult_cps" / "market_squid_encounter_events.parquet"
SQUID_TABLE = REPO_ROOT / "data" / "processed" / "adult_cps" / "market_squid_encounter_training_table.parquet"
SQUID_SUMMARY = REPO_ROOT / "data" / "processed" / "adult_cps" / "market_squid_encounter_build_summary.json"


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.adult.constants import NEARSHORE_CATCH_PATH, TRAWL_CATCH_PATH
    from fishai.ingestion.adult.squid_encounter import assemble_market_squid_encounter_observations
    from fishai.ingestion.adult.training_build import (
        assemble_adult_physics_events,
        build_adult_cps_training_table,
    )

    parser = argparse.ArgumentParser(description="Market squid encounter training table (no length gate)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--events-out", type=Path, default=SQUID_EVENTS)
    parser.add_argument("--table-out", type=Path, default=SQUID_TABLE)
    args = parser.parse_args(argv)

    import pandas as pd

    trawl_catch = pd.read_parquet(TRAWL_CATCH_PATH)
    near_catch = pd.read_parquet(NEARSHORE_CATCH_PATH)
    observations, obs_summary = assemble_market_squid_encounter_observations(
        trawl_catch=trawl_catch,
        nearshore_catch=near_catch,
    )
    event_ids = set(observations["event_id"].astype(str))
    events, bbox_drops = assemble_adult_physics_events(observation_event_ids=event_ids)

    summary = {
        "observations": obs_summary,
        "physics_events": len(events),
        "bbox_drops": int(len(bbox_drops)),
    }

    if args.dry_run:
        summary["dry_run"] = True
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    import os

    from fishai.ingestion.physics.cufes_training_covariates import (
        _subset_batch_live,
        new_glorys_field_store_for_live_build,
        plan_glorys_subset_batches,
        populate_store_days_from_cache,
        unique_event_days,
    )
    from fishai.ingestion.physics.glorys_cufes_subset import enforce_subset_request_budget
    from fishai.ingestion.physics.glorys_training_build import (
        GlorysTrainingBuildError,
        assert_copernicus_env_credentials,
        assert_store_ready_for_copernicus_export,
    )
    from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config

    if not (
        os.environ.get("COPERNICUSMARINE_SERVICE_USERNAME")
        and os.environ.get("COPERNICUSMARINE_SERVICE_PASSWORD")
    ):
        print("blocked: COPERNICUSMARINE_* env vars absent", file=sys.stderr)
        return 2

    args.events_out.parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(args.events_out, index=False)

    cfg = load_overlap_config()
    days = unique_event_days(events)
    batches = plan_glorys_subset_batches(days)
    enforce_subset_request_budget(batches)
    store = new_glorys_field_store_for_live_build(cfg)
    cache_dir = REPO_ROOT / "data" / "cache" / "glorys_market_squid_encounter"
    cache_dir.mkdir(parents=True, exist_ok=True)
    log_path = REPO_ROOT / str(cfg["pull_logs"]["glorys"])
    assert_copernicus_env_credentials()
    for batch in batches:
        _subset_batch_live(batch, cache_dir, log_path=log_path)
    populate_store_days_from_cache(store, days, batches, cache_dir)
    assert_store_ready_for_copernicus_export(store, days)

    table, qc, drops = build_adult_cps_training_table(events, observations, store)
    args.table_out.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(args.table_out, index=False)
    summary["glorys_qc"] = qc
    summary["training_rows"] = int(len(table))
    SQUID_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
