"""Catch row semantics (weights, counts, presence-only)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

from fishai.ingestion.biology.cps_trawl.constants import WEIGHT_FLAG_PARTIAL


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


def resolve_weights(
    subsample_weight_kg: float | None,
    remaining_weight_kg: float | None,
) -> tuple[float | None, str | None, float | None, float | None]:
    """
    Return (weight_kg, weight_flag, subsample_weight_kg, remaining_weight_kg).

    A single present weight without the other is partial (never summed to total).
    """
    has_sub = subsample_weight_kg is not None
    has_rem = remaining_weight_kg is not None
    if has_sub and has_rem:
        return (
            float(subsample_weight_kg + remaining_weight_kg),
            None,
            subsample_weight_kg,
            remaining_weight_kg,
        )
    if has_sub or has_rem:
        return None, WEIGHT_FLAG_PARTIAL, subsample_weight_kg, remaining_weight_kg
    return None, None, None, None


def estimate_count_raised(
    subsample_count: int | None,
    subsample_weight_kg: float | None,
    remaining_weight_kg: float | None,
) -> tuple[int | None, str | None]:
    """Raise subsample count to estimated haul total when both weights are valid."""
    if subsample_count is None:
        return None, "subsample_count_missing"
    if subsample_weight_kg is None or remaining_weight_kg is None:
        return None, "raising_weights_incomplete"
    if subsample_weight_kg <= 0:
        return None, "subsample_weight_not_positive"
    total_w = subsample_weight_kg + remaining_weight_kg
    raised = subsample_count * total_w / subsample_weight_kg
    return int(round(raised)), None


@dataclass(frozen=True)
class CatchValues:
    species: str
    itis_tsn: int | None
    subsample_count: int | None
    count_raised_est: int | None
    count_raised_est_null_reason: str | None
    weight_kg: float | None
    subsample_weight_kg: float | None
    remaining_weight_kg: float | None
    weight_flag: str | None
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
    subsample_count = _parse_int(row.get("subsample_count"))
    sub_w = _parse_float(row.get("subsample_weight"))
    rem_w = _parse_float(row.get("remaining_weight"))

    if presence:
        return CatchValues(
            species=species,
            itis_tsn=tsn,
            subsample_count=subsample_count,
            count_raised_est=None,
            count_raised_est_null_reason="presence_only",
            weight_kg=None,
            subsample_weight_kg=None,
            remaining_weight_kg=None,
            weight_flag=None,
            presence_only=True,
            weight_null_reason="presence_only",
        )

    weight_kg, weight_flag, sub_out, rem_out = resolve_weights(sub_w, rem_w)
    raised, raised_reason = estimate_count_raised(subsample_count, sub_w, rem_w)
    weight_reason = None
    if weight_kg is None and weight_flag is None:
        weight_reason = "weights_missing"

    return CatchValues(
        species=species,
        itis_tsn=tsn,
        subsample_count=subsample_count,
        count_raised_est=raised,
        count_raised_est_null_reason=raised_reason,
        weight_kg=weight_kg,
        subsample_weight_kg=sub_out,
        remaining_weight_kg=rem_out,
        weight_flag=weight_flag,
        presence_only=False,
        weight_null_reason=weight_reason if weight_flag != WEIGHT_FLAG_PARTIAL else "weight_partial",
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
        counts = [r.subsample_count for r in weighted if r.subsample_count is not None]
        subsample_count = sum(counts) if counts else None
        if len(weighted) == 1:
            single = weighted[0]
            if subsample_count != single.subsample_count:
                raised, raised_reason = estimate_count_raised(
                    subsample_count,
                    single.subsample_weight_kg,
                    single.remaining_weight_kg,
                )
                return CatchValues(
                    species=species,
                    itis_tsn=tsn,
                    subsample_count=subsample_count,
                    count_raised_est=raised,
                    count_raised_est_null_reason=raised_reason,
                    weight_kg=single.weight_kg,
                    subsample_weight_kg=single.subsample_weight_kg,
                    remaining_weight_kg=single.remaining_weight_kg,
                    weight_flag=single.weight_flag,
                    presence_only=False,
                    weight_null_reason=single.weight_null_reason,
                )
            return single
        any_partial = any(r.weight_flag == WEIGHT_FLAG_PARTIAL for r in weighted)
        if any_partial:
            sub_out = next((r.subsample_weight_kg for r in weighted if r.subsample_weight_kg is not None), None)
            rem_out = next((r.remaining_weight_kg for r in weighted if r.remaining_weight_kg is not None), None)
            return CatchValues(
                species=species,
                itis_tsn=tsn,
                subsample_count=subsample_count,
                count_raised_est=None,
                count_raised_est_null_reason="raising_weights_incomplete",
                weight_kg=None,
                subsample_weight_kg=sub_out,
                remaining_weight_kg=rem_out,
                weight_flag=WEIGHT_FLAG_PARTIAL,
                presence_only=False,
                weight_null_reason="weight_partial",
            )
        sub_w = sum(r.subsample_weight_kg for r in weighted if r.subsample_weight_kg is not None)
        rem_w = sum(r.remaining_weight_kg for r in weighted if r.remaining_weight_kg is not None)
        weight_kg, weight_flag, sub_out, rem_out = resolve_weights(sub_w, rem_w)
        raised, raised_reason = estimate_count_raised(subsample_count, sub_out, rem_out)
        weight_reason = None if weight_kg is not None else "weights_missing"
        return CatchValues(
            species=species,
            itis_tsn=tsn,
            subsample_count=subsample_count,
            count_raised_est=raised,
            count_raised_est_null_reason=raised_reason,
            weight_kg=weight_kg,
            subsample_weight_kg=sub_out,
            remaining_weight_kg=rem_out,
            weight_flag=weight_flag,
            presence_only=False,
            weight_null_reason=weight_reason,
        )
    counts = [r.subsample_count for r in presence if r.subsample_count is not None]
    return CatchValues(
        species=species,
        itis_tsn=tsn,
        subsample_count=counts[0] if counts else None,
        count_raised_est=None,
        count_raised_est_null_reason="presence_only",
        weight_kg=None,
        subsample_weight_kg=None,
        remaining_weight_kg=None,
        weight_flag=None,
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


def catch_values_to_record(haul_id: str, merged: CatchValues) -> dict[str, Any]:
    return {
        "haul_id": haul_id,
        "species": merged.species,
        "itis_tsn": merged.itis_tsn,
        "subsample_count": merged.subsample_count,
        "count_raised_est": merged.count_raised_est,
        "count_raised_est_null_reason": merged.count_raised_est_null_reason,
        "weight_kg": merged.weight_kg,
        "subsample_weight_kg": merged.subsample_weight_kg,
        "remaining_weight_kg": merged.remaining_weight_kg,
        "weight_flag": merged.weight_flag,
        "presence_only": merged.presence_only,
        "weight_null_reason": merged.weight_null_reason,
    }
