#!/usr/bin/env python3
"""Test event frames and valid zeros for Milestone 2 programs.

Prints and writes aggregates only. No coordinate values.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "biological"
OUT = ROOT / "audit" / "surveys" / "STRUCTURED_PROGRAM_FRAMES.json"
MD = ROOT / "audit" / "surveys" / "STRUCTURED_PROGRAM_STATUS.md"


def open_text(path: Path):
    if path.suffix == ".gz" or path.name.endswith(".csv.gz"):
        return gzip.open(path, "rt", encoding="latin-1", newline="")
    return path.open("rt", encoding="latin-1", newline="")


def skip_units(row: dict) -> bool:
    first = next(iter(row.values()), "")
    joined = " ".join((v or "").lower() for v in list(row.values())[:4])
    return not (first or "").strip()[:1].isdigit() and any(
        tok in joined for tok in ("degrees", "unitless", "utc", "seconds since")
    )


def header_fields(path: Path) -> list[str]:
    with open_text(path) as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or [])


def count_rows(path: Path) -> int:
    with open_text(path) as handle:
        reader = csv.DictReader(handle)
        n = 0
        first = True
        for row in reader:
            if first and skip_units(row):
                first = False
                continue
            first = False
            n += 1
        return n


def atlantic_like(path: Path) -> dict:
    fields = {f.lower() for f in header_fields(path)}
    year_f = "YEAR" if "year" in fields else None
    num_f = "NUM" if "num" in fields else None
    code_f = "SPECIES_CD" if "species_cd" in fields else None
    if not (year_f and num_f and code_f):
        return {}
    events = {}
    zeros = positives = 0
    with open_text(path) as handle:
        reader = csv.DictReader(handle)
        first = True
        for row in reader:
            if first and skip_units(row):
                first = False
                continue
            first = False
            key = (
                (row.get("PRIMARY_SAMPLE_UNIT") or "").strip(),
                (row.get("STATION_NR") or "").strip(),
                (row.get("time") or "").strip(),
            )
            code = (row.get("SPECIES_CD") or "").strip()
            try:
                num = float(row.get("NUM") or "")
            except ValueError:
                continue
            if num == 0:
                zeros += 1
                flag = "z"
            elif num > 0:
                positives += 1
                flag = "p"
            else:
                continue
            rec = events.setdefault(key, {"codes": set(), "sp": defaultdict(lambda: {"z": 0, "p": 0})})
            rec["codes"].add(code)
            rec["sp"][code][flag] += 1
    universes = {frozenset(rec["codes"]) for rec in events.values()}
    # Length bins may mix 0 and >0 on one species-event. Collapse first:
    # any NUM>0 is detection; all-zero bins are constructed non-detection.
    mixed_after_collapse = 0
    species_zeros = 0
    for rec in events.values():
        for counts in rec["sp"].values():
            if counts["p"] == 0 and counts["z"] > 0:
                species_zeros += 1
    status = "VALID_ZEROS_AND_EVENTS"
    if not events or zeros == 0 or len(universes) != 1:
        status = "ZERO_OR_EVENT_UNRESOLVED"
    return {
        "events": len(events),
        "zero_rows": zeros,
        "positive_rows": positives,
        "universes": len(universes),
        "species_level_nondetections": species_zeros,
        "status": status,
    }


def generic_frame(path: Path, event_fields: list[str], value_field: str | None, taxon_field: str | None) -> dict:
    events = {}
    zeros = positives = 0
    with open_text(path) as handle:
        reader = csv.DictReader(handle)
        first = True
        for row in reader:
            if first and skip_units(row):
                first = False
                continue
            first = False
            key = tuple((row.get(f) or "").strip() for f in event_fields)
            if not any(key):
                continue
            rec = events.setdefault(key, {"n": 0, "taxa": set()})
            rec["n"] += 1
            if taxon_field and row.get(taxon_field):
                rec["taxa"].add((row.get(taxon_field) or "").strip())
            if value_field:
                raw = (row.get(value_field) or "").strip()
                try:
                    val = float(raw)
                except ValueError:
                    continue
                if val == 0:
                    zeros += 1
                elif val > 0:
                    positives += 1
    status = "EVENT_FRAME_PRESENT"
    if zeros > 0 and events:
        status = "VALID_ZEROS_AND_EVENTS"
    elif events and positives > 0 and zeros == 0:
        status = "EVENTS_WITHOUT_EXPLICIT_ZEROS"
    elif not events:
        status = "EVENT_KEY_UNRESOLVED"
    return {
        "events": len(events),
        "zero_rows": zeros,
        "positive_rows": positives,
        "status": status,
    }


def pick_field(fields: list[str], candidates: tuple[str, ...]) -> str | None:
    lower = {f.lower(): f for f in fields}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def inspect_path(path: Path, program: str, method: str, region: str, us: str) -> dict:
    fields = header_fields(path)
    base = {
        "program": program,
        "method": method,
        "region": region,
        "us_jurisdiction": us,
        "file": path.name,
        "columns": len(fields),
        "data_rows": count_rows(path),
    }
    atlantic = atlantic_like(path)
    if atlantic:
        base.update(atlantic)
        return base
    event = [
        f
        for f in (
            pick_field(fields, ("survey", "Survey", "MISSION")),
            pick_field(fields, ("haulno", "HaulNo", "Haul", "SETNO", "setno", "TOW", "tow_number", "order_occupied")),
            pick_field(fields, ("year", "Year", "YEAR")),
            pick_field(fields, ("cruise", "Cruise")),
            pick_field(fields, ("station", "Station", "STATION")),
            pick_field(fields, ("survey_id", "site_code", "survey_date", "block")),
        )
        if f
    ]
    value = pick_field(
        fields,
        ("HLNoAtLngt", "TotalNo", "TOTNO", "TOTWGT", "NUMBER_CAUGHT", "count", "std_count", "abundance", "total"),
    )
    taxon = pick_field(
        fields,
        ("ScientificName", "scientific_name", "SPECCODE", "Species", "species", "CODE", "aphia"),
    )
    if event:
        extra = generic_frame(path, event, value, taxon)
        base.update(extra)
        base["event_fields"] = event
        base["value_field"] = value
        base["taxon_field"] = taxon
        return base
    base["status"] = "HEADER_ONLY_OR_UNPARSED"
    return base


def collect() -> list[dict]:
    reports: list[dict] = []
    mapping = [
        (RAW / "noaa-ncrmp" / "CRCP_Reef_Fish_Surveys_Puerto_Rico", "NCRMP_RVC", "reef_visual_census", "Puerto Rico", "yes"),
        (RAW / "noaa-ncrmp" / "CRCP_Reef_Fish_Surveys_USVI", "NCRMP_RVC", "reef_visual_census", "USVI", "yes"),
        (RAW / "noaa-ncrmp" / "CRCP_Reef_Fish_Surveys_Flower_Gardens", "NCRMP_RVC", "reef_visual_census", "Flower Garden Banks", "yes"),
        (RAW / "calcofi", "CalCOFI", "ichthyoplankton_net_or_station", "California Current", "yes"),
        (RAW / "datras", "ICES_DATRAS", "bottom_trawl", "North Sea", "no"),
        (RAW / "reef-life-survey", "Reef_Life_Survey_NRMN", "reef_visual_transect", "global_NRMN_sample", "no"),
        (RAW / "dfo", "DFO_Maritimes_RV", "bottom_trawl", "Scotian Shelf / Bay of Fundy", "no"),
    ]
    for folder, program, method, region, us in mapping:
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".csv", ".gz"} and not path.name.endswith(".csv.gz"):
                continue
            if "dictionary" in path.name.lower() or path.name.endswith(".xml.gz"):
                continue
            try:
                reports.append(inspect_path(path, program, method, region, us))
            except Exception as exc:  # noqa: BLE001
                reports.append(
                    {
                        "program": program,
                        "method": method,
                        "region": region,
                        "us_jurisdiction": us,
                        "file": path.name,
                        "status": "INSPECT_FAIL",
                        "error": type(exc).__name__,
                    }
                )
    return reports


def summarize(reports: list[dict]) -> dict:
    programs = sorted({r["program"] for r in reports if r.get("program")})
    methods = sorted({r["method"] for r in reports if r.get("method")})
    non_us = sorted({r["region"] for r in reports if r.get("us_jurisdiction") == "no"})
    valid = [r for r in reports if r.get("status") in {"VALID_ZEROS_AND_EVENTS", "EVENT_FRAME_PRESENT"}]
    valid_zeros = [r for r in reports if r.get("status") == "VALID_ZEROS_AND_EVENTS"]
    return {
        "programs": programs,
        "program_count": len(programs),
        "methods": methods,
        "method_count": len(methods),
        "non_us_regions": non_us,
        "non_us_region_count": len(non_us),
        "files_inspected": len(reports),
        "files_with_event_or_zeros": len(valid),
        "files_with_valid_zeros": len(valid_zeros),
        "milestone2_bar": (
            len(programs) >= 5
            and len(methods) >= 3
            and len(non_us) >= 2
            and len(valid_zeros) >= 1
            and len(valid) >= 3
        ),
    }


def write_md(reports: list[dict], summary: dict) -> None:
    MD.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Structured program status",
        "",
        "Aggregates only. No coordinates. Presence-only sources stay in `data/manifests/presence-only-catalog.csv`.",
        "",
        f"- Programs: {summary['program_count']} ({', '.join(summary['programs'])})",
        f"- Methods: {summary['method_count']} ({', '.join(summary['methods'])})",
        f"- Non-US regions: {summary['non_us_region_count']} ({', '.join(summary['non_us_regions'])})",
        f"- Files with event frames: {summary['files_with_event_or_zeros']}",
        f"- Files with valid zeros: {summary['files_with_valid_zeros']}",
        f"- Milestone 2 bar (5 programs / 3 methods / 2 non-US + tested frames): **{'PASS' if summary['milestone2_bar'] else 'INCOMPLETE'}**",
        "",
        "| Program | Method | Region | File | Events | Zeros | Status |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for rec in reports:
        lines.append(
            "| {program} | {method} | {region} | `{file}` | {events} | {zeros} | `{status}` |".format(
                program=rec.get("program", ""),
                method=rec.get("method", ""),
                region=rec.get("region", ""),
                file=rec.get("file", ""),
                events=rec.get("events", ""),
                zeros=rec.get("zero_rows", ""),
                status=rec.get("status", ""),
            )
        )
    lines.append("")
    MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    reports = collect()
    summary = summarize(reports)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"summary": summary, "files": reports}, indent=2) + "\n", encoding="utf-8")
    write_md(reports, summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
