"""Load and enforce ``data/SOURCES.yaml`` for ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "data" / "SOURCES.yaml"

REQUIRED_SOURCE_FIELDS = (
    "module",
    "license",
    "license_url",
    "attribution",
    "status",
    "enabled",
)

ALLOWED_STATUS = frozenset({"approved", "pending", "account_required", "disabled"})


class SourceNotApprovedError(RuntimeError):
    """Raised when ingestion is attempted for a blocked source."""


def load_sources_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or MANIFEST_PATH
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("SOURCES.yaml must be a mapping")
    return data


def get_source_entry(source_id: str, *, path: Path | None = None) -> dict[str, Any]:
    data = load_sources_manifest(path)
    sources = data.get("sources") or {}
    entry = sources.get(source_id)
    if not isinstance(entry, dict):
        raise KeyError(f"unknown source_id: {source_id}")
    return entry


def require_approved(source_id: str, *, path: Path | None = None) -> dict[str, Any]:
    """Return the source entry when ``status`` is approved and ``enabled`` is true."""
    entry = get_source_entry(source_id, path=path)
    status = entry.get("status")
    enabled = entry.get("enabled")
    if status not in ALLOWED_STATUS:
        raise SourceNotApprovedError(f"{source_id}: invalid status {status!r}")
    if status != "approved" or enabled is not True:
        raise SourceNotApprovedError(
            f"{source_id}: ingestion blocked (status={status!r}, enabled={enabled!r})"
        )
    missing = [field for field in REQUIRED_SOURCE_FIELDS if field not in entry]
    if missing:
        raise SourceNotApprovedError(f"{source_id}: missing manifest fields: {missing}")
    return entry


def attribution_for(source_id: str, *, path: Path | None = None) -> str:
    """Return required attribution text for an approved source."""
    entry = require_approved(source_id, path=path)
    text = entry.get("attribution")
    if not text or not str(text).strip():
        raise SourceNotApprovedError(f"{source_id}: attribution must be non-empty")
    return str(text).strip()
