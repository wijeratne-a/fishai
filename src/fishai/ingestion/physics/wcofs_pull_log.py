"""Append-only WCOFS PDS pull provenance (no credentials)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fishai.ingestion.sources import REPO_ROOT

DEFAULT_WCOFS_PULL_LOG = REPO_ROOT / "data" / "provenance" / "wcofs_pull_log.jsonl"


def append_wcofs_pull_log(record: dict[str, Any], *, log_path: Path | None = None) -> Path:
    path = log_path or DEFAULT_WCOFS_PULL_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return path


def build_wcofs_pull_record(
    *,
    cycle_date: str,
    s3_key: str,
    attribution: str,
    request_count: int = 1,
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    ts = timestamp or datetime.now(timezone.utc)
    return {
        "source": "wcofs",
        "cycle_date": cycle_date,
        "s3_key": s3_key,
        "attribution": attribution,
        "timestamp": ts.isoformat(),
        "request_count": int(request_count),
    }
