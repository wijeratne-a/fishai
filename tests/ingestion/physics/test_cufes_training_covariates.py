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
    glorys_store_from_synthetic_days,
    plan_glorys_subset_batches,
    run_build_cufes_training_covariates,
    unique_event_days,
    write_training_covariates_parquet,
)
from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_MYINT_ID,
    PRODUCT_MY_ID,
    glorys_dataset_for_date,
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


def test_glorys_product_switch_at_my_myint_boundary() -> None:
    assert glorys_dataset_for_date(dt.date(2021, 6, 30))[0] == PRODUCT_MY_ID
    assert glorys_dataset_for_date(dt.date(2021, 7, 1))[0] == PRODUCT_MYINT_ID


def test_plan_batches_splits_my_and_myint_months() -> None:
    days = [
        dt.date(2021, 6, 15),
        dt.date(2021, 6, 30),
        dt.date(2021, 7, 1),
        dt.date(2021, 7, 20),
    ]
    batches = plan_glorys_subset_batches(days)
    assert len(batches) == 2
    assert batches[0].dataset_id == PRODUCT_MY_ID
    assert batches[1].dataset_id == PRODUCT_MYINT_ID


def test_one_row_per_event_id_and_required_columns(tmp_path: Path) -> None:
    events = _synthetic_events()
    days = unique_event_days(events)
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(days, lat=lat, lon=lon)
    out, _qc, _drops = build_cufes_training_covariates_table(events, store, provenance="test")
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
    out, _qc, drops = build_cufes_training_covariates_table(events, store)
    assert bool(out.iloc[0]["excluded"])
    assert pd.isna(out.iloc[0]["bottom_depth_m"])
    assert out.iloc[0]["bottom_depth_m"] != 0.0
    assert (drops["reason"] == DROP_REASON_OUTSIDE_WCOFS_DOMAIN).any()


def test_excluded_reason_nonempty_iff_excluded() -> None:
    events = _synthetic_events()
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops = build_cufes_training_covariates_table(events, store)
    for _, row in out.iterrows():
        if row["excluded"]:
            assert str(row["excluded_reason"]).strip() != ""
        else:
            assert row["excluded_reason"] == ""


def test_source_product_matches_event_date() -> None:
    events = _synthetic_events()
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops = build_cufes_training_covariates_table(events, store)
    assert out.loc[out["event_id"] == "e1", "source_product"].iloc[0] == PRODUCT_MY_ID
    assert out.loc[out["event_id"] == "e2", "source_product"].iloc[0] == PRODUCT_MYINT_ID


def test_pull_log_includes_version_and_sha256(tmp_path: Path) -> None:
    log_path = tmp_path / "copernicus_pull_log.jsonl"
    rec = build_pull_record(
        dataset_id=PRODUCT_MY_ID,
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


def test_training_parquet_metadata_has_credit_and_doi(tmp_path: Path) -> None:
    events = _synthetic_events().iloc[[0]]
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops = build_cufes_training_covariates_table(events, store)
    path = tmp_path / "out.parquet"
    write_training_covariates_parquet(out, path, entry=require_approved("glorys", purpose="training"))
    meta = pq.read_metadata(path).metadata
    raw = meta.get(b"glorys")
    assert raw is not None
    doc = json.loads(raw.decode())
    assert GLORYS_CREDIT_TEXT in doc["attribution"]
    assert GLORYS_DOI in doc["attribution"]
    bottom = doc["bottom_depth_m"]
    assert bottom["source"] == WCOFS_BOTTOM_DEPTH_SOURCE
    assert bottom["variable"] == WCOFS_BOTTOM_DEPTH_VARIABLE


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


def test_covariates_not_zero_when_present() -> None:
    events = _synthetic_events().iloc[[0]]
    lat, lon = _small_glorys_axes()
    store = glorys_store_from_synthetic_days(unique_event_days(events), lat=lat, lon=lon)
    out, _qc, _drops = build_cufes_training_covariates_table(events, store)
    assert np.isfinite(out.iloc[0]["T3m"])
    for field in CUFES_COVARIATE_FIELDS:
        if np.isfinite(out.iloc[0][field]):
            assert out.iloc[0][field] != 0.0 or field == "upwelling"
