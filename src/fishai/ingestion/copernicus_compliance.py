"""Copernicus Marine licence compliance helpers (no credential access)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

GLORYS_CREDIT_TEXT = "Generated using E.U. Copernicus Marine Service Information"
GLORYS_DOI = "10.48670/moi-00021"

DEFAULT_PULL_LOG = REPO_ROOT / "data" / "interim" / "copernicus_pull_log.jsonl"


class GlorysAttributionError(RuntimeError):
    """Raised when GLORYS-derived export metadata lacks required credit/DOI."""


def glorys_attribution_bundle(entry: dict[str, Any]) -> dict[str, str]:
    """Build required attribution fields from a SOURCES.yaml entry."""
    credit = str(entry.get("copernicus_credit") or GLORYS_CREDIT_TEXT).strip()
    doi = str(entry.get("copernicus_doi") or GLORYS_DOI).strip()
    text = str(entry.get("attribution") or "").strip()
    return {
        "attribution": text,
        "copernicus_credit": credit,
        "copernicus_doi": doi,
    }


def require_glorys_attribution(metadata: dict[str, Any]) -> None:
    """
    Fail closed before rendering/exporting GLORYS-derived products.

    Any map layer, metadata export, or published artifact that includes GLORYS
    data must carry the mandated credit line and DOI.
    """
    if not metadata.get("glorys_derived"):
        return
    credit = str(metadata.get("copernicus_credit") or metadata.get("attribution") or "")
    doi = str(metadata.get("copernicus_doi") or "")
    combined = f"{credit} {doi} {metadata.get('attribution', '')}"
    if GLORYS_CREDIT_TEXT not in credit and GLORYS_CREDIT_TEXT not in combined:
        raise GlorysAttributionError(f"missing Copernicus credit: {GLORYS_CREDIT_TEXT!r}")
    if GLORYS_DOI not in doi and GLORYS_DOI not in combined:
        raise GlorysAttributionError(f"missing Copernicus DOI: {GLORYS_DOI!r}")


def append_pull_log(
    record: dict[str, Any],
    *,
    log_path: Path | None = None,
) -> Path:
    """Append one immutable Copernicus request record (never rotates or truncates)."""
    path = log_path or DEFAULT_PULL_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return path


def build_pull_record(
    *,
    dataset_id: str,
    date_start: str,
    date_end: str,
    variables: tuple[str, ...] | list[str],
    bbox: tuple[float, float, float, float],
    request_count: int = 1,
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    ts = timestamp or datetime.now(timezone.utc)
    la0, la1, lo0, lo1 = bbox
    return {
        "dataset_id": dataset_id,
        "date_start": date_start,
        "date_end": date_end,
        "variables": list(variables),
        "bbox": {"lat_min": la0, "lat_max": la1, "lon_min": lo0, "lon_max": lo1},
        "timestamp": ts.isoformat(),
        "request_count": int(request_count),
    }
