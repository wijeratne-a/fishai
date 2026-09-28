"""Covariate join drop-table reasons."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd

import pytest

from fishai.ingestion.physics.covariates import (
    COVARIATE_FIELDS_EXEMPT_FROM_MISSING_EXCLUSION,
    CUFES_COVARIATE_FIELDS,
    COL_START_LAT,
    COL_START_LON,
    COL_STOP_LAT,
    COL_STOP_LON,
    CufesEventValidationError,
    DEFAULT_COVARIATE_DROP_SUMMARY_JSON_NAME,
    DEFAULT_COVARIATE_DROPS_PARQUET_NAME,
    DROP_REASON_LAND_MASK,
    DROP_REASON_MISSING_COVARIATE,
    DROP_REASON_MISSING_ENDPOINT,
    DROP_REASON_TOO_FEW_TRACK_POINTS,
    DROP_REASONS_ALL,
    DROP_SUMMARY_JSON_SCHEMA_VERSION,
    SAMPLER_LAND_MASK_KEY,
    join_covariates_to_events,
)


def _assert_json_ints(obj: Any) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            _assert_json_ints(v)
    elif isinstance(obj, list):
        for v in obj:
            _assert_json_ints(v)
    else:
        assert isinstance(obj, int)


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


def test_drop_summary_input_event_count_matches_unique_input_rows() -> None:
    events = _events()
    out, qc, _ = join_covariates_to_events(events, field_sampler=lambda *_: {}, source="t")
    unique_in = events["event_id"].nunique()
    assert qc["drop_summary"]["input_event_count"] == unique_in
    assert qc["drop_summary"]["input_event_count"] == len(events)
    assert len(out) == qc["drop_summary"]["input_event_count"]


def test_join_rejects_duplicate_event_id() -> None:
    events = _events()
    events = pd.concat([events, events.iloc[[0]]], ignore_index=True)
    with pytest.raises(CufesEventValidationError, match="duplicate event_id"):
        join_covariates_to_events(events, field_sampler=lambda *_: {}, source="t")


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


def test_land_mask_does_not_inflate_missing_by_field_counts() -> None:
    events = _events().iloc[[0]]

    def sampler(_lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        vals = {field: 1.0 for field in CUFES_COVARIATE_FIELDS}
        vals[SAMPLER_LAND_MASK_KEY] = True
        return vals

    _, qc, _ = join_covariates_to_events(events, field_sampler=sampler, source="t")
    assert qc["missing_by_field"] == {field: 0 for field in CUFES_COVARIATE_FIELDS}


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


def test_drop_summary_counts_unique_events_per_reason() -> None:
    """One event missing two covariates → one unique missing_covariate, not two."""
    events = _events().iloc[[0]]
    _, qc, drops = join_covariates_to_events(events, field_sampler=lambda *_: {}, source="t")
    missing_rows = drops[drops["reason"] == DROP_REASON_MISSING_COVARIATE]
    expected_missing_fields = len(CUFES_COVARIATE_FIELDS) - len(
        COVARIATE_FIELDS_EXEMPT_FROM_MISSING_EXCLUSION
    )
    assert len(missing_rows) == expected_missing_fields
    assert qc["drop_summary"][DROP_REASON_MISSING_COVARIATE] == 1
    assert qc["rows_by_reason"][DROP_REASON_MISSING_COVARIATE] == len(missing_rows)
    assert qc["drop_summary"]["dropped_unique_total"] == 1
    assert qc["dropped_unique_total"] == 1


def test_drop_summary_two_reasons_one_unique_event() -> None:
    events = _events().iloc[[2]].copy()
    events.loc[events.index[0], COL_STOP_LAT] = events.loc[events.index[0], COL_START_LAT]
    events.loc[events.index[0], COL_STOP_LON] = events.loc[events.index[0], COL_START_LON]

    def sampler(_lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        return {SAMPLER_LAND_MASK_KEY: True, "T3m": 1.0}

    _, qc, drops = join_covariates_to_events(events, field_sampler=sampler, source="t")
    eid = events.iloc[0]["event_id"]
    event_drops = drops[drops["event_id"] == eid]
    reasons = set(event_drops["reason"])
    assert DROP_REASON_TOO_FEW_TRACK_POINTS in reasons
    assert DROP_REASON_LAND_MASK in reasons
    assert qc["drop_summary"][DROP_REASON_TOO_FEW_TRACK_POINTS] == 1
    assert qc["drop_summary"][DROP_REASON_LAND_MASK] == 1
    assert qc["drop_summary"]["dropped_unique_total"] == 1


def test_excluded_flag_and_nan_covariates_for_land_and_short_track() -> None:
    events = _events().copy()
    events.loc[1, COL_STOP_LAT] = 33.51
    events.loc[1, COL_STOP_LON] = -119.99
    events.loc[2, COL_STOP_LAT] = events.loc[2, COL_START_LAT]
    events.loc[2, COL_STOP_LON] = events.loc[2, COL_START_LON]
    fields = ("T3m", "S3m", "MLD_m", "sst_grad", "front_distance_km", "upwelling")

    def sampler(lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        if 33.49 <= lat <= 33.52:
            return {SAMPLER_LAND_MASK_KEY: True, "T3m": 99.0}
        return {field: 1.0 for field in fields}

    out, _, _ = join_covariates_to_events(events, field_sampler=sampler, source="t")
    assert bool(out.loc[1, "excluded"]) is True
    assert bool(out.loc[2, "excluded"]) is True
    for idx in (1, 2):
        for col in fields:
            assert pd.isna(out.loc[idx, col])
    assert bool(out.loc[0, "excluded"]) is False
    assert np.isfinite(out.loc[0, "T3m"])


def test_writes_drop_parquet(tmp_path) -> None:
    events = _events()
    drops_path = tmp_path / DEFAULT_COVARIATE_DROPS_PARQUET_NAME
    _, qc, _ = join_covariates_to_events(
        events,
        field_sampler=lambda *_: {},
        source="t",
        drops_parquet_path=drops_path,
    )
    assert drops_path.is_file()
    assert qc["drops_parquet_path"] == str(drops_path)


def test_writes_drop_summary_json_round_trip(tmp_path) -> None:
    events = _events()
    events.loc[0, COL_STOP_LAT] = np.nan
    drops_path = tmp_path / DEFAULT_COVARIATE_DROPS_PARQUET_NAME
    summary_path = tmp_path / DEFAULT_COVARIATE_DROP_SUMMARY_JSON_NAME

    def sampler(_lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        return {field: 1.0 for field in CUFES_COVARIATE_FIELDS}

    _, qc, drops = join_covariates_to_events(
        events,
        field_sampler=sampler,
        source="t",
        drops_parquet_path=drops_path,
        drop_summary_json_path=summary_path,
    )
    assert summary_path.is_file()
    assert qc["drop_summary_json_path"] == str(summary_path)
    loaded = json.loads(summary_path.read_text(encoding="utf-8"))
    unique_in = int(events["event_id"].nunique())
    assert loaded["schema_version"] == DROP_SUMMARY_JSON_SCHEMA_VERSION
    assert loaded["input_event_count"] == unique_in
    assert loaded["input_event_count"] == qc["drop_summary"]["input_event_count"]
    assert loaded["dropped_unique_total"] == int(drops["event_id"].nunique())
    assert loaded["dropped_unique_total"] == qc["drop_summary"]["dropped_unique_total"]
    for reason in DROP_REASONS_ALL:
        assert reason in loaded["unique_by_reason"]
        assert reason in loaded["rows_by_reason"]
        assert loaded["unique_by_reason"][reason] == qc["drop_summary"].get(reason, 0)
        assert loaded["rows_by_reason"][reason] == qc["rows_by_reason"].get(reason, 0)
    assert loaded["unique_by_reason"][DROP_REASON_MISSING_ENDPOINT] >= 1
    assert loaded["unique_by_reason"][DROP_REASON_LAND_MASK] == 0
    _assert_json_ints(loaded)


def test_drop_summary_json_all_reasons_zero_when_no_drops(tmp_path) -> None:
    events = _events().iloc[[0]].copy()
    summary_path = tmp_path / DEFAULT_COVARIATE_DROP_SUMMARY_JSON_NAME

    def sampler(_lat: float, _lon: float, _t: pd.Timestamp) -> dict:
        return {field: 1.0 for field in CUFES_COVARIATE_FIELDS}

    join_covariates_to_events(
        events,
        field_sampler=sampler,
        source="t",
        drop_summary_json_path=summary_path,
    )
    loaded = json.loads(summary_path.read_text(encoding="utf-8"))
    for reason in DROP_REASONS_ALL:
        assert loaded["unique_by_reason"][reason] == 0
        assert loaded["rows_by_reason"][reason] == 0
    assert loaded["dropped_unique_total"] == 0
