#!/usr/bin/env python3
"""Download CPS trawl and nearshore specimen ERDDAP tables into processed parquet."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pyarrow is required") from exc


def _load_odp_csv_rows(path: Path, mapping: dict[str, str]) -> list[dict]:
    import csv

    out: list[dict] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            out.append({mapping.get(k, k): v for k, v in row.items()})
    return out


def _load_odp_trawl_specimen_rows(path: Path) -> list[dict]:
    return _load_odp_csv_rows(
        path,
        {
            "Latitude": "latitude",
            "Longitude": "longitude",
            "Time": "time",
            "itisTSN": "itis_tsn",
            "scientificName": "scientific_name",
            "standardLength_mm": "standard_length",
            "forkLength_mm": "fork_length",
            "totalLength_mm": "total_length",
            "weightg": "weight",
        },
    )


def _load_odp_nearshore_specimen_rows(path: Path) -> list[dict]:
    return _load_odp_csv_rows(
        path,
        {
            "Latitude": "latitude",
            "Longitude": "longitude",
            "Time": "time",
            "itisTSN": "itis_tsn",
            "scientificName": "scientific_name",
            "standardLength_mm": "standard_length",
            "forkLength_mm": "fork_length",
            "totalLength_mm": "total_length",
            "weightg": "weight",
        },
    )


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.adult.constants import NEARSHORE_SPECIMENS_PATH, TRAWL_SPECIMENS_PATH
    from fishai.ingestion.adult.specimen_fetch import (
        fetch_nearshore_specimens,
        fetch_trawl_specimens,
        read_specimen_csv,
    )
    from fishai.ingestion.adult.specimens import (
        normalize_nearshore_specimens,
        normalize_trawl_specimens,
    )
    from fishai.ingestion.biology.cps_nearshore.pipeline import pilot_bbox_from_manifest as near_bbox
    from fishai.ingestion.biology.cps_trawl.pipeline import pilot_bbox_from_manifest as trawl_bbox

    parser = argparse.ArgumentParser(description="Fetch adult CPS specimen tables (public ERDDAP)")
    parser.add_argument("--trawl-start", type=date.fromisoformat, default=date(2003, 7, 9))
    parser.add_argument("--trawl-end", type=date.fromisoformat, default=date(2026, 12, 31))
    parser.add_argument("--nearshore-start", type=date.fromisoformat, default=date(2019, 6, 21))
    parser.add_argument("--nearshore-end", type=date.fromisoformat, default=date(2026, 12, 31))
    parser.add_argument(
        "--nearshore-half-year",
        action="store_true",
        help="Use six-month ERDDAP windows (oceanview mirror fallback)",
    )
    parser.add_argument("--skip-trawl", action="store_true")
    parser.add_argument("--skip-nearshore", action="store_true")
    parser.add_argument(
        "--odp-bulk",
        action="store_true",
        help="Load SWFSC ODP bulk CSVs from data/raw (no ERDDAP)",
    )
    args = parser.parse_args(argv)

    bbox = trawl_bbox()
    trawl_rows: list[dict] = []
    near_rows: list[dict] = []

    if not args.skip_trawl:
        raw_trawl = REPO_ROOT / "data" / "raw" / "swfsc_cps_trawl_haul_catch" / "specimens"
        if args.odp_bulk:
            odp = raw_trawl / "CPS_Trawl_LifeHistory_Specimen.csv"
            if not odp.is_file():
                raise SystemExit(f"missing ODP trawl specimen CSV: {odp}")
            trawl_rows.extend(_load_odp_trawl_specimen_rows(odp))
        else:
            files = fetch_trawl_specimens(args.trawl_start, args.trawl_end, bbox, dest_dir=raw_trawl)
            for path in sorted(files):
                chunk, _ = read_specimen_csv(path)
                trawl_rows.extend(chunk)
        trawl_df = normalize_trawl_specimens(trawl_rows)
        TRAWL_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.Table.from_pandas(trawl_df), TRAWL_SPECIMENS_PATH)
        print(f"trawl_specimens rows={len(trawl_df)} path={TRAWL_SPECIMENS_PATH}")

    if not args.skip_nearshore:
        raw_near = REPO_ROOT / "data" / "raw" / "swfsc_cps_nearshore_set_catch" / "specimens"
        if args.odp_bulk:
            odp = raw_near / "CPS_Trawl_LifeHistory_Nearshore_Specimen.csv"
            if not odp.is_file():
                raise SystemExit(f"missing ODP nearshore specimen CSV: {odp}")
            near_rows.extend(_load_odp_nearshore_specimen_rows(odp))
        else:
            files = fetch_nearshore_specimens(
                args.nearshore_start,
                args.nearshore_end,
                near_bbox(),
                dest_dir=raw_near,
                half_year=args.nearshore_half_year,
            )
            for path in sorted(files):
                chunk, _ = read_specimen_csv(path)
                near_rows.extend(chunk)
        near_df = normalize_nearshore_specimens(near_rows)
        NEARSHORE_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.Table.from_pandas(near_df), NEARSHORE_SPECIMENS_PATH)
        print(f"nearshore_specimens rows={len(near_df)} path={NEARSHORE_SPECIMENS_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
