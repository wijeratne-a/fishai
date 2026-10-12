#!/usr/bin/env python3
"""
GATE 1: spatiotemporal overlap between public predator telemetry and CPS prey surveys.

Public inputs only (GBIF/ERDDAP). Writes summary JSON under artifacts/ (counts only;
raw pulls stay in data/raw/, gitignored).
"""

from __future__ import annotations

import csv
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fishai.ingestion.biology.cps_nearshore.fetch import (  # noqa: E402
    BBox as NSBBox,
    build_erddap_csv_url as build_nearshore_url,
)
from fishai.ingestion.biology.cps_trawl.fetch import (  # noqa: E402
    BBox,
    build_erddap_csv_url as build_trawl_url,
    iter_halfyear_windows,
)

PILOT = BBox(32.0, 35.0, -121.0, -117.0)

# GBIF datasets explicitly labeled TOPP on OBIS-SEAMAP (verified 2026-10-12).
TOPP_GBIF_DATASETS = {
    "50914b57-6c66-4432-91c7-edbc7a296a9f": {
        "title": "TOPP Summary of SSM-derived Telemetry",
        "url": "https://www.gbif.org/dataset/50914b57-6c66-4432-91c7-edbc7a296a9f",
        "doi": "10.82144/d127533f",
        "notes": "SSM-derived; 1° grid cells in many records (coarse).",
    },
    "e737f8ca-6176-4e3a-9ab1-dc5a77d46194": {
        "title": "TOPP Albatrosses 2002-06",
        "url": "https://www.gbif.org/dataset/e737f8ca-6176-4e3a-9ab1-dc5a77d46194",
        "doi": None,
        "notes": "Point-level satellite/GPS albatross tracks.",
    },
}

PREY_SPECIES = {
    "Trachurus symmetricus": "jack_mackerel",
    "Sardinops sagax": "sardine",
    "Engraulis mordax": "anchovy",
}

TRAWL_T0 = date(2003, 7, 9)
TRAWL_T1 = date(2025, 9, 10)
NEARSHORE_T0 = date(2019, 6, 21)
NEARSHORE_T1 = date(2026, 6, 1)

# Jack mackerel encounter model uses CPS adult training table (post-QC subset of surveys).
MODEL_TRAINING_NOTE = (
    "Jack mackerel all-sizes encounter fit frame: 253 presences / 536 rows after mesh/covariate QC "
    "(configs/models/jack_mackerel_encounter_all_sizes.yaml); includes nearshore through 2024–2025."
)

SPATIAL_MATCH_KM = 50.0
TEMPORAL_MATCH_DAYS = 14


def _http_get_json(url: str, *, timeout: float = 120.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "fishai-predator-prey-gate1/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_get_bytes(url: str, *, timeout: float = 300.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "fishai-predator-prey-gate1/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def parse_event_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(raw[:19], fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def in_pilot(lat: float | None, lon: float | None) -> bool:
    if lat is None or lon is None:
        return False
    return PILOT.lat_min <= lat <= PILOT.lat_max and PILOT.lon_min <= lon <= PILOT.lon_max


@dataclass(frozen=True)
class PredPoint:
    dataset_key: str
    species: str
    lat: float
    lon: float
    when: datetime


@dataclass(frozen=True)
class PreyEvent:
    source: str
    species: str
    lat: float
    lon: float
    when: datetime
    event_id: str


def gbif_occurrence_count(dataset_key: str, *, pilot_only: bool) -> int:
    params: dict[str, str | int | float] = {"datasetKey": dataset_key, "limit": 0}
    if pilot_only:
        params.update(
            {
                "decimalLatitude": f"{PILOT.lat_min},{PILOT.lat_max}",
                "decimalLongitude": f"{PILOT.lon_min},{PILOT.lon_max}",
            }
        )
    q = urllib.parse.urlencode(params)
    payload = _http_get_json(f"https://api.gbif.org/v1/occurrence/search?{q}")
    return int(payload.get("count") or 0)


def fetch_gbif_dataset_occurrences(
    dataset_key: str,
    *,
    pilot_only: bool = True,
) -> list[PredPoint]:
    out: list[PredPoint] = []
    offset = 0
    limit = 300
    while True:
        params: dict[str, str | int | float] = {
            "datasetKey": dataset_key,
            "limit": limit,
            "offset": offset,
        }
        if pilot_only:
            params.update(
                {
                    "decimalLatitude": f"{PILOT.lat_min},{PILOT.lat_max}",
                    "decimalLongitude": f"{PILOT.lon_min},{PILOT.lon_max}",
                }
            )
        q = urllib.parse.urlencode(params)
        payload = _http_get_json(f"https://api.gbif.org/v1/occurrence/search?{q}")
        results = payload.get("results") or []
        if not results:
            break
        for row in results:
            lat = row.get("decimalLatitude")
            lon = row.get("decimalLongitude")
            if lat is None or lon is None:
                continue
            when = parse_event_date(row.get("eventDate")) or (
                datetime(int(row["year"]), 7, 1, tzinfo=timezone.utc) if row.get("year") else None
            )
            if when is None:
                continue
            species = row.get("species") or row.get("scientificName") or "unknown"
            out.append(
                PredPoint(
                    dataset_key=dataset_key,
                    species=str(species),
                    lat=float(lat),
                    lon=float(lon),
                    when=when,
                )
            )
        offset += limit
        if payload.get("endOfRecords"):
            break
        time.sleep(0.15)
    return out


def _fetch_erddap_csv(url: str) -> list[dict[str, str]]:
    try:
        body = _http_get_bytes(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise
    text = body.decode("utf-8", errors="replace")
    reader = csv.DictReader(text.splitlines())
    rows = list(reader)
    # Drop ERDDAP units row if present
    if rows and rows[0].get("cruise", "").startswith("Unit"):
        rows = rows[1:]
    return rows


def fetch_prey_presence_events() -> list[PreyEvent]:
    events: list[PreyEvent] = []
    # Trawl haul catch — presence rows for target species (non presence-only, counted).
    for win_start, win_end in iter_halfyear_windows(TRAWL_T0, TRAWL_T1):
        url = build_trawl_url(win_start, win_end, PILOT)
        for row in _fetch_erddap_csv(url):
            name = (row.get("scientific_name") or "").strip()
            if name not in PREY_SPECIES:
                continue
            if (row.get("presence_only") or "").strip().upper() == "Y":
                continue
            cnt = row.get("subsample_count")
            if not cnt or not str(cnt).strip().lstrip("-").isdigit():
                continue
            if int(float(cnt)) <= 0:
                continue
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            when = parse_event_date(row.get("time"))
            if when is None:
                continue
            eid = f"trawl:{row.get('cruise')}:{row.get('ship')}:{row.get('haul')}"
            events.append(
                PreyEvent(
                    source="swfsc_cps_trawl_haul_catch",
                    species=PREY_SPECIES[name],
                    lat=lat,
                    lon=lon,
                    when=when,
                    event_id=eid,
                )
            )

    ns_bbox = NSBBox(PILOT.lat_min, PILOT.lat_max, PILOT.lon_min, PILOT.lon_max)
    for year in range(NEARSHORE_T0.year, NEARSHORE_T1.year + 1):
        win_start = datetime(year, 1, 1, tzinfo=timezone.utc)
        win_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        url = build_nearshore_url(win_start, win_end, ns_bbox)
        for row in _fetch_erddap_csv(url):
            name = (row.get("scientific_name") or "").strip()
            if name not in PREY_SPECIES:
                continue
            n = row.get("totalNumber") or row.get("total_number")
            if not n or not str(n).strip().lstrip("-").isdigit():
                continue
            if int(float(n)) <= 0:
                continue
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            # nearshore uses date + time columns
            when = parse_event_date(row.get("time")) or parse_event_date(row.get("date"))
            if when is None:
                continue
            eid = f"nearshore:{row.get('cruise')}:{row.get('set')}"
            events.append(
                PreyEvent(
                    source="swfsc_cps_nearshore_set_catch",
                    species=PREY_SPECIES[name],
                    lat=lat,
                    lon=lon,
                    when=when,
                    event_id=eid,
                )
            )
    return events


def summarize_predators(points: list[PredPoint]) -> dict:
    scb = [p for p in points if in_pilot(p.lat, p.lon)]
    by_ds: Counter[str] = Counter()
    by_sp: Counter[str] = Counter()
    years_scb: list[int] = []
    for p in scb:
        by_ds[p.dataset_key] += 1
        by_sp[p.species] += 1
        years_scb.append(p.when.year)
    return {
        "n_global": len(points),
        "n_pilot_bbox": len(scb),
        "year_min_pilot": min(years_scb) if years_scb else None,
        "year_max_pilot": max(years_scb) if years_scb else None,
        "n_pilot_year_lte_2010": sum(1 for p in scb if p.when.year <= 2010),
        "n_pilot_year_gte_2011": sum(1 for p in scb if p.when.year >= 2011),
        "top_species_pilot": by_sp.most_common(15),
        "by_dataset_pilot": dict(by_ds),
    }


def summarize_prey(events: list[PreyEvent]) -> dict:
    years = [e.when.year for e in events]
    by_sp = Counter(e.species for e in events)
    by_src = Counter(e.source for e in events)
    post_2010 = [e for e in events if e.when.year >= 2011]
    return {
        "n_presence_events_pilot": len(events),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "n_presence_events_year_gte_2011": len(post_2010),
        "by_species": dict(by_sp),
        "by_source": dict(by_src),
    }


def spatiotemporal_overlap(pred: list[PredPoint], prey: list[PreyEvent]) -> dict:
    pred_scb = [p for p in pred if in_pilot(p.lat, p.lon)]
    if not pred_scb or not prey:
        return {
            "n_pred_pilot": len(pred_scb),
            "n_prey_presence": len(prey),
            "n_pred_matched": 0,
            "fraction_pred_matched": 0.0,
            "n_prey_matched": 0,
            "fraction_prey_matched": 0.0,
        }

    # Index prey by year for cheap candidate filtering
    prey_by_year: dict[int, list[PreyEvent]] = defaultdict(list)
    for e in prey:
        prey_by_year[e.when.year].append(e)

    matched_pred = 0
    matched_prey_ids: set[str] = set()
    delta = timedelta(days=TEMPORAL_MATCH_DAYS)

    for p in pred_scb:
        candidates: list[PreyEvent] = []
        for yr in range(p.when.year - 1, p.when.year + 2):
            candidates.extend(prey_by_year.get(yr, []))
        hit = False
        for e in candidates:
            if abs((p.when - e.when).total_seconds()) > delta.total_seconds():
                continue
            if haversine_km(p.lat, p.lon, e.lat, e.lon) <= SPATIAL_MATCH_KM:
                hit = True
                matched_prey_ids.add(e.event_id)
        if hit:
            matched_pred += 1

    return {
        "spatial_match_km": SPATIAL_MATCH_KM,
        "temporal_match_days": TEMPORAL_MATCH_DAYS,
        "n_pred_pilot": len(pred_scb),
        "n_prey_presence": len(prey),
        "n_pred_matched": matched_pred,
        "fraction_pred_matched": matched_pred / len(pred_scb) if pred_scb else 0.0,
        "n_prey_matched": len(matched_prey_ids),
        "fraction_prey_matched": len(matched_prey_ids) / len(prey) if prey else 0.0,
    }


def overlap_post_2010_only(pred: list[PredPoint], prey: list[PreyEvent]) -> dict:
    pred2 = [p for p in pred if in_pilot(p.lat, p.lon) and p.when.year >= 2011]
    prey2 = [e for e in prey if e.when.year >= 2011]
    base = spatiotemporal_overlap(pred2, prey2)
    base["subset"] = "pilot_bbox_and_year_gte_2011"
    return base


def main() -> int:
    out_dir = REPO / "artifacts" / "predator_prey_proxy"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "gate1_overlap_summary.json"

    print("Fetching TOPP GBIF datasets...", flush=True)
    all_pred: list[PredPoint] = []
    dataset_meta = []
    for key, meta in TOPP_GBIF_DATASETS.items():
        n_global = gbif_occurrence_count(key, pilot_only=False)
        pts = fetch_gbif_dataset_occurrences(key, pilot_only=True)
        all_pred.extend(pts)
        dataset_meta.append(
            {
                **meta,
                "dataset_key": key,
                "n_occurrences_gbif_global": n_global,
                "n_occurrences_pilot_bbox": len(pts),
            }
        )
        print(
            f"  {meta['title']}: global={n_global} pilot={len(pts)}",
            flush=True,
        )

    print("Fetching CPS prey presence events (ERDDAP)...", flush=True)
    prey = fetch_prey_presence_events()
    print(f"  prey presence events in pilot bbox: {len(prey)}", flush=True)

    pred_summary = summarize_predators(all_pred)
    pred_summary["n_global_gbif_topp_datasets"] = sum(m["n_occurrences_gbif_global"] for m in dataset_meta)
    prey_summary = summarize_prey(prey)
    overlap_all = spatiotemporal_overlap(all_pred, prey)
    overlap_post2010 = overlap_post_2010_only(all_pred, prey)

    # IOOS ATN / OTN / IMOS: documented availability scan (no bulk public pull in this run).
    ancillary_sources = {
        "ioos_atn_portal": {
            "url": "https://portal.atn.ioos.us/",
            "result": "Portal loads; no public ERDDAP/API bulk export discovered at /api/ or /erddap/ (404 on 2026-10-12). Catalog search not scripted.",
        },
        "ocean_tracking_network": {
            "url": "https://oceantrack.org/data/",
            "result": "Program site; no California Current bulk track download endpoint used (Atlantic-centric network).",
        },
        "imos_animal_tracking": {
            "url": "https://animaltracking.aodn.org.au/",
            "result": "Australian domain; not queried for SCB overlap (out of geography).",
        },
    }

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pilot_bbox": {
            "lat_min": PILOT.lat_min,
            "lat_max": PILOT.lat_max,
            "lon_min": PILOT.lon_min,
            "lon_max": PILOT.lon_max,
        },
        "predator_sources_gbif_topp": dataset_meta,
        "predator_summary": pred_summary,
        "prey_survey_sources": {
            "trawl": {
                "dataset": "FRDCPSTrawlLHHaulCatch",
                "url": "https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSTrawlLHHaulCatch",
                "date_range_requested": [str(TRAWL_T0), str(TRAWL_T1)],
            },
            "nearshore": {
                "dataset": "FRDCPSNearshoreSetCatch",
                "url": "https://coastwatch.pfeg.noaa.gov/erddap/tabledap/FRDCPSNearshoreSetCatch",
                "date_range_requested": [str(NEARSHORE_T0), str(NEARSHORE_T1)],
            },
        },
        "prey_presence_summary": prey_summary,
        "model_training_note": MODEL_TRAINING_NOTE,
        "jack_mackerel_cv_baseline": {
            "source": "artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json",
            "n_failed_folds": 0,
            "oof_auc": 0.7622,
            "model_spec": "linear_covariates_spatial_off_rw0",
        },
        "overlap_all_years": overlap_all,
        "overlap_post_2010_prey_era": overlap_post2010,
        "ancillary_source_scan": ancillary_sources,
        "gate1_verdict": None,
    }

    # Meaningful overlap threshold (pre-declared, conservative): >=5% predator points matched OR >=5% post-2010 prey matched.
    post = overlap_post2010
    meaningful = (
        post["fraction_pred_matched"] >= 0.05
        or post["fraction_prey_matched"] >= 0.05
    )
    if pred_summary["n_pilot_bbox"] == 0:
        verdict = "STOP: zero predator telemetry points in pilot bbox from public TOPP GBIF products."
    elif pred_summary["n_pilot_year_gte_2011"] == 0:
        verdict = (
            "STOP: temporal mismatch — all TOPP GBIF points in pilot bbox end by 2010; "
            f"post-2010 prey presence events={prey_summary['n_presence_events_year_gte_2011']} with zero overlapping-era predator tags."
        )
    elif not meaningful:
        verdict = (
            "STOP: no meaningful spatiotemporal overlap in post-2010 era "
            f"(pred matched fraction={post['fraction_pred_matched']:.4f}, "
            f"prey matched fraction={post['fraction_prey_matched']:.4f}; "
            f"threshold 5%)."
        )
    else:
        verdict = "PROCEED: meaningful overlap — GATE 2 modeling allowed."

    report["gate1_verdict"] = verdict
    summary_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nWrote {summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
