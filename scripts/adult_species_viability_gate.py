#!/usr/bin/env python3
"""Count non–presence-only catch presences for an adult CPS target species (viability gate)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from fishai.ingestion.biology.cps_trawl.catch import is_presence_only  # noqa: E402
from fishai.ingestion.sources import load_sources_manifest  # noqa: E402

GCS_BASE = "https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division"
GCS_TRAWL_CATCH = f"{GCS_BASE}/CPS_Trawl_LifeHistory_HaulCatch.csv"
GCS_NEARSHORE_CATCH = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv"
GCS_TRAWL_SPECIMEN = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Specimen.csv"
GCS_NEARSHORE_SPECIMEN = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Nearshore_Specimen.csv"

STOP_BELOW = 100
MARGINAL_MAX = 150


@dataclass(frozen=True)
class BBox:
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "na", ""}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(value: Any) -> int | None:
    f = _parse_float(value)
    if f is None:
        return None
    if f < 0 or f != int(f):
        return None
    return int(f)


def _in_bbox(lat: Any, lon: Any, bbox: BBox) -> bool:
    lat_f, lon_f = _parse_float(lat), _parse_float(lon)
    if lat_f is None or lon_f is None:
        return False
    return bbox.lat_min <= lat_f <= bbox.lat_max and bbox.lon_min <= lon_f <= bbox.lon_max


def _trawl_row_presence(row: dict[str, str]) -> bool:
    if is_presence_only(row.get("presenceOnly") or row.get("presence_only")):
        return False
    for key in (
        "subSampleCount",
        "subsample_count",
        "subSampleWeightkg",
        "subsample_weight",
        "remainingWeightkg",
        "remaining_weight",
    ):
        v = _parse_float(row.get(key))
        if v is not None and v > 0:
            return True
    sc = _parse_int(row.get("subSampleCount") or row.get("subsample_count"))
    return sc is not None and sc > 0


def _nearshore_row_presence(row: dict[str, str]) -> bool:
    for key in ("totalNumber", "total_number", "totalWeightkg", "total_weight_kg"):
        v = _parse_float(row.get(key))
        if v is not None and v > 0:
            return True
    return False


def _species_name(row: dict[str, str]) -> str:
    return str(row.get("scientificName") or row.get("scientific_name") or "").strip()


def _count_trawl(path: Path, species: str, bbox: BBox) -> dict[str, int]:
    out = {
        "catch_rows_total": 0,
        "species_rows_all_regions": 0,
        "presence_only_rows_pilot": 0,
        "non_presence_only_presences_pilot": 0,
        "non_presence_only_presences_all_regions": 0,
    }
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            out["catch_rows_total"] += 1
            if _species_name(row) != species:
                continue
            out["species_rows_all_regions"] += 1
            lat = row.get("startLatitude") or row.get("latitude")
            lon = row.get("startLongitude") or row.get("longitude")
            in_pilot = _in_bbox(lat, lon, bbox)
            po = is_presence_only(row.get("presenceOnly") or row.get("presence_only"))
            if _trawl_row_presence(row):
                out["non_presence_only_presences_all_regions"] += 1
                if in_pilot and not po:
                    out["non_presence_only_presences_pilot"] += 1
            if in_pilot and po:
                out["presence_only_rows_pilot"] += 1
    return out


def _count_nearshore(path: Path, species: str, bbox: BBox) -> dict[str, int]:
    out = {
        "catch_rows_total": 0,
        "species_rows_all_regions": 0,
        "presences_pilot": 0,
        "presences_all_regions": 0,
    }
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            out["catch_rows_total"] += 1
            if _species_name(row) != species:
                continue
            out["species_rows_all_regions"] += 1
            lat = row.get("Latitude") or row.get("latitude")
            lon = row.get("Longitude") or row.get("longitude")
            if not _nearshore_row_presence(row):
                continue
            out["presences_all_regions"] += 1
            if _in_bbox(lat, lon, bbox):
                out["presences_pilot"] += 1
    return out


def _specimen_length_mm(row: dict[str, str]) -> float | None:
    for key in (
        "standardLength_mm",
        "standard_length",
        "forkLength_mm",
        "fork_length",
        "totalLength_mm",
        "total_length",
    ):
        v = _parse_float(row.get(key))
        if v is not None:
            return v
    return None


def _specimen_stats(path: Path, species: str, bbox: BBox) -> dict[str, Any]:
    lengths: list[float] = []
    specimens_pilot = 0
    specimens_all = 0
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if _species_name(row) != species:
                continue
            specimens_all += 1
            lat = row.get("Latitude") or row.get("latitude")
            lon = row.get("Longitude") or row.get("longitude")
            if _in_bbox(lat, lon, bbox):
                specimens_pilot += 1
            lm = _specimen_length_mm(row)
            if lm is not None:
                lengths.append(lm)
    stats: dict[str, Any] = {
        "specimens_all_regions": specimens_all,
        "specimens_pilot_bbox": specimens_pilot,
        "specimens_with_length_all_regions": len(lengths),
    }
    if lengths:
        stats["length_mm_min"] = min(lengths)
        stats["length_mm_max"] = max(lengths)
        stats["length_mm_median"] = sorted(lengths)[len(lengths) // 2]
    return stats


def _verdict(combined_presences: int) -> str:
    if combined_presences < STOP_BELOW:
        return "species_not_viable"
    if combined_presences <= MARGINAL_MAX:
        return "marginal_proceed"
    return "viable_proceed"


def pilot_bbox_from_manifest() -> BBox:
    manifest = load_sources_manifest()
    pilot = manifest["pilot"]["bbox"]
    return BBox(
        lat_min=float(pilot["lat_min"]),
        lat_max=float(pilot["lat_max"]),
        lon_min=float(pilot["lon_min"]),
        lon_max=float(pilot["lon_max"]),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Adult CPS species viability gate (public catch only)")
    parser.add_argument("--species", default="Merluccius productus")
    parser.add_argument("--trawl-catch", type=Path, required=True)
    parser.add_argument("--nearshore-catch", type=Path, required=True)
    parser.add_argument("--trawl-specimen", type=Path, default=None)
    parser.add_argument("--nearshore-specimen", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument(
        "--data-provenance",
        default="NOAA SWFSC FRD CPS CSV (GCS nmfs_odp_swfsc mirror; ERDDAP tabledap when reachable)",
    )
    args = parser.parse_args(argv)

    bbox = pilot_bbox_from_manifest()
    trawl = _count_trawl(args.trawl_catch, args.species, bbox)
    near = _count_nearshore(args.nearshore_catch, args.species, bbox)
    combined = trawl["non_presence_only_presences_pilot"] + near["presences_pilot"]

    payload: dict[str, Any] = {
        "species_scientific": args.species,
        "common_name": "Pacific hake",
        "pilot_bbox": {
            "lat_min": bbox.lat_min,
            "lat_max": bbox.lat_max,
            "lon_min": bbox.lon_min,
            "lon_max": bbox.lon_max,
        },
        "gate_thresholds": {
            "stop_below_presences": STOP_BELOW,
            "marginal_upper_presences": MARGINAL_MAX,
        },
        "data_provenance": args.data_provenance,
        "public_sources": {
            "trawl_haul_catch_gcs": GCS_TRAWL_CATCH,
            "nearshore_set_catch_gcs": GCS_NEARSHORE_CATCH,
            "trawl_specimen_gcs": GCS_TRAWL_SPECIMEN,
            "nearshore_specimen_gcs": GCS_NEARSHORE_SPECIMEN,
            "erddap_trawl_catch": "https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSTrawlLHHaulCatch.csv",
            "erddap_nearshore_catch": "https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSNearshoreSetCatch.csv",
        },
        "counts": {
            "trawl": trawl,
            "nearshore": near,
            "combined_non_presence_only_presences_pilot": combined,
        },
        "verdict": _verdict(combined),
    }

    if args.trawl_specimen and args.trawl_specimen.is_file():
        payload["specimen_length_availability"] = {
            "trawl": _specimen_stats(args.trawl_specimen, args.species, bbox),
        }
    if args.nearshore_specimen and args.nearshore_specimen.is_file():
        payload.setdefault("specimen_length_availability", {})["nearshore"] = _specimen_stats(
            args.nearshore_specimen, args.species, bbox
        )

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "combined_presences_pilot": combined}, indent=2))
    return 0 if payload["verdict"] != "species_not_viable" else 2


if __name__ == "__main__":
    raise SystemExit(main())
