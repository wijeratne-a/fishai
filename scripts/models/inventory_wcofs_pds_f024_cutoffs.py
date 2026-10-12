#!/usr/bin/env python3
"""List public PDS f024 objects for rolling-origin cutoff days (jack mackerel 24h)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

PDS_ARCHIVE_START = dt.date(2024, 7, 1)
DEFAULT_CUTOFFS = (
    "2013-04-26",
    "2013-06-10",
    "2016-09-08",
    "2018-09-20",
    "2021-04-02",
    "2022-09-23",
    "2024-07-29",
    "2026-06-25",
)


def resolve_f024_pds(day: dt.date, list_keys) -> dict:
    from fishai.ingestion.physics.wcofs_pds_store import (
        CycleNotAvailable,
        _s3_url,
        layout_prefixes,
        resolve_fields_key,
    )

    lead = "f024"
    try:
        key = resolve_fields_key(day, lead, list_keys)
        return {
            "cutoff": day.isoformat(),
            "available": True,
            "product": "fields",
            "s3_key": key,
            "url": _s3_url(key),
        }
    except CycleNotAvailable:
        pass
    ymd = day.strftime("%Y%m%d")
    bases = {
        f"wcofs.t03z.{ymd}.regulargrid.{lead}.nc",
        f"nos.wcofs.regulargrid.{lead}.{ymd}.t03z.nc",
    }
    matches: list[str] = []
    for prefix in layout_prefixes(day):
        for key in list_keys(prefix):
            if key.rsplit("/", 1)[-1] in bases:
                matches.append(key)
    unique = sorted(set(matches))
    if len(unique) == 1:
        return {
            "cutoff": day.isoformat(),
            "available": True,
            "product": "regulargrid",
            "s3_key": unique[0],
            "url": _s3_url(unique[0]),
        }
    if not unique:
        return {
            "cutoff": day.isoformat(),
            "available": False,
            "product": None,
            "s3_key": None,
            "url": None,
            "reason": "no_pds_f024",
        }
    return {
        "cutoff": day.isoformat(),
        "available": False,
        "product": "ambiguous",
        "s3_key": unique,
        "url": None,
        "reason": "ambiguous_pds_f024",
    }


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix
    from fishai.ingestion.physics.wcofs_pds_store import WCOFS_PDS_BUCKET

    parser = argparse.ArgumentParser(description="Inventory PDS f024 for forecast cutoffs")
    parser.add_argument("--cutoffs", nargs="*", default=list(DEFAULT_CUTOFFS))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    rows = [resolve_f024_pds(dt.date.fromisoformat(c), list_keys_under_prefix) for c in args.cutoffs]
    covered = [r for r in rows if r.get("available")]
    payload = {
        "bucket": WCOFS_PDS_BUCKET,
        "pds_archive_start": PDS_ARCHIVE_START.isoformat(),
        "lead": "f024",
        "cycle": "t03z",
        "cutoffs": rows,
        "cutoffs_with_f024": [r["cutoff"] for r in covered],
        "n_cutoffs_with_f024": len(covered),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
