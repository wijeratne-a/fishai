"""CLI entrypoints for pilot ingestion and modeling."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone

from fishai.ingestion.sensors.internal.config import load_sensors_config, pilot_bbox
from fishai.ingestion.sensors.internal.consistency import score_cycle
from fishai.ingestion.sensors.internal.holdout import score_holdout
from fishai.ingestion.sensors.internal.model_loader import load_wcofs_cycle
from fishai.ingestion.sensors.internal.sync import parse_since, run_sync
from fishai.ingestion.sensors.sources.gliders import fetch_profiles, list_active
from fishai.ingestion.sensors.sources.hfradar import fetch_hfr_sync_window
from fishai.ingestion.sensors.sources.ndbc import fetch_ndbc
from fishai.ingestion.sources import require_approved


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid date: {value}") from exc


def _not_implemented(name: str) -> int:
    print(f"{name}: not implemented", file=sys.stderr)
    return 1


def main_bio(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-bio", description="Biology ingestion (CalCOFI CUFES)")
    sub = parser.add_subparsers(dest="command")

    sync = sub.add_parser("sync", help="Sync a biology source into data/processed/")
    sync_sub = sync.add_subparsers(dest="source")
    cufes = sync_sub.add_parser("cufes", help="CalCOFI CUFES egg counts (ERDDAP)")
    cufes.add_argument("--start", required=True, type=_parse_date, help="Start date (YYYY-MM-DD, inclusive)")
    cufes.add_argument("--end", required=True, type=_parse_date, help="End date (YYYY-MM-DD, inclusive)")
    cufes.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip ERDDAP download; process existing raw CSV under data/raw/calcofi_cufes/",
    )
    cufes.add_argument("--dwc", action="store_true", help="Also write Darwin Core text files")

    args = parser.parse_args(argv)
    if args.command == "sync" and args.source == "cufes":
        from fishai.ingestion.biology.cufes import format_qc_summary, sync_cufes

        result = sync_cufes(
            args.start,
            args.end,
            fetch=not args.no_fetch,
            write_dwc=args.dwc,
        )
        print(
            f"cufes sync: events={result['n_events']} "
            f"occurrence_rows={result['n_occurrence_rows']} "
            f"→ {result['events_path']}"
        )
        print(format_qc_summary(result["qc_report"]))
        print(f"qc report → {result['qc_report_path']}")
        return 0

    parser.print_help(file=sys.stderr)
    return 1 if argv is not None else _not_implemented("fishai-bio")


def main_physics(argv: list[str] | None = None) -> int:
    from fishai.ingestion.physics.cli import main as physics_main

    return physics_main(argv)


def main_sensors(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-sensors", description="Sensor consistency ingestion")
    sub = parser.add_subparsers(dest="command", required=True)

    sync_p = sub.add_parser("sync", help="Pull HF radar, NDBC, and gliders into local archive")
    sync_p.add_argument("--since", default="24h", help="Lookback for tabular sources (e.g. 24h, 7d)")

    cons_p = sub.add_parser("consistency", help="Score WCOFS vs radar and buoy SST for a cycle")
    cons_p.add_argument("--cycle", required=True, help="WCOFS cycle UTC date YYYYMMDD")

    hold_p = sub.add_parser("holdout", help="Score WCOFS vs glider subsurface profiles")
    hold_p.add_argument("--cycle", required=True, help="WCOFS cycle UTC date YYYYMMDD")

    args = parser.parse_args(argv)
    cfg = load_sensors_config()

    if args.command == "sync":
        report = run_sync(since=args.since)
        print(json.dumps(report, indent=2, default=str))
        return 0

    if args.command == "consistency":
        require_approved("sccoos_hfr")
        require_approved("ndbc_met")
        model = load_wcofs_cycle(args.cycle)
        if model is None:
            print(json.dumps({"skipped": True, "cycle": args.cycle, "reason": "CycleNotAvailable"}))
            return 0
        bbox = pilot_bbox(cfg)
        hfr = fetch_hfr_sync_window(bbox)
        since = parse_since("24h")
        ndbc = fetch_ndbc(since, datetime.now(timezone.utc), bbox, None)
        scores = score_cycle(model, {"hfr": hfr, "ndbc": ndbc}, cfg=cfg)
        print(scores.to_json(orient="records", indent=2))
        return 0

    if args.command == "holdout":
        try:
            require_approved("ioos_glider_dac")
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        model = load_wcofs_cycle(args.cycle)
        if model is None:
            print(json.dumps({"skipped": True, "cycle": args.cycle, "reason": "CycleNotAvailable"}))
            return 0
        bbox = pilot_bbox(cfg)
        since = parse_since("7d")
        active = list_active(bbox, since)
        import pandas as pd

        frames = [fetch_profiles(ds, since, datetime.now(timezone.utc)) for ds in active]
        profiles = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        scores = score_holdout(model, profiles, cfg=cfg)
        print(scores.to_json(orient="records", indent=2))
        return 0

    return 1


def main_models(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-models", description="sdmTMB modeling wrapper")
    parser.parse_args(argv)
    return _not_implemented("fishai-models")
