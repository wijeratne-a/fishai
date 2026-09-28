"""Instrument coordinate exemption policy (``record_type: instrument`` in SOURCES.yaml)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "SOURCES.yaml"

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

FISHERY_FIELD_EXACT = frozenset({"species", "count"})
FISHERY_FIELD_PREFIX = ("catch",)


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or MANIFEST_PATH
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def instrument_source_ids(manifest: dict[str, Any] | None = None) -> frozenset[str]:
    manifest = manifest or load_manifest()
    sources = manifest.get("sources") or {}
    ids: set[str] = set()
    for source_id, entry in sources.items():
        if isinstance(entry, dict) and entry.get("record_type") == "instrument":
            ids.add(str(source_id))
    return frozenset(ids)


def resolve_source_id(rel: str, path: Path | None = None) -> str | None:
    normalized = rel.replace("\\", "/")
    best: tuple[int, str] | None = None
    for prefix, source_id in INSTRUMENT_PATH_PREFIXES:
        if normalized.startswith(prefix):
            if best is None or len(prefix) > best[0]:
                best = (len(prefix), source_id)
    if best:
        return best[1]
    if path is not None and path.suffix.lower() == ".parquet":
        try:
            import pyarrow.parquet as pq

            meta = pq.read_metadata(path).metadata
            if meta:
                raw = meta.get(b"fishai_source_id") or meta.get("fishai_source_id")
                if raw is not None:
                    return raw.decode() if isinstance(raw, bytes) else str(raw)
        except OSError:
            pass
    return None


def field_is_fishery_dependent(name: str) -> bool:
    normalized = name.replace(" ", "_").lower()
    if normalized in FISHERY_FIELD_EXACT:
        return True
    return any(normalized.startswith(prefix) for prefix in FISHERY_FIELD_PREFIX)


def fishery_fields_in_names(names: list[str]) -> list[str]:
    return [n for n in names if field_is_fishery_dependent(n)]


def apply_instrument_coordinate_exemption(
    rel: str,
    hits: list[str],
    field_names: list[str],
    *,
    path: Path | None = None,
    manifest: dict[str, Any] | None = None,
) -> list[str]:
    """Drop coordinate hits for declared instrument sources unless fishery fields present."""
    manifest = manifest or load_manifest()
    allowed = instrument_source_ids(manifest)
    source_id = resolve_source_id(rel, path=path)
    if not source_id or source_id not in allowed:
        return hits
    fishery = fishery_fields_in_names(field_names)
    if fishery:
        extra = [f"instrument:fishery_field_with_coordinates:{source_id}:{f}" for f in fishery]
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
