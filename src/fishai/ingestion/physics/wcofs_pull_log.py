"""Append-only WCOFS pull provenance (daily job + PDS overlap helpers)."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from fishai.ingestion.sources import REPO_ROOT

DAY_TOMBSTONE_RECORD_TYPE = "day_tombstone"
DAY_SUCCESS_RECORD_TYPE = "day_success"

DEFAULT_PULL_LOG_DIR = REPO_ROOT / "data" / "provenance"
DEFAULT_WCOFS_PULL_LOG = DEFAULT_PULL_LOG_DIR / "wcofs_pull_log.jsonl"


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


def utc_today() -> date:
    """Current calendar date in UTC (operational WCOFS target day)."""
    return datetime.now(timezone.utc).date()


def build_day_tombstone_record(
    target: date,
    *,
    reason: str,
    run_time_utc: datetime | None = None,
    attempted_s3_keys: Sequence[str] | None = None,
    attempted_cycles: Sequence[str] | None = None,
    unknown_slots: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    ts = run_time_utc or datetime.now(timezone.utc)
    cycle = f"{target.strftime('%Y%m%d')}T03Z"
    rec: dict[str, Any] = {
        "record_type": DAY_TOMBSTONE_RECORD_TYPE,
        "target_date": target.isoformat(),
        "target_cycle": cycle,
        "cycle": cycle,
        "status": "failed",
        "reason": reason,
        "fetch_time_utc": ts.isoformat(),
    }
    if attempted_s3_keys is not None:
        rec["attempted_s3_keys"] = list(attempted_s3_keys)
    if attempted_cycles is not None:
        rec["attempted_cycles"] = list(attempted_cycles)
    if unknown_slots is not None:
        rec["unknown_slots"] = list(unknown_slots)
    return rec


def build_day_success_record(
    target: date,
    *,
    run_time_utc: datetime | None = None,
) -> dict[str, Any]:
    ts = run_time_utc or datetime.now(timezone.utc)
    cycle = f"{target.strftime('%Y%m%d')}T03Z"
    return {
        "record_type": DAY_SUCCESS_RECORD_TYPE,
        "target_date": target.isoformat(),
        "target_cycle": cycle,
        "cycle": cycle,
        "status": "ok",
        "fetch_time_utc": ts.isoformat(),
    }


def load_day_outcome(log_path: Path) -> tuple[str | None, dict[str, Any] | None]:
    """
    Return the latest day-level outcome in ``log_path`` (append order wins).

    ``failed`` means the most recent day-level record is a tombstone; ``success``
    means the most recent record is a successful daily completion.
    """
    if not log_path.is_file():
        return None, None
    status: str | None = None
    record: dict[str, Any] | None = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        record_type = rec.get("record_type")
        if record_type == DAY_TOMBSTONE_RECORD_TYPE:
            status = "failed"
            record = rec
        elif record_type == DAY_SUCCESS_RECORD_TYPE:
            status = "success"
            record = rec
    return status, record


def load_day_tombstone(log_path: Path) -> dict[str, Any] | None:
    """Return the latest day-level tombstone in ``log_path``, if any."""
    if not log_path.is_file():
        return None
    tombstone: dict[str, Any] | None = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("record_type") == DAY_TOMBSTONE_RECORD_TYPE:
            tombstone = rec
    return tombstone


def pull_log_path_for_date(
    target: date,
    *,
    out_root: Path | None = None,
    provenance_dir: Path | None = None,
) -> Path:
    log_dir = resolve_pull_log_dir(out_root, provenance_dir)
    return pull_log_path(target.strftime("%Y%m%d"), log_dir=log_dir)


def day_outcome_for_date(
    target: date,
    *,
    out_root: Path | None = None,
    provenance_dir: Path | None = None,
) -> tuple[str | None, dict[str, Any] | None]:
    return load_day_outcome(pull_log_path_for_date(target, out_root=out_root, provenance_dir=provenance_dir))


def day_tombstone_for_date(
    target: date,
    *,
    out_root: Path | None = None,
    provenance_dir: Path | None = None,
) -> dict[str, Any] | None:
    return load_day_tombstone(
        pull_log_path_for_date(target, out_root=out_root, provenance_dir=provenance_dir)
    )


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
