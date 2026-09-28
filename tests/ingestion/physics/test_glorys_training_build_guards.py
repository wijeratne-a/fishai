"""Production GLORYS training build must never stamp Copernicus metadata on synthetic data."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import pytest

from fishai.ingestion.physics.cufes_training_covariates import (
    run_build_cufes_training_covariates,
    write_training_covariates_parquet,
)
from fishai.ingestion.physics.glorys_training_build import (
    REASON_CREDENTIALS_MISSING,
    REASON_SYNTHETIC_PROVENANCE_FORBIDDEN,
    GlorysTrainingBuildError,
    SYNTHETIC_TEST_FIXTURE_SOURCE,
)
from fishai.ingestion.sources import require_approved
from tests.ingestion.physics.cufes_glorys_synthetic_fixture import (
    glorys_store_from_synthetic_days,
)


def test_live_build_fails_without_credentials(tmp_path: Path) -> None:
    events = pd.DataFrame(
        {
            "event_id": ["e1"],
            "start_time": pd.to_datetime(["2020-06-15T12:00:00Z"], utc=True),
            "stop_time": pd.to_datetime(["2020-06-15T12:10:00Z"], utc=True),
            "start_latitude": [33.0],
            "start_longitude": [-120.0],
            "stop_latitude": [33.01],
            "stop_longitude": [-119.99],
        }
    )
    events_path = tmp_path / "events.parquet"
    events.to_parquet(events_path, index=False)
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        run_build_cufes_training_covariates(events_path=events_path, output_path=tmp_path / "out.parquet")
    assert excinfo.value.reason_code == REASON_CREDENTIALS_MISSING
    assert not (tmp_path / "out.parquet").exists()


def test_synthetic_fixture_cannot_write_glorys_parquet(tmp_path: Path) -> None:
    store = glorys_store_from_synthetic_days([dt.date(2020, 1, 1)])
    assert store.covariate_data_source == SYNTHETIC_TEST_FIXTURE_SOURCE
    out = pd.DataFrame([{"event_id": "e1", "T3m": 1.0, "excluded": False}])
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        write_training_covariates_parquet(
            out,
            tmp_path / "bad.parquet",
            entry=require_approved("glorys", purpose="training"),
            store=store,
        )
    assert excinfo.value.reason_code == REASON_SYNTHETIC_PROVENANCE_FORBIDDEN
