"""CLI entrypoints for pilot ingestion and modeling."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from fishai.ingestion.sensors.internal.config import load_sensors_config, pilot_bbox
from fishai.ingestion.sensors.internal.consistency import score_cycle
from fishai.ingestion.sensors.internal.holdout import score_holdout
from fishai.ingestion.sensors.internal.model_loader import load_wcofs_cycle
from fishai.ingestion.sensors.sources.hfradar import fetch_hfr_sync_window
from fishai.ingestion.sensors.sources.ndbc import fetch_ndbc
from fishai.ingestion.sensors.sources.gliders import fetch_profiles, list_active
from fishai.ingestion.sensors.internal.sync import parse_since, run_sync
from fishai.ingestion.sources import require_approved


def _not_implemented(name: str) -> int:
    print(f"{name}: not implemented", file=sys.stderr)
    return 1


def main_bio(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-bio", description="Biology ingestion (CalCOFI CUFES)")
    parser.parse_args(argv)
    return _not_implemented("fishai-bio")


def main_physics(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-physics", description="Physics ingestion (WCOFS/GLORYS)")
    parser.parse_args(argv)
    return _not_implemented("fishai-physics")


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
        bbox = pilot_bbox(cfg)
        since = parse_since("7d")
        active = list_active(bbox, since)
        frames = [fetch_profiles(ds, since, datetime.now(timezone.utc)) for ds in active]
        import pandas as pd

        profiles = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        scores = score_holdout(model, profiles, cfg=cfg)
        print(scores.to_json(orient="records", indent=2))
        return 0

    return 1


def main_models(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-models", description="sdmTMB modeling wrapper")
    parser.parse_args(argv)
    return _not_implemented("fishai-models")
