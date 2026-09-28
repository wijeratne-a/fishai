"""CUFES event_id covariate join along tow segments (synthetic events)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest

from fishai.ingestion.physics.covariates import (
    CUFES_COVARIATE_FIELDS,
    COL_START_TIME,
    COL_STOP_LAT,
    COL_STOP_TIME,
    CufesEventValidationError,
    event_mid_time,
    great_circle_sample_points,
    join_covariates_to_events,
    normalize_cufes_events_for_physics,
    validate_cufes_events,
)
from fishai.ingestion.physics.cufes_training_covariates import unique_event_days
from fishai.ingestion.physics.store import event_covariates_parquet


def _synthetic_events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": [
                "CUFES:2020-01:SH01:42",
                "CUFES:2020-01:SH01:43",
                "CUFES:2020-02:SH02:7",
            ],
            "start_time": pd.to_datetime(
                ["2020-01-15T12:00:00Z", "2020-01-15T12:05:00Z", "2020-02-01T08:00:00Z"],
                utc=True,
            ),
            "stop_time": pd.to_datetime(
                ["2020-01-15T12:10:00Z", "2020-01-15T12:15:00Z", "2020-02-01T08:12:00Z"],
                utc=True,
            ),
            "start_latitude": [33.5, 33.51, 34.2],
            "start_longitude": [-120.1, -120.09, -119.5],
            "stop_latitude": [33.52, 33.53, 34.22],
            "stop_longitude": [-120.08, -120.07, -119.48],
        }
    )


def test_normalize_pr4_cufes_events_parquet_schema() -> None:
    """PR #4 ``row_to_event`` columns map to the physics join contract."""
    pr4 = pd.DataFrame(
        {
            "event_id": ["CUFES:2020-01:SH01:42"],
            "time": "2020-01-15T12:00:00+00:00",
            "lat": 33.5,
            "lon": -120.1,
            "stop_time": "2020-01-15T12:10:00+00:00",
            "stop_lat": 33.52,
            "stop_lon": -120.08,
            "volume_m3": 12.0,
            "pump_readings_used": 2,
        }
    )
    norm = normalize_cufes_events_for_physics(pr4)
    validate_cufes_events(norm)
    assert norm[COL_START_TIME].dt.tz is not None
    out, _, _ = join_covariates_to_events(
        pr4,
        field_sampler=lambda *_: {f: 1.0 for f in CUFES_COVARIATE_FIELDS},
        source="test",
    )
    assert len(out) == 1


def test_midpoint_utc_date_crosses_midnight_for_glorys_day() -> None:
    events = pd.DataFrame(
        {
            "event_id": ["midnight_cross"],
            "start_time": pd.to_datetime(["2021-06-30T23:50:00Z"], utc=True),
            "stop_time": pd.to_datetime(["2021-07-01T00:10:00Z"], utc=True),
            "start_latitude": [33.0],
            "start_longitude": [-120.0],
            "stop_latitude": [33.01],
            "stop_longitude": [-119.99],
        }
    )
    mid = event_mid_time(events.iloc[0])
    assert mid.date().isoformat() == "2021-07-01"
    assert unique_event_days(events) == [dt.date(2021, 7, 1)]


def test_rejects_duplicate_event_id() -> None:
    events = _synthetic_events()
    events = pd.concat([events, events.iloc[[0]]], ignore_index=True)
    with pytest.raises(CufesEventValidationError, match="duplicate"):
        validate_cufes_events(events)


def test_great_circle_sample_at_least_start_mid_stop() -> None:
    pts = great_circle_sample_points(33.0, -120.0, 33.1, -120.0, grid_cell_km=4.0)
    assert len(pts) >= 3
    assert pts[0] == (33.0, -120.0)
    assert pts[-1] == (33.1, -120.0)


def test_join_one_row_per_event_id_segment_mean() -> None:
    events = _synthetic_events()

    def field_sampler(lat: float, lon: float, _t: pd.Timestamp) -> dict:
        return {field: lat for field in CUFES_COVARIATE_FIELDS}

    out, qc, _drops = join_covariates_to_events(
        events, field_sampler=field_sampler, source="wcofs", provenance="test-fixture"
    )
    assert len(out) == len(events)
    assert out["event_id"].tolist() == events["event_id"].tolist()
    assert (~out["excluded"]).all()
    assert qc["events_endpoint_missing"] == 0
    assert qc["missing_by_field"] == {c: 0 for c in CUFES_COVARIATE_FIELDS}
    expected_mean = np.mean([33.5, 33.52])
    assert abs(out.loc[0, "T3m"] - expected_mean) < 0.02


def test_missing_endpoint_leaves_nan_and_qc_count() -> None:
    events = _synthetic_events().iloc[[0, 1]].copy()
    events.loc[events.index[1], COL_STOP_LAT] = np.nan

    def field_sampler(_lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        return {field: 1.0 for field in CUFES_COVARIATE_FIELDS}

    out, qc, _drops = join_covariates_to_events(
        events,
        field_sampler=field_sampler,
        source="test",
    )
    assert bool(out.loc[events.index[1], "excluded"])
    assert pd.isna(out.loc[events.index[1], "T3m"])
    assert not bool(out.loc[events.index[0], "excluded"])
    assert qc["events_endpoint_missing"] == 1
    assert qc["missing_by_field"]["T3m"] == 1


def test_missing_covariates_left_nan_with_qc_counts() -> None:
    events = _synthetic_events().iloc[[0, 2]].copy()

    def field_sampler(lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        if lat > 34.0:
            return {"T3m": 15.0}
        return {field: 1.0 for field in CUFES_COVARIATE_FIELDS}

    out, qc, _drops = join_covariates_to_events(events, field_sampler=field_sampler, source="test")
    assert not bool(out.iloc[0]["excluded"])
    assert np.isfinite(out.iloc[0]["T3m"])
    assert bool(out.iloc[1]["excluded"])
    assert all(pd.isna(out.iloc[1][c]) for c in CUFES_COVARIATE_FIELDS)
    assert qc["missing_by_field"]["S3m"] >= 1


def test_event_covariates_parquet_requires_event_id(tmp_path) -> None:
    events = _synthetic_events()

    def field_sampler(_lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        return {}

    out, _, _drops = join_covariates_to_events(events, field_sampler=field_sampler, source="test")
    path = tmp_path / "cufes_physics_covariates.parquet"
    event_covariates_parquet(out, path)
    loaded = pd.read_parquet(path)
    assert list(loaded["event_id"]) == list(events["event_id"])
