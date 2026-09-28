#!/usr/bin/env python3
"""Acquire depth-resolved temperature and chlorophyll for Florida Keys survey dates.

Protected storage only (data/restricted/). Regional box grids, not event extracts.
No join, no model fit, no coordinates printed. Survey coordinates are read only to
confirm the box contains every dive.

HYCOM water_temp (all depth levels) from ncss.hycom.org, one experiment per survey year.
VIIRS SNPP science-quality weekly chlorophyll from CoastWatch ERDDAP.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "biological"
OUT = ROOT / "data" / "restricted" / "environmental"
HYCOM_DIR = OUT / "hycom" / "florida-keys" / "by-date"
VIIRS_DIR = OUT / "viirs-chla-weekly" / "florida-keys" / "by-week"
MANIFEST = ROOT / "data" / "manifests" / "florida-keys-environment-manifest.csv"

SURVEY_YEARS = (2014, 2016, 2018, 2022, 2024)
BOX = {"north": 25.9, "south": 24.3, "west": -82.1, "east": -80.0}
MAX_PAST_DAYS = 2
NCSS = "https://ncss.hycom.org/thredds/ncss"
VIIRS_URL = "https://coastwatch.noaa.gov/erddap/griddap/noaacwNPPVIIRSSQchlaWeekly.nc"

# One HYCOM experiment per survey year so a year never mixes model configurations.
HYCOM_BY_YEAR = {
    2014: ("GLBv0.08/expt_53.X/data/2014", "GOFS 3.1 reanalysis", date(2014, 1, 1), date(2014, 12, 31)),
    2016: ("GLBv0.08/expt_57.2", "GOFS 3.1 analysis", date(2016, 5, 1), date(2017, 2, 1)),
    2018: ("GLBv0.08/expt_93.0", "GOFS 3.1 analysis", date(2018, 1, 1), date(2020, 2, 19)),
    2022: ("GLBy0.08/expt_93.0/ts3z", "GOFS 3.1 analysis", date(2018, 12, 4), date(2024, 9, 5)),
    2024: ("GLBy0.08/expt_93.0/ts3z", "GOFS 3.1 analysis", date(2018, 12, 4), date(2024, 9, 5)),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def survey_files() -> dict[int, Path]:
    return {year: RAW / f"noaa-rvc-florida-keys-{year}.csv.gz" for year in SURVEY_YEARS}


def survey_dates() -> dict[int, list[date]]:
    """Distinct survey dates per year; asserts every dive is inside BOX."""
    out: dict[int, list[date]] = {}
    for year, path in survey_files().items():
        dates: set[date] = set()
        outside = 0
        with gzip.open(path, "rt", encoding="latin-1", newline="") as handle:
            for row in csv.DictReader(handle):
                stamp = (row.get("time") or "").strip()
                if not stamp[:4].isdigit():
                    continue
                dates.add(date.fromisoformat(stamp[:10]))
                try:
                    lat, lon = float(row["latitude"]), float(row["longitude"])
                except (KeyError, ValueError):
                    continue
                if not (BOX["south"] <= lat <= BOX["north"] and BOX["west"] <= lon <= BOX["east"]):
                    outside += 1
        if outside:
            raise RuntimeError(f"{year}: {outside} survey rows fall outside the acquisition box")
        out[year] = sorted(dates)
    return out


def curl(url: str, dest: Path, timeout: int = 300, tries: int = 3) -> int:
    """Download a NetCDF file. HTTP 200 with a non-NetCDF body is retried, not accepted."""
    partial = dest.with_suffix(dest.suffix + ".partial")
    code = -1
    for attempt in range(tries):
        result = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), "-o", str(partial), "-w", "%{http_code}", url],
            capture_output=True,
            text=True,
        )
        code = int(result.stdout.strip() or 0) or -1
        if code == 200 and partial.is_file() and partial.read_bytes()[:3] == b"CDF":
            partial.replace(dest)
            return code
        if partial.exists():
            partial.unlink()
        if code != 200:
            return code
        time.sleep(5 * (attempt + 1))
    return code


def hycom_url(dataset: str, day: date) -> str:
    return (
        f"{NCSS}/{dataset}?var=water_temp"
        f"&north={BOX['north']}&south={BOX['south']}&west={BOX['west']}&east={BOX['east']}"
        f"&time={day.isoformat()}T12:00:00Z&accept=netcdf"
    )


def fetch_hycom(year: int, day: date) -> dict:
    """Same-day field, else a past day. Never a later day."""
    dataset, product, start, end = HYCOM_BY_YEAR[year]
    dest = HYCOM_DIR / f"{day.isoformat()}.nc"
    meta = dest.with_suffix(".json")
    if dest.is_file() and meta.is_file():
        return json.loads(meta.read_text(encoding="utf-8"))
    record = {
        "survey_date": day.isoformat(),
        "survey_year": year,
        "dataset": dataset,
        "product": product,
        "variable": "water_temp",
        "units": "degC",
        "status": "missing",
        "field_date": None,
        "offset_days": None,
        "attempts": [],
        "retrieved_utc": utc_now(),
    }
    for back in range(0, MAX_PAST_DAYS + 1):
        cand = day - timedelta(days=back)
        if not (start <= cand <= end):
            record["attempts"].append({"field_date": cand.isoformat(), "http": "OUT_OF_EXPERIMENT_RANGE"})
            continue
        url = hycom_url(dataset, cand)
        code = curl(url, dest)
        record["attempts"].append({"field_date": cand.isoformat(), "http": code})
        if dest.is_file():
            record.update(
                status="ok",
                field_date=cand.isoformat(),
                offset_days=back,
                url=url,
                bytes=dest.stat().st_size,
                sha256=sha256(dest),
            )
            break
    HYCOM_DIR.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def viirs_weeks(dates: list[date]) -> list[date]:
    """Weekly composite centers (Mondays) spanning the survey season plus a lead-in."""
    first = min(dates) - timedelta(days=21)
    monday = first - timedelta(days=first.weekday())
    weeks = []
    while monday <= max(dates):
        weeks.append(monday)
        monday += timedelta(days=7)
    return weeks


def fetch_viirs(week: date) -> dict:
    dest = VIIRS_DIR / f"{week.isoformat()}.nc"
    meta = dest.with_suffix(".json")
    if dest.is_file() and meta.is_file():
        return json.loads(meta.read_text(encoding="utf-8"))
    url = (
        f"{VIIRS_URL}?chlor_a%5B({week.isoformat()}T12:00:00Z)%5D%5B(0.0)%5D"
        f"%5B({BOX['north']}):1:({BOX['south']})%5D%5B({BOX['west']}):1:({BOX['east']})%5D"
    )
    VIIRS_DIR.mkdir(parents=True, exist_ok=True)
    code = curl(url, dest)
    record = {
        "week_center": week.isoformat(),
        "dataset": "noaacwNPPVIIRSSQchlaWeekly",
        "variable": "chlor_a",
        "units": "mg m-3",
        "fill_value": -999.0,
        "time_semantics": "centered weekly composite; covers about center-3.5d to center+3.5d",
        "causal_rule": "usable for a survey only if week_center + 4 days < survey date",
        "status": "ok" if dest.is_file() else "missing",
        "http": code,
        "url": url,
        "retrieved_utc": utc_now(),
    }
    if dest.is_file():
        record.update(bytes=dest.stat().st_size, sha256=sha256(dest))
    meta.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def write_manifest(hycom: list[dict], viirs: list[dict], dates: dict[int, list[date]]) -> None:
    rows = []
    for year in SURVEY_YEARS:
        recs = [r for r in hycom if r["survey_year"] == year]
        ok = [r for r in recs if r["status"] == "ok"]
        rows.append(
            {
                "variable": "water_temp_all_depths",
                "provider": "HYCOM consortium (ncss.hycom.org)",
                "dataset_id": HYCOM_BY_YEAR[year][0],
                "survey_year": year,
                "survey_dates": len(dates[year]),
                "dates_ok": len(ok),
                "dates_missing": len(recs) - len(ok),
                "past_day_fallbacks": sum(1 for r in ok if r["offset_days"]),
                "future_days_used": 0,
                "storage": str(HYCOM_DIR.relative_to(ROOT)),
                "joined_to_events": "no",
                "notes": HYCOM_BY_YEAR[year][1] + "; regional box grid; one experiment per year",
            }
        )
    ok_weeks = sum(1 for r in viirs if r["status"] == "ok")
    rows.append(
        {
            "variable": "chlorophyll_a_weekly",
            "provider": "NOAA CoastWatch (VIIRS SNPP science quality)",
            "dataset_id": "noaacwNPPVIIRSSQchlaWeekly",
            "survey_year": "all",
            "survey_dates": sum(len(v) for v in dates.values()),
            "dates_ok": ok_weeks,
            "dates_missing": len(viirs) - ok_weeks,
            "past_day_fallbacks": "n/a",
            "future_days_used": 0,
            "storage": str(VIIRS_DIR.relative_to(ROOT)),
            "joined_to_events": "no",
            "notes": "weekly composites counted in dates_ok; masked over shallow reef and land (fill -999)",
        }
    )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--only", choices=["hycom", "viirs", "all"], default="all")
    args = parser.parse_args()

    dates = survey_dates()
    print(json.dumps({"survey_dates": {y: len(d) for y, d in dates.items()}}), flush=True)

    hycom: list[dict] = []
    if args.only in ("hycom", "all"):
        jobs = [(y, d) for y, ds in dates.items() for d in ds]
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for i, rec in enumerate(pool.map(lambda job: fetch_hycom(*job), jobs), 1):
                hycom.append(rec)
                if i % 25 == 0 or i == len(jobs):
                    ok = sum(1 for r in hycom if r["status"] == "ok")
                    print(f"hycom {i}/{len(jobs)} ok={ok}", flush=True)

    viirs: list[dict] = []
    if args.only in ("viirs", "all"):
        weeks = sorted({w for ds in dates.values() for w in viirs_weeks(ds)})
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for i, rec in enumerate(pool.map(fetch_viirs, weeks), 1):
                viirs.append(rec)
                if i % 25 == 0 or i == len(weeks):
                    ok = sum(1 for r in viirs if r["status"] == "ok")
                    print(f"viirs {i}/{len(weeks)} ok={ok}", flush=True)

    if args.only == "all":
        write_manifest(hycom, viirs, dates)
        print(f"wrote {MANIFEST.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
