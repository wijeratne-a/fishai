"""Map WCOFS ``forecast_age_hours`` to PR #5 prediction ``lead_days`` / evidence tier."""

from __future__ import annotations

import math
from typing import Any

from fishai.ingestion.physics.wcofs_daily import evidence_from_forecast_age


class InvalidLeadDaysInputError(ValueError):
    """Raised when Zarr/input ``lead_days`` violates the operational contract."""


def _coerce_optional_lead_days(lead_days_input: Any) -> int | None:
    if lead_days_input is None:
        return None
    if isinstance(lead_days_input, float) and math.isnan(lead_days_input):
        return None
    try:
        value = int(lead_days_input)
    except (TypeError, ValueError) as exc:
        raise InvalidLeadDaysInputError(f"invalid lead_days input {lead_days_input!r}") from exc
    if value < 0:
        raise InvalidLeadDaysInputError(
            f"invalid lead_days input {lead_days_input!r}; must be >= 0 (never -1 in outputs)"
        )
    return value


def prediction_output_from_forecast_age(
    forecast_age_hours: float | None,
    *,
    fallback_used: bool,
    lead_days_input: Any = None,
    unknown_reason: str | None = None,
) -> dict[str, Any]:
    """Resolve prediction-row evidence tier and ``lead_days`` (0–3, never NaN).

    Uses only ``forecast_age_hours`` for lead logic (not ``lead_hours``).
    Nowcast when ``forecast_age_hours <= 0`` and ``fallback_used`` is false;
    otherwise forecast with ``lead_days = ceil(forecast_age_hours / 24)`` (fallback
    forces at least 1 day when age <= 0).
    """
    if unknown_reason:
        return {
            "evidence_tier": "unknown",
            "evidence_state": "UNKNOWN",
            "lead_days": 0,
            "unknown_reason": unknown_reason,
        }
    if forecast_age_hours is None or (
        isinstance(forecast_age_hours, float) and math.isnan(forecast_age_hours)
    ):
        return {
            "evidence_tier": "unknown",
            "evidence_state": "UNKNOWN",
            "lead_days": 0,
            "unknown_reason": "missing_operational_cycle",
        }

    _coerce_optional_lead_days(lead_days_input)

    age = float(forecast_age_hours)
    hint, lead_days = evidence_from_forecast_age(age, fallback_used=fallback_used)
    if hint == "nowcast":
        return {
            "evidence_tier": "nowcast",
            "evidence_state": "NOWCAST",
            "lead_days": 0,
            "unknown_reason": None,
        }
    assert lead_days is not None
    out_days = int(max(0, min(3, lead_days)))
    return {
        "evidence_tier": "forecast",
        "evidence_state": "FORECAST",
        "lead_days": out_days,
        "unknown_reason": None,
    }
