#!/usr/bin/env python3
"""Match OISST to Puerto Rico survey dates; search one depth-relevant product.

Protected storage only. Does not rescore MUR SST. Does not download global grids.
Does not print coordinates.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "modeling"))

from run_puerto_rico_prediction_test import (  # noqa: E402
    HOLDOUT_YEAR,
    PR_LAT,
    PR_LON,
    TRAIN_YEARS,
    UA,
    YEARS,
    causal_sst_offsets,
    http_get_bytes,
    load_puerto_rico_events,
    parse_iso_date,
    required_paths,
    resolve_sst_for_day,
)

OISST_DATASET = "ncdcOisst21Agg_LonPM180"
OISST_VAR = "sst"
OISST_BASE = f"https://coastwatch.pfeg.noaa.gov/erddap/griddap/{OISST_DATASET}.csv"
OISST_CACHE = ROOT / "data" / "restricted" / "environmental" / OISST_DATASET / "by-date"
CW_SEARCH = "https://coastwatch.pfeg.noaa.gov/erddap/search/index.json"
NCEI_SEARCH = "https://www.ncei.noaa.gov/erddap/search/index.json"
STRIDE = 4
MAX_DAY_OFFSET = 2
AUDIT = ROOT / "audit" / "predictors"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def oisst_url(day: date) -> str:
    t = f"{day.isoformat()}T12:00:00Z"
    return (
        f"{OISST_BASE}?{OISST_VAR}"
        f"[({t}):1:({t})]"
        f"[(0.0):1:(0.0)]"
        f"[({PR_LAT[0]}):{STRIDE}:({PR_LAT[1]})]"
        f"[({PR_LON[0]}):{STRIDE}:({PR_LON[1]})]"
    )


def parse_mean(payload: bytes, field: str) -> float | None:
    text = payload.decode("utf-8", errors="replace")
    if text.lstrip().startswith("<"):
        return None
    reader = csv.DictReader(io.StringIO(text))
    vals: list[float] = []
    for row in reader:
        raw = (row.get(field) or "").strip()
        if not raw or raw.lower() in {"nan", "none", "null"}:
            continue
        try:
            vals.append(float(raw))
        except ValueError:
            continue
    if not vals:
        return None
    return sum(vals) / len(vals)


def fetch_day(day: date) -> float | None:
    OISST_CACHE.mkdir(parents=True, exist_ok=True)
    cache = OISST_CACHE / f"{day.isoformat()}.csv"
    meta = OISST_CACHE / f"{day.isoformat()}.json"
    if cache.is_file() and cache.stat().st_size > 0:
        mean = parse_mean(cache.read_bytes(), OISST_VAR)
        if mean is not None:
            return mean
        if meta.is_file() and json.loads(meta.read_text(encoding="utf-8")).get("status") == "empty":
            return None
    url = oisst_url(day)
    payload = http_get_bytes(url)
    time.sleep(0.12)
    cache.write_bytes(payload)
    mean = parse_mean(payload, OISST_VAR)
    meta.write_text(
        json.dumps(
            {
                "date": day.isoformat(),
                "url": url,
                "status": "ok" if mean is not None else "empty",
                "mean_sst": mean,
                "units": "degree_celsius",
                "time_offset": "T12:00:00Z product time; survey date kept at day precision",
                "bytes": len(payload),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return mean


def match_oisst(events: dict) -> dict:
    dates = sorted({parse_iso_date(rec["date"]) for rec in events.values() if rec.get("date")})
    day_sst: dict[str, float | None] = {}
    blockers: list[str] = []

    def ensure(day: date) -> float | None:
        key = day.isoformat()
        if key not in day_sst:
            try:
                day_sst[key] = fetch_day(day)
            except Exception as exc:  # noqa: BLE001
                blockers.append(f"{type(exc).__name__}")
                day_sst[key] = None
        return day_sst[key]

    print(f"oisst_dates={len(dates)}", flush=True)
    for i, day in enumerate(dates, 1):
        ensure(day)
        if i % 25 == 0 or i == len(dates):
            print(f"oisst_fetched={i}/{len(dates)}", flush=True)
    for day in dates:
        if day_sst.get(day.isoformat()) is not None:
            continue
        for offset in causal_sst_offsets(MAX_DAY_OFFSET)[1:]:
            if ensure(day + timedelta(days=offset)) is not None:
                break

    n_events = n_missing = 0
    for rec in events.values():
        n_events += 1
        d = rec.get("date")
        val = None
        off = None
        if d:
            val, off = resolve_sst_for_day(parse_iso_date(d), day_sst, max_past_days=MAX_DAY_OFFSET)
        rec["oisst"] = val
        rec["oisst_offset_days"] = off
        if val is None:
            n_missing += 1

    join_meta = {
        "dataset_id": OISST_DATASET,
        "variable": OISST_VAR,
        "units": "degree_celsius",
        "time_offset": "OISST daily field at 12:00Z; survey dates remain day precision",
        "lane": "retrospective",
        "max_day_offset": MAX_DAY_OFFSET,
        "allowed_offsets": causal_sst_offsets(MAX_DAY_OFFSET),
        "future_day_offsets_forbidden": True,
        "distinct_survey_dates": len(dates),
        "events": n_events,
        "events_missing": n_missing,
        "missing_fraction": round(n_missing / n_events, 6) if n_events else 1.0,
        "cache_dir": str(OISST_CACHE.relative_to(ROOT)),
        "blockers": blockers,
        "region_box": {"lat": PR_LAT, "lon": PR_LON, "stride": STRIDE},
        "same_config_can_point_at_another_region": True,
        "rescored_mur": False,
        "scored_on_2023": False,
        "retrieved_utc": utc_now(),
    }
    meta_path = OISST_CACHE.parent / "JOIN_META.json"
    meta_path.write_text(json.dumps(join_meta, indent=2) + "\n", encoding="utf-8")
    return join_meta


def search_erddap(base: str, query: str) -> list[dict]:
    url = f"{base}?searchFor={query.replace(' ', '%20')}&itemsPerPage=20&page=1"
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except Exception as exc:  # noqa: BLE001
        return [{"provider": base, "query": query, "error": str(exc)[:200]}]
    cols = payload["table"]["columnNames"]
    id_i = cols.index("Dataset ID")
    title_i = cols.index("Title")
    rows = []
    for item in payload["table"]["rows"]:
        rows.append(
            {
                "provider": base,
                "query": query,
                "dataset_id": item[id_i],
                "title": item[title_i],
            }
        )
    return rows


def search_depth_product() -> dict:
    queries = (
        "bottom temperature",
        "potential temperature depth",
        "GODAS temperature",
        "HYCOM temperature",
    )
    hits: list[dict] = []
    for q in queries:
        hits.extend(search_erddap(CW_SEARCH, q))
        time.sleep(0.2)
    depthish = [
        h
        for h in hits
        if h.get("dataset_id")
        and any(
            tok in (h.get("title", "") + " " + h.get("dataset_id", "")).lower()
            for tok in ("godas", "hycom", "bottom", "potential temperature", "3d", "depth")
        )
        and "sst" not in h.get("dataset_id", "").lower()
    ]
    chosen = None
    coverage = "HISTORICAL_COVERAGE_FAILED"
    for cand in depthish:
        ds = cand["dataset_id"]
        info_url = f"https://coastwatch.pfeg.noaa.gov/erddap/info/{ds}/index.json"
        try:
            request = urllib.request.Request(info_url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=45) as response:
                info = json.loads(response.read().decode("utf-8", errors="replace"))
            chosen = {
                "dataset_id": ds,
                "title": cand.get("title"),
                "info_url": info_url,
                "machine_readable": True,
                "global_grid_downloaded": False,
            }
            coverage = "DATASET_ID_VERIFIED_NOT_JOINED"
            _ = info
            break
        except Exception:
            continue
    result = {
        "variable": "bottom_or_depth_temperature",
        "coverage_status": coverage if chosen else "HISTORICAL_COVERAGE_FAILED",
        "chosen": chosen,
        "candidate_count": len(depthish),
        "notes": "No global grid downloaded. SST products were not accepted as bottom temperature.",
        "retrieved_utc": utc_now(),
    }
    dest = AUDIT / "DEPTH_TEMPERATURE_SEARCH.json"
    dest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def inventory(join_meta: dict, depth: dict) -> None:
    dest = AUDIT / "PILOT_VARIABLE_CURRENT_FORECAST.csv"
    rows = [
        {
            "variable": "analysed_sst",
            "product": "jplMURSST41",
            "historical": "MATCHED_TO_PR_EVENTS",
            "current_endpoint": "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41",
            "forecast_endpoint": "MISSING",
            "notes": "Already rejected for PR holdout. Not rescored.",
        },
        {
            "variable": "sst",
            "product": OISST_DATASET,
            "historical": "MATCHED_TO_PR_EVENTS" if join_meta.get("events") else "MATCH_FAILED",
            "current_endpoint": OISST_BASE.replace(".csv", ""),
            "forecast_endpoint": "MISSING",
            "notes": f"missing_fraction={join_meta.get('missing_fraction')}; units=degree_celsius; time=12:00Z daily",
        },
        {
            "variable": "bottom_or_depth_temperature",
            "product": (depth.get("chosen") or {}).get("dataset_id") or "",
            "historical": depth.get("coverage_status"),
            "current_endpoint": "MISSING" if not depth.get("chosen") else (depth["chosen"].get("info_url") or ""),
            "forecast_endpoint": "MISSING",
            "notes": "Global grids not downloaded.",
        },
        {
            "variable": "survey_depth",
            "product": "RVC SAMPLE_DEPTH",
            "historical": "ON_SURVEY",
            "current_endpoint": "N/A_SURVEY_FIELD",
            "forecast_endpoint": "N/A_SURVEY_FIELD",
            "notes": "Same config can point at another Atlantic RVC region.",
        },
    ]
    with dest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    events, _ = load_puerto_rico_events(required_paths())
    # Keep only the locked PR years already used; do not invent 2025.
    events = {k: v for k, v in events.items() if v.get("year") in YEARS}
    join_meta = match_oisst(events)
    depth = search_depth_product()
    inventory(join_meta, depth)
    print(f"oisst_events={join_meta['events']}")
    print(f"oisst_missing_fraction={join_meta['missing_fraction']}")
    print(f"depth_status={depth['coverage_status']}")
    print("rescored_mur=False")
    print("scored_on_2023=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
