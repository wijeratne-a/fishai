"""Append-only ERDDAP wind pull provenance (no credentials)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fishai.ingestion.sources import REPO_ROOT

DEFAULT_WIND_PULL_LOG = REPO_ROOT / "data" / "provenance" / "wind_pull_log.jsonl"


def append_wind_pull_log(record: dict[str, Any], *, log_path: Path | None = None) -> Path:
    path = log_path or DEFAULT_WIND_PULL_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return path


def build_wind_pull_record(
    *,
    dataset_id: str,
    date_start: str,
    date_end: str,
    variables: tuple[str, ...] | list[str],
    bbox: tuple[float, float, float, float],
    dataset_version: str | None = None,
    request_count: int = 1,
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    ts = timestamp or datetime.now(timezone.utc)
    la0, la1, lo0, lo1 = bbox
    record: dict[str, Any] = {
        "dataset_id": dataset_id,
        "date_start": date_start,
        "date_end": date_end,
        "variables": list(variables),
        "bbox": {"lat_min": la0, "lat_max": la1, "lon_min": lo0, "lon_max": lo1},
        "timestamp": ts.isoformat(),
        "request_count": int(request_count),
    }
    if dataset_version is not None:
        record["dataset_version"] = dataset_version
    return record
