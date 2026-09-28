"""``fishai-physics`` CLI: daily and hindcast physics ingestion."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from fishai.ingestion.sources import load_sources_manifest

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = REPO_ROOT / "data" / "processed" / "physics"


def _pilot_bbox(manifest: dict) -> tuple[float, float, float, float]:
    pilot = manifest.get("pilot") or {}
    bbox = pilot.get("bbox") or {}
    return (
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )


def cmd_daily(args: argparse.Namespace) -> int:
    from fishai.ingestion.physics.sources.wcofs import NOWCAST_LEADS, fetch_cycle

    manifest = load_sources_manifest()
    bbox = _pilot_bbox(manifest)
    run_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    leads = tuple(args.leads.split(",")) if args.leads else NOWCAST_LEADS[:1]
    from fishai.ingestion.physics.wcofs_store import write_wcofs_cycle

    ds = fetch_cycle(run_date, leads, bbox)
    out = Path(args.output)
    zarr_path = write_wcofs_cycle(ds, run_date, out)
    print(f"wrote {zarr_path}")
    return 0


def cmd_hindcast(args: argparse.Namespace) -> int:
    print("hindcast: use daily over a date range (orchestrator not bundled in pilot)", file=sys.stderr)
    return 1


def cmd_build_cufes_training_covariates(args: argparse.Namespace) -> int:
    from fishai.ingestion.physics.cufes_training_covariates import (
        DEFAULT_EVENTS_PATH,
        DEFAULT_OUTPUT_PATH,
        run_build_cufes_training_covariates,
    )

    events_path = Path(args.events) if args.events else DEFAULT_EVENTS_PATH
    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT_PATH
    result = run_build_cufes_training_covariates(
        events_path=events_path,
        output_path=output_path,
        dry_run=bool(args.dry_run),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-physics", description="Physics ingestion")
    sub = parser.add_subparsers(dest="command", required=True)
    p_daily = sub.add_parser("daily", help="Fetch WCOFS daily cycle subset for pilot bbox")
    p_daily.add_argument("--date", help="Cycle date YYYY-MM-DD (default: today UTC)")
    p_daily.add_argument("--leads", help="Comma-separated leads e.g. n003,n024")
    p_daily.add_argument("--output", default=str(DEFAULT_OUT))
    p_daily.set_defaults(func=cmd_daily)
    p_hind = sub.add_parser("hindcast", help="Historical physics backfill (stub)")
    p_hind.set_defaults(func=cmd_hindcast)
    p_cufes = sub.add_parser(
        "build-cufes-training-covariates",
        help="Match Copernicus GLORYS covariates to QC-kept CUFES events (event_id join)",
    )
    p_cufes.add_argument(
        "--events",
        help="Input cufes_events.parquet (default: data/processed/calcofi_cufes/cufes_events.parquet)",
    )
    p_cufes.add_argument("--output", help="Output training covariates parquet path")
    p_cufes.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned Copernicus subset batches and request count only",
    )
    p_cufes.set_defaults(func=cmd_build_cufes_training_covariates)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
