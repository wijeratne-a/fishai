"""``fishai-physics`` CLI: daily and hindcast physics ingestion."""

from __future__ import annotations

import argparse
import datetime as dt
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


def cmd_wcofs_daily(args: argparse.Namespace) -> int:
    from fishai.ingestion.physics.wcofs_daily import run_wcofs_daily

    run_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    out = Path(args.out)
    plan = run_wcofs_daily(
        run_date,
        out_root=out,
        dry_run=args.dry_run,
        wait_for_cycle=not args.no_wait,
        provenance_dir=Path(args.provenance_dir) if args.provenance_dir else None,
    )
    if args.dry_run:
        print(f"target_cycle={plan.target_date.isoformat()} primary_available={plan.primary_available}")
        print(f"requests={plan.request_count}")
        for key in plan.s3_keys:
            print(key)
        if plan.zarr_path:
            print(f"zarr={plan.zarr_path}")
        if plan.pull_log:
            print(f"pull_log={plan.pull_log}")
        if plan.qc_report_path:
            print(f"qc_report={plan.qc_report_path}")
        if plan.unknown_leads:
            print(f"unknown={plan.unknown_leads}")
        return 0
    print(f"wrote {plan.zarr_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-physics", description="Physics ingestion")
    sub = parser.add_subparsers(dest="command", required=True)
    p_daily = sub.add_parser("daily", help="Fetch WCOFS daily cycle subset for pilot bbox")
    p_daily.add_argument("--date", help="Cycle date YYYY-MM-DD (default: today UTC)")
    p_daily.add_argument("--leads", help="Comma-separated leads e.g. n003,n024")
    p_daily.add_argument("--output", default=str(DEFAULT_OUT))
    p_daily.set_defaults(func=cmd_daily)
    p_wdaily = sub.add_parser("wcofs-daily", help="Operational WCOFS daily pull (nowcast+72h forecast)")
    p_wdaily.add_argument("--date", help="Target cycle date YYYY-MM-DD (default: today UTC)")
    p_wdaily.add_argument("--out", default=str(DEFAULT_OUT), help="Processed physics store root")
    p_wdaily.add_argument(
        "--provenance-dir",
        help="Pull log directory (default: data/provenance for pilot out, else <out>/provenance)",
    )
    p_wdaily.add_argument("--dry-run", action="store_true", help="List S3 keys and outputs only")
    p_wdaily.add_argument(
        "--no-wait",
        action="store_true",
        help="Do not retry for same-day t03z cycle (use fallback immediately)",
    )
    p_wdaily.set_defaults(func=cmd_wcofs_daily)
    p_hind = sub.add_parser("hindcast", help="Historical physics backfill (stub)")
    p_hind.set_defaults(func=cmd_hindcast)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
