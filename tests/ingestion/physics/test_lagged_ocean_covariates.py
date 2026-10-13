"""Operational lag covariates (synthetic GLORYS store)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import pytest

from fishai.ingestion.physics.covariates import COL_EVENT_ID
from fishai.ingestion.physics.lagged_ocean_covariates import (
    attach_lagged_physics_columns,
    lagged_column_name,
    sample_lagged_physics_for_event,
)
from cufes_glorys_synthetic_fixture import glorys_store_from_synthetic_days

GLORYS_DAY = dt.date(2021, 7, 15)
EVENT_DAY = dt.date(2021, 7, 22)


def _point_event() -> pd.Series:
    return pd.Series(
        {
            COL_EVENT_ID: "CPSTrawl:209901:SY:lag",
            "start_time": pd.Timestamp(f"{EVENT_DAY.isoformat()}T12:00:00Z"),
            "stop_time": pd.Timestamp(f"{EVENT_DAY.isoformat()}T12:30:00Z"),
            "start_latitude": 33.5,
            "start_longitude": -120.0,
            "stop_latitude": 33.5,
            "stop_longitude": -120.0,
        }
    )


def test_lagged_sampler_uses_shifted_day() -> None:
    store = glorys_store_from_synthetic_days([GLORYS_DAY, EVENT_DAY])
    event = _point_event()
    out = sample_lagged_physics_for_event(event, store, lag_days=(7,))
    col = lagged_column_name("T3m", 7)
    assert col in out
    mid_t = pd.Timestamp(f"{EVENT_DAY.isoformat()}T12:15:00Z")
    direct = store.field_sampler(33.5, -120.0, mid_t - pd.Timedelta(days=7))
    assert out[col] == pytest.approx(direct["T3m"], rel=1e-6)


def test_attach_lagged_columns_one_row_per_event() -> None:
    store = glorys_store_from_synthetic_days([GLORYS_DAY, EVENT_DAY])
    events = pd.DataFrame([_point_event()])
    lag_df = attach_lagged_physics_columns(events, store, lag_days=(7, 14))
    assert len(lag_df) == 1
    assert lagged_column_name("MLD_m", 14) in lag_df.columns
