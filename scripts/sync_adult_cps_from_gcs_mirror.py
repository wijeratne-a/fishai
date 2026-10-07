#!/usr/bin/env python3
"""Sync adult CPS catch + specimen inputs from NOAA public GCS mirrors (ERDDAP 504 fallback)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.adult.constants import NEARSHORE_SPECIMENS_PATH, TRAWL_SPECIMENS_PATH
    from fishai.ingestion.adult.gcs_mirror import (
        NEARSHORE_SET_CATCH_URL,
        NEARSHORE_SPECIMEN_URL,
        TRAWL_HAUL_CATCH_URL,
        TRAWL_SPECIMEN_URL,
        download_public_csv,
        gcs_raw_dir,
        in_pilot_bbox,
        iter_gcs_csv_rows,
        normalize_nearshore_set_gcs_row,
        normalize_nearshore_specimen_gcs_row,
        normalize_trawl_haul_gcs_row,
        normalize_trawl_specimen_gcs_row,
    )
    from fishai.ingestion.adult.specimens import (
        normalize_nearshore_specimens,
        normalize_trawl_specimens,
    )
    from fishai.ingestion.biology.cps_nearshore.pipeline import (
        build_set_species_matrix,
        pilot_bbox_from_manifest as near_bbox,
        processed_dir as near_processed,
        write_metadata as near_write_metadata,
        write_parquet_contracts as near_write_parquet,
        write_qc_report as near_write_qc,
    )
    from fishai.ingestion.biology.cps_nearshore.transform import transform_rows as near_transform
    from fishai.ingestion.biology.cps_nearshore.zero_frame import DEFAULT_EVIDENCE_PATH as near_evidence
    from fishai.ingestion.biology.cps_trawl.pipeline import (
        build_haul_species_matrix,
        pilot_bbox_from_manifest,
        processed_dir as trawl_processed,
        write_metadata as trawl_write_metadata,
        write_parquet_contracts as trawl_write_parquet,
        write_qc_report as trawl_write_qc,
    )
    from fishai.ingestion.biology.cps_trawl.transform import transform_rows as trawl_transform
    from fishai.ingestion.biology.cps_trawl.zero_frame import DEFAULT_EVIDENCE_PATH as trawl_evidence
    from fishai.ingestion.sources import load_sources_manifest, require_approved

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("pyarrow is required") from exc

    parser = argparse.ArgumentParser(description="Sync CPS inputs from NOAA GCS CSV mirrors")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args(argv)

    require_approved("swfsc_cps_trawl_haul_catch")
    require_approved("swfsc_cps_nearshore_set_catch")
    bbox = pilot_bbox_from_manifest()
    raw = gcs_raw_dir()

    def _bbox_dict(box) -> dict[str, float]:
        return {
            "lat_min": box.lat_min,
            "lat_max": box.lat_max,
            "lon_min": box.lon_min,
            "lon_max": box.lon_max,
        }

    paths = {
        "trawl_haul": raw / "CPS_Trawl_LifeHistory_HaulCatch.csv",
        "trawl_specimen": raw / "CPS_Trawl_LifeHistory_Specimen.csv",
        "nearshore_set": raw / "CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv",
        "nearshore_specimen": raw / "CPS_Trawl_LifeHistory_Nearshore_Specimen.csv",
    }
    urls = {
        "trawl_haul": TRAWL_HAUL_CATCH_URL,
        "trawl_specimen": TRAWL_SPECIMEN_URL,
        "nearshore_set": NEARSHORE_SET_CATCH_URL,
        "nearshore_specimen": NEARSHORE_SPECIMEN_URL,
    }
    if not args.skip_download:
        for key, dest in paths.items():
            print(f"download {key} -> {dest}")
            download_public_csv(urls[key], dest)

    trawl_rows: list[dict] = []
    for row in iter_gcs_csv_rows(paths["trawl_haul"]):
        if not in_pilot_bbox(row, bbox, lat_key="startLatitude", lon_key="startLongitude"):
            continue
        trawl_rows.append(normalize_trawl_haul_gcs_row(row))
    trawl_result = trawl_transform(trawl_rows, units_rows_skipped=0)
    trawl_matrix = build_haul_species_matrix(
        trawl_result.hauls, trawl_result.catch, evidence_path=trawl_evidence
    )
    trawl_out = trawl_processed()
    trawl_write_parquet(trawl_result.hauls, trawl_result.catch, trawl_matrix, trawl_out)
    trawl_write_qc(trawl_result.qc_report, trawl_out)
    manifest = load_sources_manifest()
    trawl_entry = (manifest.get("sources") or {}).get("swfsc_cps_trawl_haul_catch") or {}
    trawl_write_metadata(
        {
            "source_id": "swfsc_cps_trawl_haul_catch",
            "ingest_path": "gcs_mirror",
            "gcs_url": TRAWL_HAUL_CATCH_URL,
            "pilot_bbox": _bbox_dict(bbox),
            "license_text": trawl_entry.get("license_text"),
            "attribution": trawl_entry.get("attribution"),
        },
        trawl_out,
    )
    print(
        f"trawl pilot hauls={len(trawl_result.hauls)} catch_rows={len(trawl_result.catch)} "
        f"raw_pilot_rows={len(trawl_rows)}"
    )

    near_rows: list[dict] = []
    nb = near_bbox()
    for row in iter_gcs_csv_rows(paths["nearshore_set"]):
        if not in_pilot_bbox(row, nb, lat_key="Latitude", lon_key="Longitude"):
            continue
        near_rows.append(normalize_nearshore_set_gcs_row(row))
    near_result = near_transform(near_rows)
    near_matrix = build_set_species_matrix(near_result.sets, near_result.catch, evidence_path=near_evidence)
    near_out = near_processed()
    near_write_parquet(near_result.sets, near_result.catch, near_matrix, near_out)
    near_qc = {
        "source_id": "swfsc_cps_nearshore_set_catch",
        "ingest_path": "gcs_mirror",
        "gcs_url": NEARSHORE_SET_CATCH_URL,
        "raw_pilot_rows": len(near_rows),
        "sets_kept": len(near_result.sets),
        "catch_rows_kept": len(near_result.catch),
    }
    near_write_qc(near_qc, near_out)
    near_entry = (manifest.get("sources") or {}).get("swfsc_cps_nearshore_set_catch") or {}
    near_write_metadata(
        {
            "source_id": "swfsc_cps_nearshore_set_catch",
            "ingest_path": "gcs_mirror",
            "gcs_url": NEARSHORE_SET_CATCH_URL,
            "pilot_bbox": _bbox_dict(nb),
            "license_text": near_entry.get("license_text"),
            "attribution": near_entry.get("attribution"),
        },
        near_out,
    )
    print(f"nearshore pilot sets={len(near_result.sets)} catch_rows={len(near_result.catch)}")

    trawl_spec_rows: list[dict] = []
    for row in iter_gcs_csv_rows(paths["trawl_specimen"]):
        if not in_pilot_bbox(row, bbox, lat_key="Latitude", lon_key="Longitude"):
            continue
        trawl_spec_rows.append(normalize_trawl_specimen_gcs_row(row))
    trawl_spec_df = normalize_trawl_specimens(trawl_spec_rows)
    TRAWL_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(trawl_spec_df), TRAWL_SPECIMENS_PATH)

    near_spec_rows: list[dict] = []
    for row in iter_gcs_csv_rows(paths["nearshore_specimen"]):
        if not in_pilot_bbox(row, nb, lat_key="Latitude", lon_key="Longitude"):
            continue
        near_spec_rows.append(normalize_nearshore_specimen_gcs_row(row))
    near_spec_df = normalize_nearshore_specimens(near_spec_rows)
    NEARSHORE_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(near_spec_df), NEARSHORE_SPECIMENS_PATH)
    print(f"specimens trawl={len(trawl_spec_df)} nearshore={len(near_spec_df)}")

    summary = {
        "ingest": "gcs_mirror",
        "pilot_bbox": _bbox_dict(bbox),
        "trawl_hauls": len(trawl_result.hauls),
        "trawl_catch_rows": len(trawl_result.catch),
        "nearshore_sets": len(near_result.sets),
        "nearshore_catch_rows": len(near_result.catch),
        "trawl_specimens": len(trawl_spec_df),
        "nearshore_specimens": len(near_spec_df),
    }
    summary_path = REPO_ROOT / "data" / "processed" / "adult_cps_gcs_mirror_sync.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"summary={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
