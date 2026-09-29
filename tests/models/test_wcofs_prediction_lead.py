"""WCOFS forecast_age_hours → prediction lead_days (PR #5 contract)."""

from __future__ import annotations

import pytest

from fishai.models.wcofs_prediction_lead import (
    InvalidLeadDaysInputError,
    prediction_output_from_forecast_age,
)


@pytest.mark.parametrize(
    ("age", "fallback", "lead_days"),
    [
        (-3.0, False, 0),
        (0.0, False, 0),
        (24.0, True, 1),
    ],
)
def test_prediction_lead_from_forecast_age(age: float, fallback: bool, lead_days: int) -> None:
    out = prediction_output_from_forecast_age(age, fallback_used=fallback)
    if fallback or age > 0:
        assert out["evidence_state"] == "FORECAST"
    else:
        assert out["evidence_state"] == "NOWCAST"
    assert out["lead_days"] == lead_days


def test_nowcast_missing_lead_days_input_still_outputs_zero() -> None:
    out = prediction_output_from_forecast_age(
        -3.0,
        fallback_used=False,
        lead_days_input=float("nan"),
    )
    assert out["lead_days"] == 0
    assert out["evidence_state"] == "NOWCAST"


def test_negative_lead_days_input_raises() -> None:
    with pytest.raises(InvalidLeadDaysInputError, match="-1"):
        prediction_output_from_forecast_age(
            0.0,
            fallback_used=False,
            lead_days_input=-1,
        )


def test_no_data_yields_unknown() -> None:
    out = prediction_output_from_forecast_age(
        float("nan"),
        fallback_used=False,
        unknown_reason=None,
    )
    assert out["evidence_state"] == "UNKNOWN"
    assert out["lead_days"] == 0
    assert out["unknown_reason"] == "missing_operational_cycle"


def test_explicit_unknown_reason() -> None:
    out = prediction_output_from_forecast_age(
        0.0,
        fallback_used=False,
        unknown_reason="missing_operational_cycle",
    )
    assert out["evidence_state"] == "UNKNOWN"
    assert out["lead_days"] == 0
