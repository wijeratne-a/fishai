"""Covariate join drop-table reasons."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fishai.ingestion.physics.covariates import (
    COL_START_LAT,
    COL_START_LON,
    COL_STOP_LAT,
    COL_STOP_LON,
    DROP_REASON_LAND_MASK,
    DROP_REASON_MISSING_COVARIATE,
    DROP_REASON_MISSING_ENDPOINT,
    DROP_REASON_TOO_FEW_TRACK_POINTS,
    SAMPLER_LAND_MASK_KEY,
    join_covariates_to_events,
)


def _events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": ["CUFES:2020-01:SH01:1", "CUFES:2020-01:SH01:2", "CUFES:2020-01:SH01:3"],
            "start_time": pd.to_datetime(["2020-01-01T12:00:00Z"] * 3, utc=True),
            "stop_time": pd.to_datetime(["2020-01-01T12:10:00Z"] * 3, utc=True),
            "start_latitude": [33.0, 33.5, 34.0],
            "start_longitude": [-120.0, -120.0, -120.0],
            "stop_latitude": [33.02, 33.5, 34.0],
            "stop_longitude": [-119.98, -120.0, -120.0],
        }
    )


def test_drop_missing_endpoint() -> None:
    events = _events()
    events.loc[0, COL_STOP_LAT] = np.nan
    _, qc, drops = join_covariates_to_events(events, field_sampler=lambda *_: {}, source="t")
    assert (drops["reason"] == DROP_REASON_MISSING_ENDPOINT).any()
    assert qc["drop_summary"][DROP_REASON_MISSING_ENDPOINT] >= 1


def test_drop_land_mask() -> None:
    events = _events()

    def sampler(lat: float, lon: float, _t: pd.Timestamp) -> dict:
        return {SAMPLER_LAND_MASK_KEY: True, "T3m": lat}

    _, qc, drops = join_covariates_to_events(events, field_sampler=sampler, source="t")
    assert (drops["reason"] == DROP_REASON_LAND_MASK).any()
    assert qc["drop_summary"][DROP_REASON_LAND_MASK] >= 1


def test_drop_too_few_track_points() -> None:
    events = _events()
    events.loc[2, COL_STOP_LAT] = events.loc[2, COL_START_LAT]
    events.loc[2, COL_STOP_LON] = events.loc[2, COL_START_LON]
    _, qc, drops = join_covariates_to_events(events, field_sampler=lambda *_: {"T3m": 1.0}, source="t")
    assert (drops["reason"] == DROP_REASON_TOO_FEW_TRACK_POINTS).any()
    assert qc["drop_summary"][DROP_REASON_TOO_FEW_TRACK_POINTS] >= 1


def test_drop_missing_covariate_per_field() -> None:
    events = _events()

    def sampler(_lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        return {}

    _, qc, drops = join_covariates_to_events(events, field_sampler=sampler, source="t")
    assert (drops["reason"] == DROP_REASON_MISSING_COVARIATE).any()
    assert qc["drop_summary"][DROP_REASON_MISSING_COVARIATE] >= 1


def test_writes_drop_parquet(tmp_path) -> None:
    events = _events()
    drops_path = tmp_path / "cufes_physics_covariate_drops.parquet"
    _, qc, _ = join_covariates_to_events(
        events,
        field_sampler=lambda *_: {},
        source="t",
        drops_parquet_path=drops_path,
    )
    assert drops_path.is_file()
    assert qc["drops_parquet_path"] == str(drops_path)
