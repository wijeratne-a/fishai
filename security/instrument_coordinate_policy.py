"""Instrument coordinate exemption policy (``record_type: instrument`` in SOURCES.yaml)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "SOURCES.yaml"
ALLOWLIST_PATH = REPO_ROOT / "config" / "instrument_coordinate_allowlist.yaml"

# Longest-prefix wins when resolving tracked paths to manifest source_id.
INSTRUMENT_PATH_PREFIXES: tuple[tuple[str, str], ...] = (
    ("tests/fixtures/instrument_data/sccoos_hfr/", "sccoos_hfr"),
    ("tests/fixtures/instrument_data/ndbc_met/", "ndbc_met"),
    ("tests/fixtures/instrument_data/ioos_glider_dac/", "ioos_glider_dac"),
    ("data/processed/sensors/hfradar/", "sccoos_hfr"),
    ("data/processed/sensors/ndbc/", "ndbc_met"),
    ("data/processed/sensors/gliders/", "ioos_glider_dac"),
)

COORDINATE_HIT_PREFIXES = (
    "csv_header:latitude_or_longitude",
    "json_schema:latitude_or_longitude",
    "geojson:coordinate_geometry",
    "parquet_schema:latitude_or_longitude",
)

SCAN_FAILURE_PREFIXES = (
    "parquet_scan:",
    "json_parse:",
)


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or MANIFEST_PATH
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_allowlist_config(path: Path | None = None) -> dict[str, Any]:
    allowlist_path = path or ALLOWLIST_PATH
    data = yaml.safe_load(allowlist_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def instrument_source_ids(manifest: dict[str, Any] | None = None) -> frozenset[str]:
    """Instrument sources that are approved and enabled in SOURCES.yaml."""
    manifest = manifest or load_manifest()
    sources = manifest.get("sources") or {}
    ids: set[str] = set()
    for source_id, entry in sources.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("record_type") != "instrument":
            continue
        if entry.get("status") != "approved":
            continue
        if entry.get("enabled") is not True:
            continue
        ids.add(str(source_id))
    return frozenset(ids)


def folder_source_id(rel: str) -> str | None:
    """Map a repo-relative path to a source_id only when under a declared instrument folder."""
    normalized = rel.replace("\\", "/")
    best: tuple[int, str] | None = None
    for prefix, source_id in INSTRUMENT_PATH_PREFIXES:
        if normalized.startswith(prefix):
            if best is None or len(prefix) > best[0]:
                best = (len(prefix), source_id)
    return best[1] if best else None


def parquet_fishai_source_id(path: Path) -> str | None:
    try:
        import pyarrow.parquet as pq

        meta = pq.read_metadata(path).metadata
        if not meta:
            return None
        raw = meta.get(b"fishai_source_id") or meta.get("fishai_source_id")
        if raw is None:
            return None
        return raw.decode() if isinstance(raw, bytes) else str(raw)
    except OSError:
        return None


def resolve_source_id(rel: str, path: Path | None = None) -> str | None:
    """
    Resolve instrument source for exemption: path prefix is required.

    When the file is Parquet, ``fishai_source_id`` metadata must match the folder source
    (tag alone never grants exemption).
    """
    folder = folder_source_id(rel)
    if folder is None:
        return None
    if path is not None and path.suffix.lower() == ".parquet":
        tag = parquet_fishai_source_id(path)
        if tag is not None and tag != folder:
            return None
    return folder


def _normalize_column(name: str) -> str:
    return name.replace(" ", "_").lower()


def allowed_columns_for_source(
    source_id: str,
    allowlist: dict[str, Any] | None = None,
) -> frozenset[str]:
    cfg = allowlist or load_allowlist_config()
    common = [_normalize_column(c) for c in cfg.get("common_columns") or []]
    src = (cfg.get("sources") or {}).get(source_id) or {}
    measurements = [_normalize_column(c) for c in src.get("measurements") or []]
    return frozenset(common + measurements)


def disallowed_columns(
    source_id: str,
    field_names: list[str],
    allowlist: dict[str, Any] | None = None,
) -> list[str]:
    allowed = allowed_columns_for_source(source_id, allowlist=allowlist)
    return [name for name in field_names if _normalize_column(name) not in allowed]


def apply_instrument_coordinate_exemption(
    rel: str,
    hits: list[str],
    field_names: list[str],
    *,
    path: Path | None = None,
    manifest: dict[str, Any] | None = None,
    allowlist: dict[str, Any] | None = None,
) -> list[str]:
    """Drop coordinate hits for declared instrument paths with allowlisted columns only."""
    manifest = manifest or load_manifest()
    allowlist = allowlist or load_allowlist_config()
    allowed_sources = instrument_source_ids(manifest)
    source_id = resolve_source_id(rel, path=path)
    if not source_id or source_id not in allowed_sources:
        return hits
    extra_cols = disallowed_columns(source_id, field_names, allowlist=allowlist)
    if extra_cols:
        extra = [f"instrument:disallowed_column:{source_id}:{c}" for c in extra_cols]
        return hits + extra
    failures = {h for h in hits if any(h.startswith(p) for p in SCAN_FAILURE_PREFIXES)}
    coord_kinds = {
        h
        for h in hits
        if any(h == p or h.startswith(p) for p in COORDINATE_HIT_PREFIXES)
    }
    if not coord_kinds:
        return hits
    return [h for h in hits if h not in coord_kinds or h in failures]
