#!/usr/bin/env python3
"""Ingest NOAA GCS CPS CSV mirrors into herring-domain processed parquets (public data only)."""

from __future__ import annotations

import csv
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pyarrow is required") from exc


def _bbox_filter(row: dict, bbox) -> bool:
    lat = row.get("latitude")
    lon = row.get("longitude")
    try:
        la = float(lat)
        lo = float(lon)
    except (TypeError, ValueError):
        return False
    return bbox.lat_min <= la <= bbox.lat_max and bbox.lon_min <= lo <= bbox.lon_max


def main() -> int:
    from fishai.ingestion.adult.constants import HERRING_PROCESSED_DIR
    from fishai.ingestion.adult.gcs_mirror import (
        DEFAULT_MIRROR_DIR,
        GCS_NEARSHORE_SET_CATCH,
        GCS_NEARSHORE_SPECIMEN,
        GCS_TRAWL_HAUL_CATCH,
        GCS_TRAWL_SPECIMEN,
        download_gcs_csv,
        normalize_nearshore_set_catch_row,
        normalize_nearshore_specimen_row,
        normalize_trawl_haul_catch_row,
        normalize_trawl_specimen_row,
    )
    from fishai.ingestion.adult.specimens import (
        normalize_nearshore_specimens,
        normalize_trawl_specimens,
    )
    from fishai.ingestion.biology.cps_nearshore.pipeline import (
        build_set_species_matrix,
        write_parquet_contracts as write_near_parquet,
    )
    from fishai.ingestion.biology.cps_nearshore.transform import transform_rows as near_transform
    from fishai.ingestion.biology.cps_trawl.fetch import BBox
    from fishai.ingestion.biology.cps_trawl.pipeline import (
        build_haul_species_matrix,
        write_parquet_contracts as write_trawl_parquet,
    )
    from fishai.ingestion.biology.cps_trawl.transform import transform_rows as trawl_transform

    domain_path = REPO_ROOT / "config" / "adult_pacific_herring_domain.json"
    domain = json.loads(domain_path.read_text(encoding="utf-8"))
    box = domain["bbox"]
    bbox = BBox(float(box["lat_min"]), float(box["lat_max"]), float(box["lon_min"]), float(box["lon_max"]))

    mirror = DEFAULT_MIRROR_DIR
    mirror.mkdir(parents=True, exist_ok=True)
    paths = {
        "trawl_catch": mirror / "CPS_Trawl_LifeHistory_HaulCatch.csv",
        "trawl_spec": mirror / "CPS_Trawl_LifeHistory_Specimen.csv",
        "near_catch": mirror / "CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv",
        "near_spec": mirror / "CPS_Trawl_LifeHistory_Nearshore_Specimen.csv",
    }
    for url, dest in (
        (GCS_TRAWL_HAUL_CATCH, paths["trawl_catch"]),
        (GCS_TRAWL_SPECIMEN, paths["trawl_spec"]),
        (GCS_NEARSHORE_SET_CATCH, paths["near_catch"]),
        (GCS_NEARSHORE_SPECIMEN, paths["near_spec"]),
    ):
        if not dest.is_file():
            print(f"download {dest.name}")
            download_gcs_csv(url, dest)

    trawl_rows: list[dict] = []
    with paths["trawl_catch"].open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = normalize_trawl_haul_catch_row(raw)
            if _bbox_filter(row, bbox):
                trawl_rows.append(row)
    trawl_res = trawl_transform(trawl_rows, units_rows_skipped=0)
    trawl_out = HERRING_PROCESSED_DIR / "swfsc_cps_trawl_haul_catch"
    matrix = build_haul_species_matrix(trawl_res.hauls, trawl_res.catch)
    write_trawl_parquet(trawl_res.hauls, trawl_res.catch, matrix, trawl_out)
    print(f"trawl hauls={len(trawl_res.hauls)} catch={len(trawl_res.catch)}")

    near_rows: list[dict] = []
    with paths["near_catch"].open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = normalize_nearshore_set_catch_row(raw)
            if _bbox_filter(row, bbox):
                near_rows.append(row)
    near_res = near_transform(near_rows)
    near_out = HERRING_PROCESSED_DIR / "swfsc_cps_nearshore_set_catch"
    near_matrix = build_set_species_matrix(near_res.sets, near_res.catch)
    write_near_parquet(near_res.sets, near_res.catch, near_matrix, near_out)
    print(f"nearshore sets={len(near_res.sets)} catch={len(near_res.catch)}")

    trawl_spec_recs = []
    with paths["trawl_spec"].open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = normalize_trawl_specimen_row(raw)
            if _bbox_filter(row, bbox):
                trawl_spec_recs.append(row)
    near_spec_recs = []
    with paths["near_spec"].open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = normalize_nearshore_specimen_row(raw)
            if _bbox_filter(row, bbox):
                near_spec_recs.append(row)
    trawl_spec_df = normalize_trawl_specimens(trawl_spec_recs)
    near_spec_df = normalize_nearshore_specimens(near_spec_recs)
    trawl_out.mkdir(parents=True, exist_ok=True)
    near_out.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(trawl_spec_df), trawl_out / "cps_trawl_specimens.parquet")
    pq.write_table(pa.Table.from_pandas(near_spec_df), near_out / "cps_nearshore_specimens.parquet")
    print(f"specimens trawl={len(trawl_spec_df)} near={len(near_spec_df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
