#!/usr/bin/env python3
"""Build Pacific herring all-sizes encounter training table (GCS domain × GLORYS)."""

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
        HERRING_BUILD_SUMMARY_PATH,
        HERRING_DROP_SUMMARY_PATH,
        HERRING_DROPS_PATH,
        HERRING_EVENTS_PATH,
        HERRING_NEARSHORE_CATCH_PATH,
        HERRING_NEARSHORE_SETS_PATH,
        HERRING_NEARSHORE_SPECIMENS_PATH,
        HERRING_TARGET_SPECIES,
        HERRING_TRAINING_TABLE_PATH,
        HERRING_TRAWL_CATCH_PATH,
        HERRING_TRAWL_HAULS_PATH,
        HERRING_TRAWL_SPECIMENS_PATH,
    )
    from fishai.ingestion.adult.training_build import (
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
        GlorysTrainingBuildError,
        assert_copernicus_env_credentials,
        assert_store_ready_for_copernicus_export,
    )
    from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
    from fishai.ingestion.sources import REPO_ROOT as REPO  # noqa: N811

    parser = argparse.ArgumentParser(
        description="Build Pacific herring all-sizes encounter training table"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    domain = json.loads(
        (REPO_ROOT / "config" / "adult_pacific_herring_domain.json").read_text(encoding="utf-8")
    )
    box = domain["bbox"]
    bbox = (
        float(box["lat_min"]),
        float(box["lat_max"]),
        float(box["lon_min"]),
        float(box["lon_max"]),
    )

    if args.dry_run:
        result = run_build_adult_cps_training_table(
            trawl_hauls_path=HERRING_TRAWL_HAULS_PATH,
            trawl_catch_path=HERRING_TRAWL_CATCH_PATH,
            trawl_specimens_path=HERRING_TRAWL_SPECIMENS_PATH,
            nearshore_sets_path=HERRING_NEARSHORE_SETS_PATH,
            nearshore_catch_path=HERRING_NEARSHORE_CATCH_PATH,
            nearshore_specimens_path=HERRING_NEARSHORE_SPECIMENS_PATH,
            events_path=HERRING_EVENTS_PATH,
            output_path=HERRING_TRAINING_TABLE_PATH,
            dry_run=True,
            target_species=HERRING_TARGET_SPECIES,
            bbox=bbox,
            build_summary_path=HERRING_BUILD_SUMMARY_PATH,
            apply_length_gate=False,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    import os

    if not (
        os.environ.get("COPERNICUSMARINE_SERVICE_USERNAME")
        and os.environ.get("COPERNICUSMARINE_SERVICE_PASSWORD")
    ):
        print("BLOCKED: COPERNICUSMARINE_* credentials absent; cannot join GLORYS", file=sys.stderr)
        return 2

    observations, _ = assemble_adult_observations(
        trawl_catch_path=HERRING_TRAWL_CATCH_PATH,
        nearshore_catch_path=HERRING_NEARSHORE_CATCH_PATH,
        trawl_specimens_path=HERRING_TRAWL_SPECIMENS_PATH,
        nearshore_specimens_path=HERRING_NEARSHORE_SPECIMENS_PATH,
        target_species=HERRING_TARGET_SPECIES,
        apply_length_gate=False,
    )
    obs_ids = set(observations["event_id"].astype(str))
    events, _ = assemble_adult_physics_events(
        trawl_hauls_path=HERRING_TRAWL_HAULS_PATH,
        nearshore_sets_path=HERRING_NEARSHORE_SETS_PATH,
        observation_event_ids=obs_ids,
        bbox=bbox,
    )

    try:
        assert_copernicus_env_credentials()
    except GlorysTrainingBuildError as exc:
        print(json.dumps({"glorys_join": "blocked", "reason": exc.reason_code}, indent=2))
        return 2

    days = unique_event_days(events)
    batches = plan_glorys_subset_batches(days)
    enforce_subset_request_budget(batches)
    overlap_cfg = load_overlap_config()
    store = new_glorys_field_store_for_live_build(overlap_cfg)
    cache_dir = REPO / "data" / "cache" / "glorys_adult_herring"
    cache_dir.mkdir(parents=True, exist_ok=True)
    log_path = REPO / str(overlap_cfg["pull_logs"]["glorys"])
    for batch in batches:
        _subset_batch_live(batch, cache_dir, log_path=log_path)
    populate_store_days_from_cache(store, days, batches, cache_dir)
    assert_store_ready_for_copernicus_export(store, days)

    build_result = run_build_adult_cps_training_table(
        trawl_hauls_path=HERRING_TRAWL_HAULS_PATH,
        trawl_catch_path=HERRING_TRAWL_CATCH_PATH,
        trawl_specimens_path=HERRING_TRAWL_SPECIMENS_PATH,
        nearshore_sets_path=HERRING_NEARSHORE_SETS_PATH,
        nearshore_catch_path=HERRING_NEARSHORE_CATCH_PATH,
        nearshore_specimens_path=HERRING_NEARSHORE_SPECIMENS_PATH,
        events_path=HERRING_EVENTS_PATH,
        output_path=HERRING_TRAINING_TABLE_PATH,
        drops_parquet_path=HERRING_DROPS_PATH,
        drop_summary_json_path=HERRING_DROP_SUMMARY_PATH,
        build_summary_path=HERRING_BUILD_SUMMARY_PATH,
        target_species=HERRING_TARGET_SPECIES,
        bbox=bbox,
        dry_run=False,
        events=events,
        observations=observations,
        store=store,
        apply_length_gate=False,
    )
    table = build_result.get("table")
    print(
        json.dumps(
            {
                "training_rows": int(len(table)) if table is not None else None,
                "encounter_1": int((table["encounter"] == 1).sum())
                if table is not None and "encounter" in table.columns
                else None,
                "qc": build_result.get("qc"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
