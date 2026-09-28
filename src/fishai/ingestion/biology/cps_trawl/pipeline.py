"""Sync pipeline: raw CSV → processed Parquet."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fishai.ingestion.biology.cps_trawl.constants import DEFAULT_ZERO_FRAME_STATUS, SOURCE_ID
from fishai.ingestion.biology.cps_trawl.fetch import (
    BBox,
    fetch_cps_trawl_haul_catch,
    iter_yearly_windows,
    read_cps_trawl_csv,
)
from fishai.ingestion.biology.cps_trawl.transform import transform_rows
from fishai.ingestion.sources import REPO_ROOT, load_sources_manifest, require_approved

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:  # pragma: no cover
    pa = None  # type: ignore[assignment]
    pq = None  # type: ignore[assignment]

QC_REPORT_FILENAME = "cps_trawl_qc_report.json"
METADATA_FILENAME = "cps_trawl_metadata.json"


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
    return REPO_ROOT / "data" / "processed" / "swfsc_cps_trawl_haul_catch"


def _table_from_records(records: list[dict[str, Any]]) -> Any:
    if pa is None:
        raise RuntimeError("pyarrow is required to write CPS trawl parquet outputs")
    return pa.Table.from_pylist(records)


def write_parquet_contracts(
    hauls: list[dict[str, Any]],
    catch: list[dict[str, Any]],
    dest: Path,
) -> tuple[Path, Path]:
    dest.mkdir(parents=True, exist_ok=True)
    hauls_path = dest / "cps_trawl_hauls.parquet"
    catch_path = dest / "cps_trawl_catch.parquet"
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


def load_raw_rows_for_window(t0: date, t1: date, raw_dir: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    units_skipped = 0
    for win_start, _ in iter_yearly_windows(t0, t1):
        path = raw_dir / f"FRDCPSTrawlLHHaulCatch_{win_start.year}.csv"
        if path.is_file():
            chunk, skipped = read_cps_trawl_csv(path)
            rows.extend(chunk)
            units_skipped += skipped
    return rows, units_skipped


def format_qc_summary(report: dict[str, Any]) -> str:
    dropped = report.get("dropped_by_rule") or {}
    parts = [
        f"catch_rows_read={report.get('catch_rows_read', 0)}",
        f"hauls_kept={report.get('hauls_kept', 0)}",
        f"catch_rows_kept={report.get('catch_rows_kept', 0)}",
    ]
    for key, count in sorted(dropped.items()):
        if count:
            parts.append(f"{key}={count}")
    return "qc " + " ".join(parts)


def sync_cps_trawl_haul_catch(
    start: date,
    end: date,
    *,
    fetch: bool = True,
    bbox: BBox | None = None,
    manifest_path: Path | None = None,
    zero_frame_status: str = DEFAULT_ZERO_FRAME_STATUS,
) -> dict[str, Any]:
    """Fetch (optional), transform, and write processed parquet under data/processed/."""
    require_approved(SOURCE_ID, path=manifest_path)
    manifest = load_sources_manifest(manifest_path)
    source_entry = (manifest.get("sources") or {}).get(SOURCE_ID) or {}
    raw = REPO_ROOT / "data" / "raw" / "swfsc_cps_trawl_haul_catch"
    fetched: list[Path] = []
    if fetch:
        fetched = fetch_cps_trawl_haul_catch(
            start,
            end,
            bbox,
            dest_dir=raw,
            manifest_path=manifest_path,
        )
    rows, units_skipped = load_raw_rows_for_window(start, end, raw)
    transformed = transform_rows(rows, units_rows_skipped=units_skipped)
    hauls = transformed.hauls
    catch = transformed.catch
    qc_report = transformed.qc_report
    qc_report["zero_frame_status"] = zero_frame_status
    out = processed_dir()
    hauls_path, catch_path = write_parquet_contracts(hauls, catch, out)
    qc_path = write_qc_report(qc_report, out)
    metadata = {
        "source_id": SOURCE_ID,
        "erddap_dataset": "FRDCPSTrawlLHHaulCatch",
        "license_text": source_entry.get("license_text"),
        "license_url": source_entry.get("license_url"),
        "attribution": source_entry.get("attribution"),
        "zero_frame_status": zero_frame_status,
        "effort_fields": {
            "net_mouth_area_m2": "not_in_source_dataset",
            "tow_distance_nm": "computed_from_start_stop_coordinates_when_present",
            "tow_duration_min": "computed_from_time_and_haulback_time",
        },
    }
    meta_path = write_metadata(metadata, out)
    return {
        "hauls_path": str(hauls_path),
        "catch_path": str(catch_path),
        "qc_report_path": str(qc_path),
        "metadata_path": str(meta_path),
        "qc_report": qc_report,
        "n_hauls": len(hauls),
        "n_catch_rows": len(catch),
        "fetched_files": [str(p) for p in fetched],
    }
