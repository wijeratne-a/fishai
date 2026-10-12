"""Normalize CPS specimen tables for adult length filtering."""

from __future__ import annotations

import math
from typing import Any, Mapping

import pandas as pd

from fishai.ingestion.biology.cps_nearshore.transform import make_set_id
from fishai.ingestion.biology.cps_trawl.transform import make_haul_id


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "na", ""}:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if math.isnan(out):
        return None
    return out


def _length_mm_from_row(row: Mapping[str, Any]) -> float | None:
    """Prefer standard length; if absent, use fork length (no FL→SL conversion)."""
    for key in (
        "standard_length",
        "standardLength_mm",
        "length_mm",
        "length",
    ):
        val = _parse_float(row.get(key))
        if val is not None and val > 0:
            return val
    for key in ("fork_length", "forkLength_mm"):
        val = _parse_float(row.get(key))
        if val is not None and val > 0:
            return val
    return None


def normalize_trawl_specimens(records: list[Mapping[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in records:
        cruise = str(row.get("cruise") or "").strip()
        ship = str(row.get("ship") or "").strip()
        haul = str(row.get("haul") or "").strip()
        species = str(
            row.get("scientific_name") or row.get("scientificName") or row.get("species") or ""
        ).strip()
        length_mm = _length_mm_from_row(row)
        if not cruise or not ship or not haul or not species or length_mm is None:
            continue
        rows.append(
            {
                "event_id": make_haul_id(cruise, ship, haul),
                "species": species,
                "length_mm": float(length_mm),
            }
        )
    return pd.DataFrame(rows)


def normalize_nearshore_specimens(records: list[Mapping[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in records:
        cruise = str(row.get("cruise") or "").strip()
        ship = str(row.get("ship") or "").strip()
        set_no = str(row.get("set") or row.get("set_number") or "").strip()
        species = str(
            row.get("scientific_name") or row.get("scientificName") or row.get("species") or ""
        ).strip()
        length_mm = _length_mm_from_row(row)
        if not cruise or not ship or not set_no or not species or length_mm is None:
            continue
        rows.append(
            {
                "event_id": make_set_id(cruise, ship, set_no),
                "species": species,
                "length_mm": float(length_mm),
            }
        )
    return pd.DataFrame(rows)


def median_length_by_event_species(specimens: pd.DataFrame) -> pd.Series:
    """Index: (event_id, species) → median length mm."""
    if specimens.empty:
        return pd.Series(dtype=float)
    grouped = specimens.groupby(["event_id", "species"], sort=True)["length_mm"].median()
    return grouped
