"""CUFES event_id covariate join (synthetic events; no network)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fishai.ingestion.physics.covariates import (
    CUFES_COVARIATE_FIELDS,
    CufesEventValidationError,
    join_covariates_to_events,
    validate_cufes_events,
)
from fishai.ingestion.physics.store import event_covariates_parquet


def _synthetic_events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": [
                "CUFES:2020-01:SH01:42",
                "CUFES:2020-01:SH01:43",
                "CUFES:2020-02:SH02:7",
            ],
            "time": pd.to_datetime(
                ["2020-01-15T12:00:00Z", "2020-01-15T12:05:00Z", "2020-02-01T08:00:00Z"],
                utc=True,
            ),
            "latitude": [33.5, 33.51, 34.2],
            "longitude": [-120.1, -120.09, -119.5],
        }
    )


def test_rejects_duplicate_event_id() -> None:
    events = _synthetic_events()
    events = pd.concat([events, events.iloc[[0]]], ignore_index=True)
    with pytest.raises(CufesEventValidationError, match="duplicate"):
        validate_cufes_events(events)


def test_join_one_row_per_event_id_exact_set() -> None:
    events = _synthetic_events()

    def sampler(event: pd.Series) -> dict:
        return {field: float(event["latitude"]) for field in CUFES_COVARIATE_FIELDS}

    out, qc = join_covariates_to_events(
        events, sampler=sampler, source="wcofs", provenance="test-fixture"
    )
    assert len(out) == len(events)
    assert out["event_id"].tolist() == events["event_id"].tolist()
    assert set(out["event_id"]) == set(events["event_id"])
    assert qc == {c: 0 for c in CUFES_COVARIATE_FIELDS}
    assert out.loc[0, "source"] == "wcofs"


def test_missing_covariates_left_nan_with_qc_counts() -> None:
    events = _synthetic_events()

    def sampler(event: pd.Series) -> dict:
        if event["event_id"] == "CUFES:2020-01:SH01:42":
            return {"T3m": 15.0}
        return {}

    out, qc = join_covariates_to_events(events, sampler=sampler, source="test")
    assert np.isfinite(out.loc[0, "T3m"])
    assert pd.isna(out.loc[0, "S3m"])
    assert qc["T3m"] == 2
    assert qc["S3m"] == 3


def test_event_covariates_parquet_requires_event_id(tmp_path) -> None:
    events = _synthetic_events()
    out, _ = join_covariates_to_events(events, sampler=lambda _e: {}, source="test")
    path = tmp_path / "cufes_physics_covariates.parquet"
    event_covariates_parquet(out, path)
    loaded = pd.read_parquet(path)
    assert list(loaded["event_id"]) == list(events["event_id"])
