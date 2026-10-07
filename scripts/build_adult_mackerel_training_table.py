#!/usr/bin/env python3
"""Build Pacific mackerel adult training table (single-species CPS × GLORYS)."""

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
        MACKEREL_EVENTS_PATH,
        MACKEREL_PROCESSED_DIR,
        MACKEREL_SCIENTIFIC_NAME,
        MACKEREL_TRAINING_TABLE_PATH,
    )
    from fishai.ingestion.adult.training_build import run_build_adult_cps_training_table
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
    from fishai.ingestion.sources import REPO_ROOT as REPO

    parser = argparse.ArgumentParser(
        description="Build Pacific mackerel CPS training table (encounter labels; optional all-sizes)"
    )
    parser.add_argument(
        "--all-sizes",
        action="store_true",
        help="Include all length classes (no L50 length gate); still excludes presence-only hauls",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--events", type=Path, default=MACKEREL_EVENTS_PATH)
    parser.add_argument("--output", type=Path, default=MACKEREL_TRAINING_TABLE_PATH)
    args = parser.parse_args(argv)

    import os

    pilot = (MACKEREL_SCIENTIFIC_NAME,)
    apply_gate = not args.all_sizes
    MACKEREL_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    def _creds() -> bool:
        return bool(
            os.environ.get("COPERNICUSMARINE_SERVICE_USERNAME")
            and os.environ.get("COPERNICUSMARINE_SERVICE_PASSWORD")
        )

    if args.dry_run or not _creds():
        result = run_build_adult_cps_training_table(
            events_path=args.events,
            output_path=args.output,
            store=None,
            dry_run=args.dry_run,
            pilot_species=pilot,
            apply_adult_length_gate=apply_gate,
        )
        if not _creds() and not args.dry_run:
            result["glorys_join"] = "blocked_credentials_missing"
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    try:
        assert_copernicus_env_credentials()
    except GlorysTrainingBuildError as exc:
        result = run_build_adult_cps_training_table(
            events_path=args.events,
            output_path=args.output,
            store=None,
            dry_run=False,
            pilot_species=pilot,
            apply_adult_length_gate=apply_gate,
        )
        result["glorys_join"] = "blocked_credentials_missing"
        result["glorys_block_reason"] = exc.reason_code
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    observations, _ = __import__(
        "fishai.ingestion.adult.training_build", fromlist=["assemble_adult_observations"]
    ).assemble_adult_observations(
        pilot_species=pilot,
        apply_adult_length_gate=apply_gate,
    )
    event_ids = set(observations["event_id"].astype(str)) if not observations.empty else set()
    events, _ = __import__(
        "fishai.ingestion.adult.training_build", fromlist=["assemble_adult_physics_events"]
    ).assemble_adult_physics_events(observation_event_ids=event_ids)
    days = unique_event_days(events)
    batches = plan_glorys_subset_batches(days)
    enforce_subset_request_budget(batches)
    cfg = load_overlap_config()
    store = new_glorys_field_store_for_live_build(cfg)
    cache_dir = REPO / "data" / "cache" / "glorys_adult_mackerel"
    cache_dir.mkdir(parents=True, exist_ok=True)
    log_path = REPO / str(cfg["pull_logs"]["glorys"])
    for batch in batches:
        _subset_batch_live(batch, cache_dir, log_path=log_path)
    populate_store_days_from_cache(store, days, batches, cache_dir)
    assert_store_ready_for_copernicus_export(store, days)

    result = run_build_adult_cps_training_table(
        events_path=args.events,
        output_path=args.output,
        store=store,
        dry_run=False,
        pilot_species=pilot,
        apply_adult_length_gate=apply_gate,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
