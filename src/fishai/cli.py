"""CLI entrypoints for pilot ingestion and modeling."""

from __future__ import annotations

import argparse
import sys
from datetime import date


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
    parser = argparse.ArgumentParser(prog="fishai-physics", description="Physics ingestion (WCOFS/GLORYS)")
    parser.parse_args(argv)
    return _not_implemented("fishai-physics")


def main_sensors(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-sensors", description="Sensor consistency ingestion")
    parser.parse_args(argv)
    return _not_implemented("fishai-sensors")


def main_models(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-models", description="sdmTMB modeling wrapper")
    parser.parse_args(argv)
    return _not_implemented("fishai-models")
