"""Sync pipeline: raw CSV → processed Parquet for CPS nearshore set catch."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from fishai.ingestion.biology.cps_nearshore.constants import (
    SET_SPECIES_MATRIX_FILENAME,
    PILOT_MATRIX_SPECIES,
    PILOT_SPECIES_ITIS_TSN,
    SOURCE_ID,
)
from fishai.ingestion.biology.cps_nearshore.matrix import expand_set_species_matrix
from fishai.ingestion.biology.cps_nearshore.zero_frame import DEFAULT_EVIDENCE_PATH
from fishai.ingestion.biology.cps_nearshore.fetch import (
    BBox,
    fetch_cps_nearshore_set_catch,
    iter_yearly_windows,
    raw_dir,
    read_cps_nearshore_csv,
)
from fishai.ingestion.biology.cps_nearshore.transform import (
    TransformResult,
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

QC_REPORT_FILENAME = "cps_nearshore_qc_report.json"
METADATA_FILENAME = "cps_nearshore_metadata.json"


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
    return REPO_ROOT / "data" / "processed" / "swfsc_cps_nearshore_set_catch"


def _table_from_records(records: list[dict[str, Any]]) -> Any:
    if pa is None:
        raise RuntimeError("pyarrow is required to write CPS nearshore parquet outputs")
    return pa.Table.from_pylist(records)


def set_meta_for_matrix(sets: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Per-set metadata required by ``expand_set_species_matrix`` zero-frame gates."""
    return [{"set_id": str(s["set_id"])} for s in sets]


def build_set_species_matrix(
    sets: Sequence[Mapping[str, Any]],
    catch: Sequence[Mapping[str, Any]],
    *,
    evidence_path: Path | None = None,
) -> list[dict[str, Any]]:
    set_ids = [str(s["set_id"]) for s in sets]
    return expand_set_species_matrix(
        catch,
        set_ids,
        list(PILOT_MATRIX_SPECIES),
        species_itis_tsn=PILOT_SPECIES_ITIS_TSN,
        set_meta=set_meta_for_matrix(sets),
        evidence_path=evidence_path,
        on_unverified="na",
    )


def write_parquet_contracts(
    sets: list[dict[str, Any]],
    catch: list[dict[str, Any]],
    matrix: list[dict[str, Any]],
    dest: Path,
) -> tuple[Path, Path, Path]:
    dest.mkdir(parents=True, exist_ok=True)
    sets_path = dest / "cps_nearshore_sets.parquet"
    catch_path = dest / "cps_nearshore_catch.parquet"
    matrix_path = dest / SET_SPECIES_MATRIX_FILENAME
    pq.write_table(_table_from_records(sets), sets_path)
    pq.write_table(_table_from_records(catch), catch_path)
    pq.write_table(_table_from_records(matrix), matrix_path)
    return sets_path, catch_path, matrix_path


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


def load_raw_rows_for_window(t0: date, t1: date, raw: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    files = 0
    paths = sorted(raw.glob("cps_nearshore_set_catch_*.csv"))
    if not paths:
        for win_start, _ in iter_yearly_windows(t0, t1):
            legacy = raw / f"cps_nearshore_set_catch_{win_start.year}.csv"
            if legacy.is_file():
                paths.append(legacy)
    for path in paths:
        files += 1
        window_rows, _ = read_cps_nearshore_csv(path)
        rows.extend(window_rows)
    return rows, files


def sync_cps_nearshore_set_catch(
    t0: date,
    t1: date,
    *,
    bbox: BBox | None = None,
    evidence_path: Path | None = None,
    download: bool = True,
) -> dict[str, Any]:
    """Fetch (optional), transform, and write processed nearshore set catch tables."""
    entry = require_approved(SOURCE_ID)
    raw = raw_dir()
    if download:
        fetch_cps_nearshore_set_catch(t0, t1, bbox, raw)
    rows, n_files = load_raw_rows_for_window(t0, t1, raw)
    result: TransformResult = transform_rows(rows)
    matrix = build_set_species_matrix(result.sets, result.catch, evidence_path=evidence_path)
    dest = processed_dir()
    sets_path, catch_path, matrix_path = write_parquet_contracts(
        result.sets, result.catch, matrix, dest
    )
    qc = {
        "source_id": SOURCE_ID,
        "erddap_dataset": entry.get("erddap_dataset"),
        "window": [t0.isoformat(), t1.isoformat()],
        "raw_files": n_files,
        "raw_rows": len(rows),
        "qc_summary": format_qc_summary(result),
        "matrix_rows": len(matrix),
        "matrix_encounters": sum(1 for r in matrix if r.get("encounter") == 1),
        "matrix_implied_zeros": sum(1 for r in matrix if r.get("encounter") == 0),
        "matrix_not_available": sum(1 for r in matrix if r.get("encounter") is None),
    }
    qc_path = write_qc_report(qc, dest)
    metadata = {
        "source_id": SOURCE_ID,
        "license_text": entry.get("license_text"),
        "attribution": entry.get("attribution"),
        "evidence_path": str(evidence_path or DEFAULT_EVIDENCE_PATH),
        "outputs": [str(sets_path), str(catch_path), str(matrix_path), str(qc_path)],
    }
    write_metadata(metadata, dest)
    return qc
