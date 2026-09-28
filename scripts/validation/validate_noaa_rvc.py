#!/usr/bin/env python3
"""Validate downloaded Florida Keys RVC gzip tables. Prints aggregates only."""

from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "biological"
EXPECTED = {
    2018: "https://www.ncei.noaa.gov/archive/accession/0208321",
    2022: "https://www.ncei.noaa.gov/archive/accession/0282183",
    2024: "https://www.ncei.noaa.gov/archive/accession/0306184",
}


def validate(year: int) -> dict:
    path = RAW / f"noaa-rvc-florida-keys-{year}.csv.gz"
    events: dict[tuple, dict] = {}
    stats = Counter()
    accessions: set[str] = set()
    with gzip.open(path, "rt", encoding="latin-1", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "time", "latitude", "longitude", "PRIMARY_SAMPLE_UNIT", "YEAR", "MONTH", "DAY",
            "STATION_NR", "DEPTH", "NUM", "SPECIES_CD", "REGION", "accession_url",
        }
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise SystemExit(f"{year} missing columns {missing}")
        first = True
        for row in reader:
            if first and (row.get("YEAR") or "").strip() == "":
                first = False
                stats["units_row"] += 1
                continue
            first = False
            stats["rows"] += 1
            if (row.get("YEAR") or "").strip() != str(year):
                stats["bad_year"] += 1
            if (row.get("REGION") or "").strip() != "FLA KEYS":
                stats["bad_region"] += 1
            try:
                int(row["MONTH"])
                int(row["DAY"])
            except ValueError:
                stats["bad_date"] += 1
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                if not (24.0 <= lat <= 26.5 and -83.5 <= lon <= -79.5):
                    stats["coord_out_of_box"] += 1
            except ValueError:
                stats["coord_out_of_box"] += 1
            depth = (row.get("DEPTH") or "").strip()
            if depth == "":
                stats["depth_missing"] += 1
            else:
                try:
                    if float(depth) < 0:
                        stats["depth_negative"] += 1
                except ValueError:
                    stats["depth_negative"] += 1
            try:
                num = float(row["NUM"])
            except ValueError:
                stats["num_non_numeric"] += 1
                continue
            if num < 0:
                stats["num_negative"] += 1
            elif num == 0:
                stats["num_zero"] += 1
            else:
                stats["num_positive"] += 1
            if not (row.get("SCIENTIFIC_NAME") or "").strip():
                stats["blank_scientific_name"] += 1
            accessions.add((row.get("accession_url") or "").strip())
            key = (
                (row.get("YEAR") or "").strip(),
                (row.get("PRIMARY_SAMPLE_UNIT") or "").strip(),
                (row.get("STATION_NR") or "").strip(),
                (row.get("time") or "").strip(),
            )
            code = (row.get("SPECIES_CD") or "").strip() or "BLANK"
            rec = events.setdefault(key, {"codes": set(), "meta": set()})
            rec["codes"].add(code)
            rec["meta"].add(
                (
                    (row.get("MONTH") or "").strip(),
                    (row.get("DAY") or "").strip(),
                    depth,
                    (row.get("HABITAT_CD") or "").strip(),
                    (row.get("SUB_REGION_NR") or "").strip(),
                    (row.get("STRAT") or "").strip(),
                )
            )
    universes = {frozenset(rec["codes"]) for rec in events.values()}
    meta_clashes = sum(1 for rec in events.values() if len(rec["meta"]) > 1)
    return {
        "year": year,
        "rows": stats["rows"],
        "events": len(events),
        "units_row": stats["units_row"],
        "bad_year": stats["bad_year"],
        "bad_region": stats["bad_region"],
        "bad_date": stats["bad_date"],
        "coord_out_of_box": stats["coord_out_of_box"],
        "depth_missing": stats["depth_missing"],
        "depth_negative": stats["depth_negative"],
        "num_zero": stats["num_zero"],
        "num_positive": stats["num_positive"],
        "num_negative": stats["num_negative"],
        "blank_scientific_name": stats["blank_scientific_name"],
        "species_universes": len(universes),
        "universe_size": len(next(iter(universes))) if len(universes) == 1 else None,
        "event_key_metadata_collisions": meta_clashes,
        "accession_ok": accessions == {EXPECTED[year]},
        "accessions": sorted(accessions),
    }


def main() -> None:
    reports = [validate(year) for year in EXPECTED]
    json.dump(reports, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if any(item["event_key_metadata_collisions"] or not item["accession_ok"] for item in reports):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
