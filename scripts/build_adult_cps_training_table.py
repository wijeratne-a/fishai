#!/usr/bin/env python3
"""Build adult CPS training table (trawl + nearshore catch × GLORYS covariates)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.adult.training_build import (
        DEFAULT_EVENTS_PATH,
        DEFAULT_TRAINING_TABLE_PATH,
        assemble_adult_observations,
        assemble_adult_physics_events,
        run_build_adult_cps_training_table,
    )
    from fishai.ingestion.physics.cufes_training_covariates import (
        _subset_batch_live,
        new_glorys_field_store_for_live_build,
        plan_glorys_subset_batches,
        populate_store_days_from_cache,
        unique_event_days,
    )
    from fishai.ingestion.physics.glorys_cufes_subset import enforce_subset_request_budget
    from fishai.ingestion.physics.glorys_training_build import (
        assert_copernicus_env_credentials,
        assert_store_ready_for_copernicus_export,
    )
    from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
    from fishai.ingestion.sources import REPO_ROOT as REPO

    parser = argparse.ArgumentParser(description="Build adult CPS × GLORYS training table")
    parser.add_argument("--dry-run", action="store_true", help="Row counts only; no GLORYS I/O")
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_TRAINING_TABLE_PATH)
    parser.add_argument("--trawl-hauls", type=Path, help="Override cps_trawl_hauls.parquet")
    parser.add_argument("--trawl-catch", type=Path, help="Override cps_trawl_catch.parquet")
    parser.add_argument("--trawl-specimens", type=Path, help="Override cps_trawl_specimens.parquet")
    parser.add_argument("--nearshore-sets", type=Path, help="Override cps_nearshore_sets.parquet")
    parser.add_argument("--nearshore-catch", type=Path, help="Override cps_nearshore_catch.parquet")
    parser.add_argument(
        "--nearshore-specimens",
        type=Path,
        help="Override cps_nearshore_specimens.parquet",
    )
    args = parser.parse_args(argv)

    import os

    from fishai.ingestion.physics.glorys_training_build import GlorysTrainingBuildError

    def _glorys_credentials_present() -> bool:
        return bool(
            os.environ.get("COPERNICUSMARINE_SERVICE_USERNAME")
            and os.environ.get("COPERNICUSMARINE_SERVICE_PASSWORD")
        )

    if args.dry_run:
        result = run_build_adult_cps_training_table(
            trawl_hauls_path=args.trawl_hauls,
            trawl_catch_path=args.trawl_catch,
            trawl_specimens_path=args.trawl_specimens,
            nearshore_sets_path=args.nearshore_sets,
            nearshore_catch_path=args.nearshore_catch,
            nearshore_specimens_path=args.nearshore_specimens,
            events_path=args.events,
            output_path=args.output,
            dry_run=True,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    observations, _ = assemble_adult_observations(
        trawl_catch_path=args.trawl_catch,
        nearshore_catch_path=args.nearshore_catch,
        trawl_specimens_path=args.trawl_specimens,
        nearshore_specimens_path=args.nearshore_specimens,
    )
    event_ids = set(observations["event_id"].astype(str)) if not observations.empty else set()
    events, _ = assemble_adult_physics_events(
        trawl_hauls_path=args.trawl_hauls,
        nearshore_sets_path=args.nearshore_sets,
        observation_event_ids=event_ids,
    )
    if events.empty:
        print(json.dumps({"error": "no adult physics events after QC"}, indent=2))
        return 1

    if not _glorys_credentials_present():
        result = run_build_adult_cps_training_table(
            trawl_hauls_path=args.trawl_hauls,
            trawl_catch_path=args.trawl_catch,
            trawl_specimens_path=args.trawl_specimens,
            nearshore_sets_path=args.nearshore_sets,
            nearshore_catch_path=args.nearshore_catch,
            nearshore_specimens_path=args.nearshore_specimens,
            events_path=args.events,
            output_path=args.output,
            store=None,
            dry_run=False,
        )
        result["glorys_join"] = "blocked_credentials_missing"
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    try:
        assert_copernicus_env_credentials()
    except GlorysTrainingBuildError as exc:
        result = run_build_adult_cps_training_table(
            trawl_hauls_path=args.trawl_hauls,
            trawl_catch_path=args.trawl_catch,
            trawl_specimens_path=args.trawl_specimens,
            nearshore_sets_path=args.nearshore_sets,
            nearshore_catch_path=args.nearshore_catch,
            nearshore_specimens_path=args.nearshore_specimens,
            events_path=args.events,
            output_path=args.output,
            store=None,
            dry_run=False,
        )
        result["glorys_join"] = "blocked_credentials_missing"
        result["glorys_block_reason"] = exc.reason_code
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    days = unique_event_days(events)
    batches = plan_glorys_subset_batches(days)
    enforce_subset_request_budget(batches)
    cfg = load_overlap_config()
    store = new_glorys_field_store_for_live_build(cfg)
    cache_dir = REPO / "data" / "cache" / "glorys_adult_cps"
    cache_dir.mkdir(parents=True, exist_ok=True)
    log_path = REPO / str(cfg["pull_logs"]["glorys"])
    for batch in batches:
        _subset_batch_live(batch, cache_dir, log_path=log_path)
    populate_store_days_from_cache(store, days, batches, cache_dir)
    assert_store_ready_for_copernicus_export(store, days)

    result = run_build_adult_cps_training_table(
        trawl_hauls_path=args.trawl_hauls,
        trawl_catch_path=args.trawl_catch,
        trawl_specimens_path=args.trawl_specimens,
        nearshore_sets_path=args.nearshore_sets,
        nearshore_catch_path=args.nearshore_catch,
        nearshore_specimens_path=args.nearshore_specimens,
        events_path=args.events,
        output_path=args.output,
        store=store,
        dry_run=False,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
