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
    ds = fetch_cycle(run_date, leads, bbox)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    zarr_path = out / f"wcofs_{run_date:%Y%m%d}.zarr"
    ds.to_zarr(zarr_path, mode="w", consolidated=False)
    print(f"wrote {zarr_path}")
    return 0


def cmd_hindcast(args: argparse.Namespace) -> int:
    print("hindcast: use daily over a date range (orchestrator not bundled in pilot)", file=sys.stderr)
    return 1


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
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
