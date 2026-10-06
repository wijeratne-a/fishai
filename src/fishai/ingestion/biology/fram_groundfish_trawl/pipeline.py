"""Sync pipeline: raw FRAM JSON → processed Parquet (pelagic bycatch corroboration)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fishai.ingestion.biology.fram_groundfish_trawl.constants import (
    API_BASE,
    PELAGIC_BYCATCH_BIAS_NOTE,
    SOURCE_ID,
)
from fishai.ingestion.biology.fram_groundfish_trawl.fetch import (
    BBox,
    fetch_operation_hauls,
    fetch_pelagic_bycatch_catch,
    load_raw_catch_for_window,
    load_raw_hauls_for_window,
    raw_dir,
)
from fishai.ingestion.biology.fram_groundfish_trawl.transform import (
    format_qc_summary,
    transform_rows,
)
from fishai.ingestion.sources import REPO_ROOT, load_sources_manifest, require_approved

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:  # pragma: no cover
    pa = None  # type: ignore[assignment]
    pq = None  # type: ignore[assignment]

QC_REPORT_FILENAME = "fram_groundfish_trawl_qc_report.json"
METADATA_FILENAME = "fram_groundfish_trawl_metadata.json"


def pilot_bbox_from_manifest(manifest_path: Path | None = None) -> BBox:
    data = load_sources_manifest(manifest_path)
    pilot = data.get("pilot") or {}
    box = pilot.get("bbox") or {}
    return BBox(
        float(box["lat_min"]),
        float(box["lat_max"]),
        float(box["lon_min"]),
        float(box["lon_max"]),
    )


def processed_dir() -> Path:
    return REPO_ROOT / "data" / "processed" / "nwfsc_fram_groundfish_trawl"


def _table_from_records(records: list[dict[str, Any]]) -> Any:
    if pa is None:
        raise RuntimeError("pyarrow is required to write FRAM groundfish trawl parquet outputs")
    return pa.Table.from_pylist(records)


def write_parquet_contracts(
    hauls: list[dict[str, Any]],
    catch: list[dict[str, Any]],
    dest: Path,
) -> tuple[Path, Path]:
    dest.mkdir(parents=True, exist_ok=True)
    hauls_path = dest / "fram_groundfish_trawl_hauls.parquet"
    catch_path = dest / "fram_groundfish_trawl_pelagic_bycatch.parquet"
    pq.write_table(_table_from_records(hauls), hauls_path)
    pq.write_table(_table_from_records(catch), catch_path)
    return hauls_path, catch_path


def write_qc_report(report: dict[str, Any], dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / QC_REPORT_FILENAME
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_metadata(metadata: dict[str, Any], dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / METADATA_FILENAME
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def sync_fram_groundfish_trawl(
    start: date,
    end: date,
    *,
    fetch: bool = True,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Fetch (optional), transform, and write processed parquet under ``data/processed/``."""
    require_approved(SOURCE_ID, path=manifest_path)
    manifest = load_sources_manifest(manifest_path)
    source_entry = (manifest.get("sources") or {}).get(SOURCE_ID) or {}
    raw = raw_dir()
    fetched: list[str] = []
    if fetch:
        for path in fetch_pelagic_bycatch_catch(start, end, dest_dir=raw, manifest_path=manifest_path):
            fetched.append(str(path))
        for path in fetch_operation_hauls(start, end, dest_dir=raw, manifest_path=manifest_path):
            fetched.append(str(path))

    catch_rows = load_raw_catch_for_window(start, end, raw)
    haul_rows = load_raw_hauls_for_window(start, end, raw)
    transformed = transform_rows(catch_rows, haul_rows)
    qc_report = transformed.qc_report
    qc_report["qc_summary"] = format_qc_summary(qc_report)
    qc_report["window"] = [start.isoformat(), end.isoformat()]

    out = processed_dir()
    hauls_path, catch_path = write_parquet_contracts(transformed.hauls, transformed.catch, out)
    qc_path = write_qc_report(qc_report, out)
    metadata = {
        "source_id": SOURCE_ID,
        "api_base": API_BASE,
        "license_text": source_entry.get("license_text"),
        "license_url": source_entry.get("license_url"),
        "attribution": source_entry.get("attribution"),
        "pelagic_bycatch_bias": PELAGIC_BYCATCH_BIAS_NOTE,
        "training_role": "adult_corroboration_only",
        "presence_only_bycatch": True,
        "implied_zeros": False,
        "survey_year_derivation": "first_four_digits_of_trawl_id",
        "effort_fields": {
            "area_swept_ha": "area_swept_ha_der",
            "cpue_kg_per_ha": "cpue_kg_per_ha_der",
        },
    }
    meta_path = write_metadata(metadata, out)
    return {
        "hauls_path": str(hauls_path),
        "catch_path": str(catch_path),
        "qc_report_path": str(qc_path),
        "metadata_path": str(meta_path),
        "qc_report": qc_report,
        "n_hauls": len(transformed.hauls),
        "n_catch_rows": len(transformed.catch),
        "fetched_files": fetched,
    }
