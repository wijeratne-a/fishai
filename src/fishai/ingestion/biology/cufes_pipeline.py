"""Sync pipeline: raw CSV → processed Parquet (+ optional DwC)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from fishai.ingestion.biology.cufes_constants import SOURCE_ID
from fishai.ingestion.biology.cufes_dwc import write_dwc_triplet
from fishai.ingestion.biology.cufes_fetch import BBox, fetch_cufes, iter_yearly_windows, read_cufes_csv
from fishai.ingestion.biology.cufes_transform import transform_rows
from fishai.ingestion.sources import REPO_ROOT, load_sources_manifest, require_approved

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:  # pragma: no cover - exercised when pyarrow installed
    pa = None  # type: ignore[assignment]
    pq = None  # type: ignore[assignment]


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
    return REPO_ROOT / "data" / "processed" / "calcofi_cufes"


def _table_from_records(records: list[dict[str, Any]]) -> Any:
    if pa is None:
        raise RuntimeError("pyarrow is required to write CUFES parquet outputs")
    return pa.Table.from_pylist(records)


def write_parquet_contracts(events: list[dict[str, Any]], counts: list[dict[str, Any]], dest: Path) -> tuple[Path, Path]:
    dest.mkdir(parents=True, exist_ok=True)
    events_path = dest / "cufes_events.parquet"
    counts_path = dest / "cufes_counts.parquet"
    pq.write_table(_table_from_records(events), events_path)
    pq.write_table(_table_from_records(counts), counts_path)
    return events_path, counts_path


def load_raw_rows_for_window(t0: date, t1: date, raw_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for win_start, _ in iter_yearly_windows(t0, t1):
        path = raw_dir / f"erdCalCOFIcufes_{win_start.year}.csv"
        if path.is_file():
            rows.extend(read_cufes_csv(path))
    return rows


def sync_cufes(
    start: date,
    end: date,
    *,
    fetch: bool = True,
    bbox: BBox | None = None,
    write_dwc: bool = False,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Fetch (optional), transform, and write processed parquet under data/processed/."""
    require_approved(SOURCE_ID, path=manifest_path)
    box = bbox or pilot_bbox_from_manifest(manifest_path)
    raw = REPO_ROOT / "data" / "raw" / "calcofi_cufes"
    fetched: list[Path] = []
    if fetch:
        fetched = fetch_cufes(start, end, box, dest_dir=raw, manifest_path=manifest_path)
    rows = load_raw_rows_for_window(start, end, raw)
    events, counts = transform_rows(rows)
    out = processed_dir()
    events_path, counts_path = write_parquet_contracts(events, counts, out)
    result: dict[str, Any] = {
        "events_path": str(events_path),
        "counts_path": str(counts_path),
        "n_events": len(events),
        "n_occurrence_rows": len(counts),
        "fetched_files": [str(p) for p in fetched],
    }
    if write_dwc:
        dwc_dir = out / "dwc"
        paths = write_dwc_triplet(events, counts, dwc_dir)
        result["dwc_paths"] = [str(p) for p in paths]
    return result
