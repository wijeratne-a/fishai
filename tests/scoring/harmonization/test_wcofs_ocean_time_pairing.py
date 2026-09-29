"""WCOFS valid time from ``ocean_time`` (auditbot1 2026-09-26 t03z pattern)."""

from __future__ import annotations

import pandas as pd

from fishai.scoring.harmonization.forecast_age import (
    NOWCAST_GROUP,
    enrich_pairing_forecast_metadata,
    is_nowcast_group,
)
from fishai.scoring.harmonization.wcofs_ocean_time import (
    attach_forecast_age_from_ocean_time,
    forecast_age_hours_from_ocean_time,
    observation_pairs_with_model_at_ocean_time,
)

RUN_TIME = "2026-09-26T03:00:00Z"


def _step_row(lead: str, ocean_time: str, obs_value: float) -> dict:
    return {
        "wcofs_lead": lead,
        "ocean_time": ocean_time,
        "source_run_time": RUN_TIME,
        "fallback_used": False,
        "date": "2026-09-26",
        "variable": "sea_water_temperature",
        "obs_value": obs_value,
        "nearshore": True,
        "obs_id": "b1",
        "wcofs_coarsened_mapped": obs_value + 0.01,
        "glorys": obs_value + 0.02,
        "wcofs_native": obs_value,
        "wcofs_coarsened": obs_value,
    }


def test_auditbot1_lead_ocean_time_pattern() -> None:
    n003 = "2026-09-25T06:00:00Z"
    n024 = RUN_TIME
    f003 = "2026-09-26T06:00:00Z"
    assert forecast_age_hours_from_ocean_time(n003, RUN_TIME) == -21.0
    assert forecast_age_hours_from_ocean_time(n024, RUN_TIME) == 0.0
    assert forecast_age_hours_from_ocean_time(f003, RUN_TIME) == 3.0


def test_observation_pairs_by_ocean_time_not_lead_token() -> None:
    model = pd.DataFrame(
        [
            _step_row("n003", "2026-09-25T06:00:00Z", 10.0),
            _step_row("n024", RUN_TIME, 11.0),
            _step_row("f003", "2026-09-26T06:00:00Z", 12.0),
        ]
    )
    obs_time = RUN_TIME
    idx = observation_pairs_with_model_at_ocean_time(obs_time, model["ocean_time"])
    assert len(idx) == 1
    assert model.loc[idx[0], "wcofs_lead"] == "n024"
    assert model.loc[idx[0], "obs_value"] == 11.0


def test_n024_nowcast_f003_forecast_group() -> None:
    df = attach_forecast_age_from_ocean_time(
        pd.DataFrame(
            [
                _step_row("n024", RUN_TIME, 11.0),
                _step_row("f003", "2026-09-26T06:00:00Z", 12.0),
            ]
        )
    )
    enriched = enrich_pairing_forecast_metadata(df)
    now = enriched[enriched["wcofs_lead"] == "n024"].iloc[0]
    fc = enriched[enriched["wcofs_lead"] == "f003"].iloc[0]
    assert is_nowcast_group(float(now["forecast_age_hours"]), bool(now["fallback_used"]))
    assert now["forecast_group"] == NOWCAST_GROUP
    assert fc["forecast_group"] != NOWCAST_GROUP
