#!/usr/bin/env python3
"""Count non-presence-only presences for a species in pilot bbox (GCS or local CSV)."""

from __future__ import annotations

import argparse
import csv
import io
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

GCS_BASE = "https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division"

GCS_FILES = {
    "trawl_catch": "CPS_Trawl_LifeHistory_HaulCatch.csv",
    "trawl_specimen": "CPS_Trawl_LifeHistory_Specimen.csv",
    "nearshore_catch": "CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv",
    "nearshore_specimen": "CPS_Trawl_LifeHistory_Nearshore_Specimen.csv",
}


def _open_csv(source: str) -> io.TextIOBase:
    if source.startswith("http://") or source.startswith("https://"):
        req = urllib.request.Request(source, headers={"User-Agent": "fishai-viability/0.1"})
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = resp.read()
        return io.StringIO(data.decode("utf-8", errors="replace"))
    return Path(source).open(encoding="utf-8", errors="replace")


def _in_bbox(lat: float, lon: float, bbox: dict[str, float]) -> bool:
    return (
        bbox["lat_min"] <= lat <= bbox["lat_max"]
        and bbox["lon_min"] <= lon <= bbox["lon_max"]
    )


def _parse_erddap_time(raw: str) -> datetime | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        val = float(text)
    except ValueError:
        return None
    return datetime.fromtimestamp(val, tz=timezone.utc)


def _is_presence_only(raw: str) -> bool:
    return str(raw or "").strip().upper() in {"Y", "YES", "TRUE", "1"}


def _positive_catch(count_raw: str, weight_raw: str) -> bool:
    for raw in (count_raw, weight_raw):
        text = (raw or "").strip()
        if not text:
            continue
        try:
            val = float(text)
        except ValueError:
            continue
        if val > 0:
            return True
    return False


def _field(row: dict[str, str], *names: str) -> str:
    for name in names:
        if name in row and row[name] is not None:
            return str(row[name])
        lower = name.casefold()
        for key, val in row.items():
            if key.casefold() == lower:
                return str(val)
    return ""


def _name_matches(scientific_name: str, target: str) -> bool:
    norm = " ".join(scientific_name.strip().split()).casefold()
    target_norm = " ".join(target.strip().split()).casefold()
    if norm == target_norm:
        return True
    parts = norm.split()
    if len(parts) >= 2 and f"{parts[0]} {parts[1]}" == target_norm:
        return True
    return False


def count_trawl_catch(reader: csv.DictReader, *, species: str, bbox: dict[str, float]) -> dict[str, int]:
    stats = {
        "rows_in_bbox": 0,
        "presence_only_rows": 0,
        "zero_catch_rows": 0,
        "presences": 0,
        "name_variants": 0,
    }
    variants: set[str] = set()
    for row in reader:
        try:
            lat = float(_field(row, "latitude", "startLatitude", "Latitude") or "")
            lon = float(_field(row, "longitude", "startLongitude", "Longitude") or "")
        except ValueError:
            continue
        if not _in_bbox(lat, lon, bbox):
            continue
        name = _field(row, "scientific_name", "scientificName")
        if not _name_matches(name, species):
            continue
        stats["rows_in_bbox"] += 1
        variants.add(name.strip())
        if _is_presence_only(_field(row, "presence_only", "presenceOnly")):
            stats["presence_only_rows"] += 1
            continue
        count = _field(row, "subsample_count", "subSampleCount")
        if not _positive_catch(count, _field(row, "remaining_weight", "remainingWeightkg")) and not _positive_catch(
            count, _field(row, "subsample_weight", "subSampleWeightkg")
        ):
            stats["zero_catch_rows"] += 1
            continue
        stats["presences"] += 1
    stats["name_variants"] = len(variants)
    return stats


def count_nearshore_catch(reader: csv.DictReader, *, species: str, bbox: dict[str, float]) -> dict[str, int]:
    stats = {
        "rows_in_bbox": 0,
        "zero_catch_rows": 0,
        "presences": 0,
        "name_variants": 0,
    }
    variants: set[str] = set()
    for row in reader:
        try:
            lat = float(_field(row, "latitude", "Latitude") or "")
            lon = float(_field(row, "longitude", "Longitude") or "")
        except ValueError:
            continue
        if not _in_bbox(lat, lon, bbox):
            continue
        name = _field(row, "scientific_name", "scientificName")
        if not _name_matches(name, species):
            continue
        stats["rows_in_bbox"] += 1
        variants.add(name.strip())
        if not _positive_catch(_field(row, "totalNumber"), _field(row, "totalWeightkg")):
            stats["zero_catch_rows"] += 1
            continue
        stats["presences"] += 1
    stats["name_variants"] = len(variants)
    return stats


def count_specimens(reader: csv.DictReader, *, species: str, bbox: dict[str, float]) -> dict[str, int]:
    stats = {"specimens_in_bbox": 0, "with_standard_length": 0, "with_fork_length": 0}
    for row in reader:
        try:
            lat = float(_field(row, "latitude", "startLatitude", "Latitude") or "")
            lon = float(_field(row, "longitude", "startLongitude", "Longitude") or "")
        except ValueError:
            continue
        if not _in_bbox(lat, lon, bbox):
            continue
        if not _name_matches(_field(row, "scientific_name", "scientificName"), species):
            continue
        stats["specimens_in_bbox"] += 1
        if _field(row, "standard_length", "standardLength").strip():
            stats["with_standard_length"] += 1
        if _field(row, "fork_length", "forkLength").strip():
            stats["with_fork_length"] += 1
    return stats


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.biology.cps_trawl.pipeline import pilot_bbox_from_manifest

    parser = argparse.ArgumentParser()
    parser.add_argument("--species", default="Trachurus symmetricus")
    parser.add_argument("--use-gcs", action="store_true", help="Stream from NOAA GCS mirror")
    parser.add_argument(
        "--local-dir",
        type=Path,
        help="Directory with GCS mirror CSV filenames (overrides --use-gcs)",
    )
    args = parser.parse_args(argv)

    box = pilot_bbox_from_manifest()
    bbox = {"lat_min": box.lat_min, "lat_max": box.lat_max, "lon_min": box.lon_min, "lon_max": box.lon_max}

    def src(key: str) -> str:
        if args.local_dir is not None:
            return str(args.local_dir / GCS_FILES[key])
        if args.use_gcs:
            return f"{GCS_BASE}/{GCS_FILES[key]}"
        raise SystemExit("pass --use-gcs or --local-dir")

    with _open_csv(src("trawl_catch")) as fh:
        trawl = count_trawl_catch(csv.DictReader(fh), species=args.species, bbox=bbox)
    with _open_csv(src("nearshore_catch")) as fh:
        near = count_nearshore_catch(csv.DictReader(fh), species=args.species, bbox=bbox)
    with _open_csv(src("trawl_specimen")) as fh:
        trawl_spec = count_specimens(csv.DictReader(fh), species=args.species, bbox=bbox)
    with _open_csv(src("nearshore_specimen")) as fh:
        near_spec = count_specimens(csv.DictReader(fh), species=args.species, bbox=bbox)

    total_presences = trawl["presences"] + near["presences"]
    print(f"species={args.species}")
    print(f"pilot_bbox={bbox}")
    print(f"trawl_non_po_presences={trawl['presences']}")
    print(f"trawl_presence_only_excluded={trawl['presence_only_rows']}")
    print(f"trawl_zero_catch_in_species_rows={trawl['zero_catch_rows']}")
    print(f"nearshore_presences={near['presences']}")
    print(f"total_non_po_presences={total_presences}")
    print(f"trawl_specimens={trawl_spec}")
    print(f"nearshore_specimens={near_spec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
