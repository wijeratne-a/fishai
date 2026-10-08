"""Catch-row parsing for CPS nearshore set catch.

Unlike the mid-water trawl source, ``totalNumber`` / ``totalWeightkg`` here are
set-level totals for the species (not subsample components), so no raising or
partial-weight logic applies. A row with neither a count nor a weight is
invalid — presence-only rows are never emitted as catch evidence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CatchValues:
    scientific_name: str
    itis_tsn: int | None
    total_number: int | None
    total_weight_kg: float | None


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


def _parse_int(value: Any) -> int | None:
    out = _parse_float(value)
    if out is None:
        return None
    return int(out)


def _parse_tsn(value: Any) -> int | None:
    return _parse_int(value)


def catch_row_unparseable(row: Mapping[str, Any]) -> bool:
    """True when the row lacks a usable species identity."""
    name = str(row.get("scientific_name") or "").strip()
    return not name


def parse_catch_row(row: Mapping[str, Any]) -> CatchValues | None:
    """Parse one ERDDAP catch row; None when unparseable (no species name)."""
    name = str(row.get("scientific_name") or "").strip()
    if not name:
        return None
    return CatchValues(
        scientific_name=name,
        itis_tsn=_parse_tsn(row.get("itis_tsn")),
        total_number=_parse_int(row.get("totalNumber")),
        total_weight_kg=_parse_float(row.get("totalWeightkg")),
    )


def catch_row_invalid(row: Mapping[str, Any]) -> bool:
    """True when the row has no usable catch measurement at all."""
    parsed = parse_catch_row(row)
    if parsed is None:
        return True
    return parsed.total_number is None and parsed.total_weight_kg is None


def catch_values_to_record(set_id: str, values: CatchValues) -> dict[str, Any]:
    return {
        "set_id": set_id,
        "scientific_name": values.scientific_name,
        "itis_tsn": values.itis_tsn,
        "total_number": values.total_number,
        "total_weight_kg": values.total_weight_kg,
    }
