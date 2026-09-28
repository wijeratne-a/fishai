#!/usr/bin/env python3
"""Validate Atlantic RVC event frames. Prints aggregates only."""

from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FILES = []


def florida_files():
    raw = ROOT / "data/raw/biological"
    for path in sorted(raw.glob("noaa-rvc-florida-keys-*.csv.gz")):
        year = int(path.name.split("-")[-1].split(".")[0])
        yield "Florida Keys", year, "CRCP_Reef_Fish_Surveys_Florida", path, "YEAR", "NUM", "SPECIES_CD"


def ncrmp_files():
    base = ROOT / "data/raw/biological/noaa-ncrmp"
    mapping = {
        "CRCP_Reef_Fish_Surveys_Puerto_Rico": "Puerto Rico",
        "CRCP_Reef_Fish_Surveys_USVI": "USVI",
        "CRCP_Reef_Fish_Surveys_Flower_Gardens": "Flower Garden Banks",
    }
    for dataset, region in mapping.items():
        folder = base / dataset
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.csv.gz")):
            year = int(path.stem.split(".")[0])
            yield region, year, dataset, path, "YEAR", "NUM", "SPECIES_CD"


def summarize(region, year, dataset, path, year_field, num_field, code_field):
    events = {}
    zeros = positives = 0
    accessions = set()
    both = multi = 0
    with gzip.open(path, "rt", encoding="latin-1", newline="") as handle:
        reader = csv.DictReader(handle)
        first = True
        for row in reader:
            if first and not (row.get(year_field) or "").strip():
                first = False
                continue
            first = False
            key = (
                (row.get("PRIMARY_SAMPLE_UNIT") or "").strip(),
                (row.get("STATION_NR") or "").strip(),
                (row.get("time") or "").strip(),
            )
            code = (row.get(code_field) or "").strip() or "BLANK"
            num = float(row[num_field])
            if num == 0:
                zeros += 1
                flag = "z"
            elif num > 0:
                positives += 1
                flag = "p"
            else:
                flag = "n"
            accessions.add((row.get("accession_url") or "").strip())
            rec = events.setdefault(key, {"codes": set(), "sp": defaultdict(lambda: {"z": 0, "p": 0}), "meta": set()})
            rec["codes"].add(code)
            rec["sp"][code][flag] += 1
            rec["meta"].add(((row.get("MONTH") or "").strip(), (row.get("DAY") or "").strip(), (row.get("DEPTH") or row.get("SAMPLE_DEPTH") or "").strip(), (row.get("HABITAT_CD") or "").strip()))
    clashes = sum(1 for rec in events.values() if len(rec["meta"]) > 1)
    for rec in events.values():
        for counts in rec["sp"].values():
            if counts["z"] and counts["p"]:
                both += 1
            if counts["z"] + counts["p"] > 1:
                multi += 1
    universes = {frozenset(rec["codes"]) for rec in events.values()}
    sizes = [len(rec["codes"]) for rec in events.values()]
    status = "MODEL_READY_WITH_RESTRICTIONS"
    if clashes:
        status = "EVENT_KEY_UNRESOLVED"
    elif len(universes) != 1 or zeros == 0:
        status = "ZERO_SEMANTICS_UNRESOLVED"
    return {
        "region": region,
        "year": year,
        "dataset": dataset,
        "events": len(events),
        "zero_rows": zeros,
        "positive_rows": positives,
        "species_list_size": sizes[0] if sizes and min(sizes) == max(sizes) else None,
        "universes": len(universes),
        "metadata_collisions": clashes,
        "species_events_mixed_zero_and_positive": both,
        "species_events_multi_row": multi,
        "accessions": sorted(a for a in accessions if a),
        "status": status,
    }


def main() -> None:
    reports = []
    for item in list(florida_files()) + list(ncrmp_files()):
        reports.append(summarize(*item))
    json.dump(reports, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
