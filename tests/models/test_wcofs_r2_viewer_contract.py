"""R-2 two-missed-runs viewer contract: lead_days from forecast_age_hours only."""

from __future__ import annotations

import datetime as dt
import math

import pytest

from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.models.wcofs_pr11_a469ebf_contract import build_pr11_scenario, pr5_prediction_from_pr11_zarr_step


def test_r2_offsets_through_24_match_age_offset_plus_48() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("r2_fallback_offsets_beyond_24_unknown", target)
    r2 = target - dt.timedelta(days=2)
    source_run = wcofs_src.cycle_run_time(r2).isoformat()
    for off in range(-21, 25, 3):
        lp = next((s for s in scenario["zarr_steps"] if s["valid_offset_h"] == off), None)
        assert lp is not None, off
        assert lp["fallback_used"] is True
        assert float(lp["forecast_age_hours"]) == off + 48
        assert lp["source_run_time"] == source_run
        pred = pr5_prediction_from_pr11_zarr_step(lp)
        assert pred["evidence_state"] == "FORECAST"
        expected_lead = int(min(3, max(1, math.ceil((off + 48) / 24))))
        assert pred["lead_days"] == expected_lead
        offset_based = int(min(3, max(0, math.ceil(off / 24)))) if off > 0 else 0
        if off <= 0:
            assert pred["lead_days"] != offset_based or off == 0


def test_r2_unknown_offsets_27_and_72() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("r2_fallback_offsets_beyond_24_unknown", target)
    reasons = {int(u["valid_offset_h"]): u["reason"] for u in scenario["pull_log_unknown"]}
    assert reasons[27] == "missing_operational_cycle"
    assert reasons[72] == "missing_operational_cycle"
