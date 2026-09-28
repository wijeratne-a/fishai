"""Catch row semantics (weights, counts, presence-only)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping


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
    f = _parse_float(value)
    if f is None:
        return None
    if f < 0 or f != int(f):
        return None
    return int(f)


def is_presence_only(raw: Any) -> bool:
    text = str(raw or "").strip().upper()
    return text == "Y"


@dataclass(frozen=True)
class CatchValues:
    species: str
    itis_tsn: int | None
    count: int | None
    weight_kg: float | None
    presence_only: bool
    weight_null_reason: str | None


def parse_catch_row(row: Mapping[str, Any]) -> CatchValues | None:
    """
    Parse one ERDDAP species row.

    Returns None when ``scientific_name`` is missing. Never coerces missing weights to zero.
    """
    species = str(row.get("scientific_name", "")).strip()
    if not species:
        return None
    tsn = _parse_int(row.get("itis_tsn"))
    presence = is_presence_only(row.get("presence_only"))
    count = _parse_int(row.get("subsample_count"))
    sub_w = _parse_float(row.get("subsample_weight"))
    rem_w = _parse_float(row.get("remaining_weight"))

    if presence:
        return CatchValues(
            species=species,
            itis_tsn=tsn,
            count=count,
            weight_kg=None,
            presence_only=True,
            weight_null_reason="presence_only",
        )

    parts = [w for w in (sub_w, rem_w) if w is not None]
    if not parts:
        weight: float | None = None
        weight_reason = "weights_missing"
    else:
        weight = float(sum(parts))
        weight_reason = None

    return CatchValues(
        species=species,
        itis_tsn=tsn,
        count=count,
        weight_kg=weight,
        presence_only=False,
        weight_null_reason=weight_reason,
    )


def merge_catch_values(rows: list[CatchValues]) -> CatchValues:
    """Merge multiple ERDDAP rows for the same haul and species (e.g. collection splits)."""
    if not rows:
        raise ValueError("merge_catch_values requires at least one row")
    species = rows[0].species
    tsn = next((r.itis_tsn for r in rows if r.itis_tsn is not None), rows[0].itis_tsn)
    weighted = [r for r in rows if not r.presence_only]
    presence = [r for r in rows if r.presence_only]
    if weighted:
        counts = [r.count for r in weighted if r.count is not None]
        count = sum(counts) if counts else None
        weights = [r.weight_kg for r in weighted if r.weight_kg is not None]
        weight = float(sum(weights)) if weights else None
        reason = None if weight is not None else "weights_missing"
        return CatchValues(
            species=species,
            itis_tsn=tsn,
            count=count,
            weight_kg=weight,
            presence_only=False,
            weight_null_reason=reason,
        )
    # presence-only rows only
    counts = [r.count for r in presence if r.count is not None]
    return CatchValues(
        species=species,
        itis_tsn=tsn,
        count=counts[0] if counts else None,
        weight_kg=None,
        presence_only=True,
        weight_null_reason="presence_only",
    )


def catch_row_invalid(row: Mapping[str, Any]) -> bool:
    """True when presence_only=N but weights are non-numeric garbage."""
    species = str(row.get("scientific_name", "")).strip()
    if not species:
        return True
    if is_presence_only(row.get("presence_only")):
        return False
    for key in ("subsample_weight", "remaining_weight"):
        raw = row.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if not text or text.lower() == "nan":
            continue
        try:
            val = float(text)
        except ValueError:
            return True
        if math.isnan(val):
            continue
    count_raw = row.get("subsample_count")
    if count_raw is not None:
        text = str(count_raw).strip()
        if text and text.lower() not in {"nan", "na"}:
            if _parse_int(count_raw) is None:
                return True
    return False
