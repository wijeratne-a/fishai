#!/usr/bin/env python3
"""Acquire HYCOM water temperature (all depths) for SBC LTER annual fish survey dates.

Protected storage only (data/restricted/). Regional box grids, not event extracts.
No join, no model fit, no coordinates printed. Site reference points are read from the
SBC LTER EML only to confirm the box contains every site with margin for the 10 km join.

One HYCOM experiment per survey year so a year never mixes model configurations.
Coverage windows were probed on ncss.hycom.org (dataset.xml TimeSpan) on 2026-09-27.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fk_acq = _load("fk_acq", "scripts/acquisition/acquire_florida_keys_environment.py")
socal = _load("socal_kelp_bass", "scripts/modeling/socal_kelp_bass.py")

HYCOM_DIR = socal.HYCOM_DIR
MANIFEST = ROOT / "data" / "manifests" / "socal-environment-manifest.csv"
SURVEY_YEARS = (*socal.TRAIN_YEARS, socal.TEST_YEAR)
MAX_PAST_DAYS = 2
BOX_MARGIN_DEG = 0.25
NCSS = "https://ncss.hycom.org/thredds/ncss"

_REAN = "GOFS 3.1 reanalysis (GLBv0.08 expt_53.X)"
HYCOM_BY_YEAR = {
    **{y: (f"GLBv0.08/expt_53.X/data/{y}", _REAN, date(y, 1, 1), date(y, 12, 31)) for y in range(1994, 2016)},
    2016: ("GLBv0.08/expt_57.2", "GOFS 3.1 analysis", date(2016, 5, 1), date(2017, 2, 1)),
    2017: ("GLBv0.08/expt_57.7", "GOFS 3.1 analysis", date(2017, 6, 1), date(2017, 10, 1)),
    2018: ("GLBv0.08/expt_93.0", "GOFS 3.1 analysis", date(2018, 1, 1), date(2020, 2, 19)),
    **{y: ("GLBy0.08/expt_93.0/ts3z", "GOFS 3.1 analysis", date(2018, 12, 4), date(2024, 9, 5)) for y in range(2019, 2025)},
}


def box() -> dict:
    sites = socal.sbc_sites()
    lats = [s["_lat"] for s in sites.values()]
    lons = [s["_lon"] for s in sites.values()]
    return {
        "north": round(max(lats) + BOX_MARGIN_DEG, 2),
        "south": round(min(lats) - BOX_MARGIN_DEG, 2),
        "west": round(min(lons) - BOX_MARGIN_DEG, 2),
        "east": round(max(lons) + BOX_MARGIN_DEG, 2),
    }


def survey_dates() -> dict[int, list[date]]:
    out: dict[int, set] = {y: set() for y in SURVEY_YEARS}
    with socal.FISH_CSV.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["SURVEY"] != socal.SURVEY_PROTOCOL:
                continue
            year = int(row["YEAR"])
            if year in out:
                out[year].add(date.fromisoformat(row["DATE"]))
    return {y: sorted(d) for y, d in out.items()}


def hycom_url(dataset: str, day: date, bbox: dict) -> str:
    return (
        f"{NCSS}/{dataset}?var=water_temp"
        f"&north={bbox['north']}&south={bbox['south']}&west={bbox['west']}&east={bbox['east']}"
        f"&time={day.isoformat()}T12:00:00Z&accept=netcdf"
    )


def fetch_hycom(year: int, day: date, bbox: dict) -> dict:
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
        "retrieved_utc": fk_acq.utc_now(),
    }
    for back in range(0, MAX_PAST_DAYS + 1):
        cand = day - timedelta(days=back)
        if not (start <= cand <= end):
            record["attempts"].append({"field_date": cand.isoformat(), "http": "OUT_OF_EXPERIMENT_RANGE"})
            continue
        url = hycom_url(dataset, cand, bbox)
        code = fk_acq.curl(url, dest)
        record["attempts"].append({"field_date": cand.isoformat(), "http": code})
        if dest.is_file():
            record.update(
                status="ok", field_date=cand.isoformat(), offset_days=back, url=url,
                bytes=dest.stat().st_size, sha256=fk_acq.sha256(dest),
            )
            break
    HYCOM_DIR.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def write_manifest(hycom: list[dict], dates: dict[int, list[date]]) -> None:
    rows = []
    for year in SURVEY_YEARS:
        recs = [r for r in hycom if r["survey_year"] == year]
        ok = [r for r in recs if r["status"] == "ok"]
        rows.append({
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
            "joined_to_events": "by scripts/modeling/socal_kelp_bass.py at run time",
            "notes": HYCOM_BY_YEAR[year][1] + "; regional box grid around SBC LTER sites; one experiment per year",
        })
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    bbox = box()
    dates = survey_dates()
    print(json.dumps({"survey_dates": {y: len(d) for y, d in dates.items()}}), flush=True)
    jobs = [(y, d) for y, ds in dates.items() for d in ds]
    hycom: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, rec in enumerate(pool.map(lambda job: fetch_hycom(job[0], job[1], bbox), jobs), 1):
            hycom.append(rec)
            if i % 25 == 0 or i == len(jobs):
                print(f"hycom {i}/{len(jobs)} ok={sum(1 for r in hycom if r['status'] == 'ok')}", flush=True)
    write_manifest(hycom, dates)
    print(f"wrote {MANIFEST.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
