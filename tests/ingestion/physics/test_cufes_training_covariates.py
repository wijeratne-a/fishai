"""CUFES × GLORYS training covariate table (synthetic / mocked only)."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

from fishai.ingestion.copernicus_compliance import (
    GLORYS_CREDIT_TEXT,
    GLORYS_DOI,
    append_pull_log,
    build_pull_record,
)
from fishai.ingestion.physics.bathymetry import (
    WCOFS_BOTTOM_DEPTH_SOURCE,
    WCOFS_BOTTOM_DEPTH_VARIABLE,
)
from fishai.ingestion.physics.covariates import (
    CUFES_COVARIATE_FIELDS,
    DROP_REASON_OUTSIDE_WCOFS_DOMAIN,
)
from fishai.ingestion.physics.cufes_training_covariates import (
    TRAINING_OUTPUT_COLUMNS,
    build_cufes_training_covariates_table,
    plan_glorys_subset_batches,
    run_build_cufes_training_covariates,
    unique_event_days,
    write_training_covariates_parquet,
)
from fishai.ingestion.physics.glorys_training_build import GLORYS_COVARIATE_SOURCE_COPERNICUS
from cufes_glorys_synthetic_fixture import glorys_store_from_synthetic_days
from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID_MY,
    glorys_product_for_date,
)
from fishai.ingestion.sources import require_approved


def _small_glorys_axes() -> tuple[np.ndarray, np.ndarray]:
    lat = np.linspace(33.0, 33.2, 5)
    lon = np.linspace(-120.5, -120.3, 5)
    return lat, lon


def _synthetic_events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": ["e1", "e2", "e3"],
            "start_time": pd.to_datetime(
                [
                    "2021-06-30T12:00:00Z",
                    "2021-07-01T08:00:00Z",
                    "2020-01-15T12:00:00Z",
                ],
                utc=True,
            ),
            "stop_time": pd.to_datetime(
                [
                    "2021-06-30T12:10:00Z",
                    "2021-07-01T08:12:00Z",
                    "2020-01-15T12:10:00Z",
                ],
                utc=True,
            ),
            "start_latitude": [33.0, 33.1, 33.2],
            "start_longitude": [-120.0, -120.1, -120.2],
            "stop_latitude": [33.01, 33.11, 33.21],
            "stop_longitude": [-119.99, -120.09, -120.19],
        }
    )


def test_glorys_product_is_my_for_pre_and_post_legacy_myint_dates() -> None:
    """Live catalogue exposes only ``my`` (``myint`` removed in PR #24)."""
    assert glorys_product_for_date(dt.date(2021, 6, 30)) == PRODUCT_ID_MY
    assert glorys_product_for_date(dt.date(2021, 7, 1)) == PRODUCT_ID_MY


def test_training_glorys_product_ids_track_glorys_product_for_date(tmp_path: Path) -> None:
    """CUFES training pulls and source_product must match PR #7 date-based product choice."""
    start = dt.date(1996, 3, 16)
    end = dt.date(2022, 4, 19)
    sample_days: list[dt.date] = [start, end, dt.date(2021, 6, 30), dt.date(2021, 7, 1)]
    cur = start
    while cur <= end:
        sample_days.append(cur)
        cur += dt.timedelta(days=45)
    sample_days = sorted(set(sample_days))

    for day in sample_days:
        expected = glorys_product_for_date(day)
        batches = plan_glorys_subset_batches([day])
        assert len(batches) == 1
        assert batches[0].dataset_id == expected

    events = pd.DataFrame(
        {
            "event_id": [f"e_{d.isoformat()}" for d in sample_days[:6]],
            "start_time": pd.to_datetime(
                [f"{d.isoformat()}T12:00:00Z" for d in sample_days[:6]], utc=True
            ),
            "stop_time": pd.to_datetime(
                [f"{d.isoformat()}T12:10:00Z" for d in sample_days[:6]], utc=True
            ),
            "start_latitude": [33.0] * 6,
            "start_longitude": [-120.0] * 6,
            "stop_latitude": [33.01] * 6,
            "stop_longitude": [-119.99] * 6,
        }
    )
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store)
    for _, ev in events.iterrows():
        mid_day = pd.Timestamp(ev["start_time"]).date()
        expected = glorys_product_for_date(mid_day)
        assert out.loc[out["event_id"] == ev["event_id"], "source_product"].iloc[0] == expected


def test_plan_batches_one_batch_per_month_same_dataset_id() -> None:
    days = [
        dt.date(2021, 6, 15),
        dt.date(2021, 6, 30),
        dt.date(2021, 7, 1),
        dt.date(2021, 7, 20),
    ]
    batches = plan_glorys_subset_batches(days)
    assert len(batches) == 2
    assert batches[0].dataset_id == PRODUCT_ID_MY
    assert batches[1].dataset_id == PRODUCT_ID_MY


def test_one_row_per_event_id_and_required_columns(tmp_path: Path) -> None:
    events = _synthetic_events()
    days = unique_event_days(events)
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(days, lat=lat, lon=lon)
    out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store, provenance="test")
    assert len(out) == len(events)
    assert out["event_id"].tolist() == events["event_id"].tolist()
    assert list(out.columns) == list(TRAINING_OUTPUT_COLUMNS)
    for col in TRAINING_OUTPUT_COLUMNS:
        assert col in out.columns


def test_no_zero_filled_nans_for_missing_bottom_depth() -> None:
    events = _synthetic_events().iloc[[0]].copy()
    days = unique_event_days(events)
    lat, lon = _small_glorys_axes()
    has_source = np.zeros((lat.size, lon.size), dtype=bool)
    store = glorys_store_from_synthetic_days(
        days,
        wcofs_h_m=np.full((lat.size, lon.size), np.nan),
        has_source=has_source,
        lat=lat,
        lon=lon,
    )
    out, _qc, drops, _floor = build_cufes_training_covariates_table(events, store)
    assert bool(out.iloc[0]["excluded"])
    assert pd.isna(out.iloc[0]["bottom_depth_m"])
    assert out.iloc[0]["bottom_depth_m"] != 0.0
    assert (drops["reason"] == DROP_REASON_OUTSIDE_WCOFS_DOMAIN).any()


def test_wcofs_h_audit_m_retained_when_row_excluded() -> None:
    events = _synthetic_events().iloc[[0]].copy()
    days = unique_event_days(events)
    lat, lon = _small_glorys_axes()
    has_source = np.zeros((lat.size, lon.size), dtype=bool)
    store = glorys_store_from_synthetic_days(
        days,
        wcofs_h_m=np.full((lat.size, lon.size), np.nan),
        has_source=has_source,
        lat=lat,
        lon=lon,
    )
    out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store)
    assert bool(out.iloc[0]["excluded"])
    assert pd.isna(out.iloc[0]["bottom_depth_m"])
    assert pd.isna(out.iloc[0]["wcofs_h_audit_m"])


def test_excluded_reason_nonempty_iff_excluded() -> None:
    events = _synthetic_events()
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store)
    for _, row in out.iterrows():
        if row["excluded"]:
            assert str(row["excluded_reason"]).strip() != ""
        else:
            assert row["excluded_reason"] == ""


def test_source_product_matches_event_date() -> None:
    events = _synthetic_events()
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store)
    assert out.loc[out["event_id"] == "e1", "source_product"].iloc[0] == glorys_product_for_date(
        dt.date(2021, 6, 30)
    )
    assert out.loc[out["event_id"] == "e2", "source_product"].iloc[0] == glorys_product_for_date(
        dt.date(2021, 7, 1)
    )


def test_pull_log_includes_version_and_sha256(tmp_path: Path) -> None:
    log_path = tmp_path / "copernicus_pull_log.jsonl"
    rec = build_pull_record(
        dataset_id=PRODUCT_ID_MY,
        date_start="2020-06-01",
        date_end="2020-06-30",
        variables=("thetao",),
        bbox=(32.0, 35.0, -121.0, -117.0),
        dataset_version="2023.1",
        file_sha256="abc123",
    )
    append_pull_log(rec, log_path=log_path)
    loaded = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert loaded["dataset_version"] == "2023.1"
    assert loaded["file_sha256"] == "abc123"


def test_training_parquet_write_read_round_trip(tmp_path: Path) -> None:
    from cufes_training_test_helpers import live_store_with_wcofs_h_and_glorys_days

    events = pd.DataFrame(
        {
            "event_id": ["e_pilot"],
            "start_time": pd.to_datetime(["2021-06-30T12:00:00Z"], utc=True),
            "stop_time": pd.to_datetime(["2021-06-30T12:10:00Z"], utc=True),
            "start_latitude": [33.15],
            "start_longitude": [-120.2],
            "stop_latitude": [33.16],
            "stop_longitude": [-120.19],
        }
    )
    days = unique_event_days(events)
    store = live_store_with_wcofs_h_and_glorys_days(tmp_path, days)
    assert store.covariate_data_source == GLORYS_COVARIATE_SOURCE_COPERNICUS
    assert store.hmin_source == "netcdf_global_attr_hmin"
    out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store)
    path = tmp_path / "cufes_training_covariates.parquet"
    write_training_covariates_parquet(
        out,
        path,
        entry=require_approved("glorys", purpose="training"),
        store=store,
    )
    assert path.is_file()
    round_trip = pd.read_parquet(path)
    assert len(round_trip) == len(events)
    assert list(round_trip.columns) == list(TRAINING_OUTPUT_COLUMNS)
    assert round_trip["event_id"].tolist() == events["event_id"].tolist()
    row = round_trip.iloc[0]
    assert not bool(row["excluded"])
    assert np.isfinite(row["T3m"])
    assert np.isfinite(row["bottom_depth_m"])
    meta = pq.read_metadata(path).metadata
    raw = meta.get(b"glorys")
    assert raw is not None
    doc = json.loads(raw.decode())
    assert GLORYS_CREDIT_TEXT in doc["attribution"]
    assert GLORYS_DOI in doc["attribution"]
    assert doc["covariate_data_source"] == GLORYS_COVARIATE_SOURCE_COPERNICUS
    bottom = doc["bottom_depth_m"]
    assert bottom["source"] == WCOFS_BOTTOM_DEPTH_SOURCE
    assert bottom["variable"] == WCOFS_BOTTOM_DEPTH_VARIABLE
    assert bottom["hmin_source"] == "netcdf_global_attr_hmin"


def test_dry_run_prints_batch_count(tmp_path: Path) -> None:
    events = _synthetic_events()
    events_path = tmp_path / "events.parquet"
    events.to_parquet(events_path, index=False)
    result = run_build_cufes_training_covariates(
        events_path=events_path,
        dry_run=True,
    )
    assert result["subset_batch_count"] >= 1
    assert result["input_event_count"] == 3


def test_depth_at_model_floor_when_near_roms_hmin() -> None:
    events = _synthetic_events().iloc[[0]].copy()
    lat, lon = _small_glorys_axes()
    hmin = 10.0
    store = glorys_store_from_synthetic_days(
        unique_event_days(events),
        lat=lat,
        lon=lon,
        wcofs_h_m=np.full((lat.size, lon.size), hmin + 0.2),
        roms_hmin_m=hmin,
        hmin_source="netcdf_global_attr_hmin",
    )
    out, _qc, _drops, floor_qc = build_cufes_training_covariates_table(events, store)
    assert bool(out.iloc[0]["depth_at_model_floor"])
    assert floor_qc["depth_at_model_floor_count"] == 1
    assert floor_qc["hmin_source"] == "netcdf_global_attr_hmin"


def test_covariates_not_zero_when_present() -> None:
    events = _synthetic_events().iloc[[0]]
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store)
    assert np.isfinite(out.iloc[0]["T3m"])
    for field in CUFES_COVARIATE_FIELDS:
        if field == "upwelling":
            continue
        if np.isfinite(out.iloc[0][field]):
            assert out.iloc[0][field] != 0.0


def test_upwelling_nan_without_excluding_events(tmp_path: Path) -> None:
    from fishai.ingestion.physics.covariates import DROP_REASON_MISSING_COVARIATE
    from fishai.ingestion.physics.wind_shared_forcing import (
        UPWELLING_STATUS_NO_CONSISTENT_WIND,
    )

    events = _synthetic_events()
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, drops, _floor = build_cufes_training_covariates_table(
        events,
        store,
        drops_parquet_path=tmp_path / "drops.parquet",
    )
    assert len(out) == len(events)
    assert out["upwelling"].isna().all()
    assert (out["upwelling_status"] == UPWELLING_STATUS_NO_CONSISTENT_WIND).all()
    assert not out["excluded"].any()
    upwelling_drops = drops[
        (drops["reason"] == DROP_REASON_MISSING_COVARIATE) & (drops["covariate"] == "upwelling")
    ]
    assert upwelling_drops.empty
