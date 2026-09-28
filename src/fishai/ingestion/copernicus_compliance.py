"""Copernicus Marine licence compliance helpers (no credential access)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

GLORYS_CREDIT_TEXT = "Generated using E.U. Copernicus Marine Service Information"
GLORYS_DOI = "10.48670/moi-00021"

DEFAULT_PULL_LOG = REPO_ROOT / "data" / "provenance" / "copernicus_pull_log.jsonl"


class GlorysAttributionError(RuntimeError):
    """Raised when GLORYS-derived export metadata lacks required credit/DOI."""


def glorys_attribution_bundle(entry: dict[str, Any]) -> dict[str, str]:
    """Return the single manifest ``attribution`` string for GLORYS exports."""
    text = str(entry.get("attribution") or "").strip()
    return {"attribution": text}


def require_glorys_attribution(metadata: dict[str, Any]) -> None:
    """
    Fail closed before rendering/exporting GLORYS-derived products.

    Validates the single ``attribution`` field contains both the mandated credit
    sentence and DOI (no separate duplicate fields required at export time).
    """
    if not metadata.get("glorys_derived"):
        return
    text = str(metadata.get("attribution") or "").strip()
    if GLORYS_CREDIT_TEXT not in text:
        raise GlorysAttributionError(f"missing Copernicus credit in attribution: {GLORYS_CREDIT_TEXT!r}")
    if GLORYS_DOI not in text:
        raise GlorysAttributionError(f"missing Copernicus DOI in attribution: {GLORYS_DOI!r}")


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
