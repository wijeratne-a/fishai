"""Immutable pull log records for WCOFS NetCDF fetches."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fishai.ingestion.sources import REPO_ROOT

DEFAULT_PULL_LOG_DIR = REPO_ROOT / "data" / "provenance"


def resolve_pull_log_dir(
    out_root: Path | None = None,
    provenance_dir: Path | None = None,
) -> Path:
    """
    Pilot layout: ``data/processed/physics`` → ``data/provenance``.

    Any other ``out_root`` (e.g. pytest ``tmp_path``) keeps logs under ``out_root/provenance``.
    """
    if provenance_dir is not None:
        return provenance_dir
    if out_root is not None:
        try:
            rel = out_root.resolve().relative_to(REPO_ROOT.resolve())
            if len(rel.parts) >= 2 and rel.parts[0] == "data" and rel.parts[1] == "processed":
                return DEFAULT_PULL_LOG_DIR
        except ValueError:
            pass
        return out_root / "provenance"
    return DEFAULT_PULL_LOG_DIR


def pull_log_path(cycle_date: str, *, log_dir: Path | None = None) -> Path:
    root = log_dir or DEFAULT_PULL_LOG_DIR
    return root / f"wcofs_pull_{cycle_date}.jsonl"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_pull_record(
    *,
    s3_key: str,
    cycle: str,
    lead: str,
    lead_hour: int,
    status: str,
    fetch_time_utc: datetime | None = None,
    etag: str | None = None,
    size_bytes: int | None = None,
    sha256: str | None = None,
    url: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ts = fetch_time_utc or datetime.now(timezone.utc)
    rec: dict[str, Any] = {
        "s3_key": s3_key,
        "cycle": cycle,
        "lead": lead,
        "lead_hour": int(lead_hour),
        "status": status,
        "fetch_time_utc": ts.isoformat(),
    }
    if url is not None:
        rec["url"] = url
    if etag is not None:
        rec["etag"] = etag
    if size_bytes is not None:
        rec["size_bytes"] = int(size_bytes)
    if sha256 is not None:
        rec["sha256"] = sha256
    if extra:
        rec.update(extra)
    return rec


def append_pull_log(record: dict[str, Any], *, log_path: Path) -> Path:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True) + "\n"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return log_path


def load_pull_index(log_path: Path) -> dict[str, dict[str, Any]]:
    """Map S3 key -> latest successful pull record."""
    if not log_path.is_file():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = rec.get("s3_key")
        if key and rec.get("status") == "ok":
            out[str(key)] = rec
    return out
