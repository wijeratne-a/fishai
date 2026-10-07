#!/usr/bin/env python3
"""Phase-1 viability gate: count non-presence-only presences for one CPS species (pilot bbox)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def _in_bbox(lat: float | None, lon: float | None, bbox) -> bool:
    if lat is None or lon is None:
        return False
    return bbox.lat_min <= lat <= bbox.lat_max and bbox.lon_min <= lon <= bbox.lon_max


def _parse_float(text: str | None) -> float | None:
    if text is None:
        return None
    s = str(text).strip()
    if not s or s.lower() in {"nan", "na", ""}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.adult.gcs_mirror import (
        DEFAULT_MIRROR_DIR,
        GCS_NEARSHORE_SET_CATCH,
        GCS_TRAWL_HAUL_CATCH,
        download_gcs_csv,
        normalize_nearshore_set_catch_row,
        normalize_trawl_haul_catch_row,
    )
    from fishai.ingestion.biology.cps_trawl.catch import merge_catch_values, parse_catch_row
    from fishai.ingestion.biology.cps_trawl.pipeline import pilot_bbox_from_manifest
    from fishai.ingestion.biology.cps_trawl.taxonomy import species_name_matches_target

    parser = argparse.ArgumentParser(description="Adult CPS species viability gate (public GCS mirror)")
    parser.add_argument("--species", default="Clupea pallasii", help="Target scientific name")
    parser.add_argument("--mirror-dir", type=Path, default=DEFAULT_MIRROR_DIR)
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args(argv)

    target = args.species.strip()
    bbox = pilot_bbox_from_manifest()
    mirror = args.mirror_dir
    trawl_path = mirror / "CPS_Trawl_LifeHistory_HaulCatch.csv"
    near_path = mirror / "CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv"

    if not args.skip_download:
        print(f"download trawl haul catch -> {trawl_path}")
        download_gcs_csv(GCS_TRAWL_HAUL_CATCH, trawl_path)
        print(f"download nearshore set catch -> {near_path}")
        download_gcs_csv(GCS_NEARSHORE_SET_CATCH, near_path)

    # --- Trawl: merge collection splits per haul × species (same as sync pipeline) ---
    haul_rows: dict[str, list[dict]] = {}
    with trawl_path.open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = normalize_trawl_haul_catch_row(raw)
            lat = _parse_float(row.get("latitude"))
            lon = _parse_float(row.get("longitude"))
            if not _in_bbox(lat, lon, bbox):
                continue
            cruise = str(row.get("cruise") or "").strip()
            ship = str(row.get("ship") or "").strip()
            haul = str(row.get("haul") or "").strip()
            if not (cruise and ship and haul):
                continue
            haul_id = f"CPSTrawl:{cruise}:{ship}:{haul}"
            haul_rows.setdefault(haul_id, []).append(row)

    trawl_presence_only = 0
    trawl_non_po_presence = 0
    trawl_non_po_zero = 0
    for rows in haul_rows.values():
        by_species: dict[str, list] = {}
        for catch_row in rows:
            parsed = parse_catch_row(catch_row)
            if parsed is None:
                continue
            if not species_name_matches_target(parsed.species, target):
                continue
            by_species.setdefault(parsed.species, []).append(parsed)
        for parsed_rows in by_species.values():
            merged = merge_catch_values(parsed_rows)
            if merged.presence_only:
                trawl_presence_only += 1
                continue
            weight = merged.weight_kg
            count = merged.subsample_count
            if (weight is not None and weight > 0) or (count is not None and count > 0):
                trawl_non_po_presence += 1
            else:
                trawl_non_po_zero += 1

    # --- Nearshore: one row per set × species ---
    near_presence = 0
    near_zero = 0
    with near_path.open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = normalize_nearshore_set_catch_row(raw)
            lat = _parse_float(row.get("latitude"))
            lon = _parse_float(row.get("longitude"))
            if not _in_bbox(lat, lon, bbox):
                continue
            name = str(row.get("scientific_name") or "").strip()
            if not species_name_matches_target(name, target):
                continue
            n = _parse_float(row.get("totalNumber"))
            w = _parse_float(row.get("totalWeightkg"))
            ni = int(n) if n is not None else None
            if (w is not None and w > 0) or (ni is not None and ni > 0):
                near_presence += 1
            else:
                near_zero += 1

    total_non_po_presence = trawl_non_po_presence + near_presence
    if total_non_po_presence < 100:
        verdict = "species not viable"
    elif total_non_po_presence < 150:
        verdict = "marginal"
    else:
        verdict = "viable"

    out = {
        "species": target,
        "pilot_bbox": {
            "lat_min": bbox.lat_min,
            "lat_max": bbox.lat_max,
            "lon_min": bbox.lon_min,
            "lon_max": bbox.lon_max,
        },
        "data_source": "NOAA GCS mirror (InPort nmfs_odp_swfsc)",
        "trawl_haul_catch": {
            "presence_only_rows_excluded": trawl_presence_only,
            "non_presence_only_presences": trawl_non_po_presence,
            "non_presence_only_zero_catch_rows": trawl_non_po_zero,
        },
        "nearshore_set_catch": {
            "presences": near_presence,
            "zero_catch_rows": near_zero,
        },
        "total_non_presence_only_presences": total_non_po_presence,
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2))
    return 0 if verdict != "species not viable" else 2


if __name__ == "__main__":
    raise SystemExit(main())
