#!/usr/bin/env python3
"""Ingest CPS trawl + nearshore tables from NOAA GCS mirror CSVs (ERDDAP fallback)."""

from __future__ import annotations

import csv
import sys
from datetime import date
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


def _read_gcs_csv(path: Path, field_map: dict[str, str]) -> list[dict]:
    from fishai.ingestion.adult.gcs_mirror import map_gcs_row

    rows: list[dict] = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            rows.append(map_gcs_row(row, field_map))
    return rows


def _download(url: str, dest: Path) -> None:
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "fishai-cps-gcs-mirror/0.1"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        dest.write_bytes(resp.read())


def main() -> int:
    import pyarrow as pa
    import pyarrow.parquet as pq

    from fishai.ingestion.adult.constants import NEARSHORE_SPECIMENS_PATH, TRAWL_SPECIMENS_PATH
    from fishai.ingestion.adult.gcs_mirror import (
        GCS_NEARSHORE_CATCH_MAP,
        GCS_NEARSHORE_SPECIMEN_MAP,
        GCS_TRAWL_CATCH_MAP,
        GCS_TRAWL_SPECIMEN_MAP,
    )
    from fishai.ingestion.adult.specimens import (
        normalize_nearshore_specimens,
        normalize_trawl_specimens,
    )
    from fishai.ingestion.biology.cps_nearshore.pipeline import (
        build_set_species_matrix,
        pilot_bbox_from_manifest as near_bbox,
        processed_dir as near_processed,
        write_parquet_contracts as near_write,
        write_qc_report as near_write_qc,
    )
    from fishai.ingestion.biology.cps_nearshore.transform import transform_rows as near_transform
    from fishai.ingestion.biology.cps_trawl.pipeline import (
        build_haul_species_matrix,
        pilot_bbox_from_manifest,
        processed_dir as trawl_processed,
        write_metadata,
        write_parquet_contracts,
        write_qc_report,
    )
    from fishai.ingestion.biology.cps_trawl.transform import transform_rows as trawl_transform
    from fishai.ingestion.biology.cps_trawl.zero_frame import DEFAULT_EVIDENCE_PATH
    from fishai.ingestion.biology.cps_nearshore.constants import SOURCE_ID as NEAR_SOURCE
    from fishai.ingestion.biology.cps_trawl.constants import SOURCE_ID as TRAWL_SOURCE
    from fishai.ingestion.sources import REPO_ROOT as REPO, load_sources_manifest, require_approved

    mirror_dir = REPO / "data" / "raw" / "gcs_mirror"
    for key, fname in GCS_FILES.items():
        dest = mirror_dir / fname
        _download(f"{GCS_BASE}/{fname}", dest)
        print(f"staged {key} -> {dest} ({dest.stat().st_size} bytes)")

    bbox = pilot_bbox_from_manifest()
    trawl_rows = _read_gcs_csv(mirror_dir / GCS_FILES["trawl_catch"], GCS_TRAWL_CATCH_MAP)
    # Pilot bbox filter client-side (GCS file is full extent).
    filtered_trawl: list[dict] = []
    for row in trawl_rows:
        try:
            lat = float(row.get("latitude") or "")
            lon = float(row.get("longitude") or "")
        except ValueError:
            continue
        if bbox.lat_min <= lat <= bbox.lat_max and bbox.lon_min <= lon <= bbox.lon_max:
            filtered_trawl.append(row)
    trawl_out = trawl_transform(filtered_trawl, units_rows_skipped=0)
    manifest = load_sources_manifest()
    trawl_entry = (manifest.get("sources") or {}).get(TRAWL_SOURCE) or {}
    matrix = build_haul_species_matrix(trawl_out.hauls, trawl_out.catch)
    out = trawl_processed()
    write_parquet_contracts(trawl_out.hauls, trawl_out.catch, matrix, out)
    write_qc_report(trawl_out.qc_report, out)
    write_metadata(
        {
            "source_id": TRAWL_SOURCE,
            "ingest_path": "gcs_mirror",
            "n_hauls": len(trawl_out.hauls),
            "n_catch_rows": len(trawl_out.catch),
            "license_text": trawl_entry.get("license_text"),
        },
        out,
    )
    print(f"trawl hauls={len(trawl_out.hauls)} catch={len(trawl_out.catch)}")

    near_rows = _read_gcs_csv(mirror_dir / GCS_FILES["nearshore_catch"], GCS_NEARSHORE_CATCH_MAP)
    nb = near_bbox()
    filtered_near: list[dict] = []
    for row in near_rows:
        try:
            lat = float(row.get("latitude") or "")
            lon = float(row.get("longitude") or "")
        except ValueError:
            continue
        if nb.lat_min <= lat <= nb.lat_max and nb.lon_min <= lon <= nb.lon_max:
            filtered_near.append(row)
    near_t = near_transform(filtered_near)
    near_matrix = build_set_species_matrix(near_t.sets, near_t.catch)
    near_proc = near_processed()
    near_write(near_t.sets, near_t.catch, near_matrix, near_proc)
    near_write_qc({"gcs_mirror_rows": len(filtered_near), "sets": len(near_t.sets)}, near_proc)
    print(f"nearshore sets={len(near_t.sets)} catch={len(near_t.catch)}")

    trawl_spec = normalize_trawl_specimens(
        _read_gcs_csv(mirror_dir / GCS_FILES["trawl_specimen"], GCS_TRAWL_SPECIMEN_MAP)
    )
    TRAWL_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(trawl_spec), TRAWL_SPECIMENS_PATH)
    near_spec = normalize_nearshore_specimens(
        _read_gcs_csv(mirror_dir / GCS_FILES["nearshore_specimen"], GCS_NEARSHORE_SPECIMEN_MAP)
    )
    NEARSHORE_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(near_spec), NEARSHORE_SPECIMENS_PATH)
    print(f"specimens trawl={len(trawl_spec)} nearshore={len(near_spec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
