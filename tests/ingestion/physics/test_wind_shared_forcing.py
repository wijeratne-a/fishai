"""Auditor: shared_forcing wind product qualification (no network)."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.features import upwelling_covariate_metadata
from fishai.ingestion.physics.sources.winds import fetch_winds_for_day
from fishai.ingestion.physics.wind_shared_forcing import (
    CUFES_TRAINING_MID_TIME_MIN,
    UPWELLING_SHARED_FORCING_QUALIFIED,
    require_day_within_ccmp_nrt,
    wind_product_audit_summary,
)


def test_cufes_training_span_precedes_ccmp_nrt() -> None:
    audit = wind_product_audit_summary()
    ncei = next(c for c in audit["candidates"] if c["dataset_id"] == "noaacwBlendedWindsDaily")
    ccmp = next(c for c in audit["candidates"] if c["dataset_id"] == "ccmp-daily-v2-1-NRT")
    assert CUFES_TRAINING_MID_TIME_MIN >= dt.date.fromisoformat(ncei["coverage_start"])
    assert CUFES_TRAINING_MID_TIME_MIN < dt.date.fromisoformat(ccmp["coverage_start"])
    assert not UPWELLING_SHARED_FORCING_QUALIFIED


def test_metadata_records_shared_forcing_false() -> None:
    meta = upwelling_covariate_metadata("ccmp_winds")
    assert meta["upwelling_shared_forcing"] is False
    assert meta["upwelling_wind_dataset_id"] == "ccmp-daily-v2-1-NRT"
    assert "upwelling_wind_audit" in meta


def test_training_fetch_rejects_pre_ccmp_day() -> None:
    with pytest.raises(ValueError, match="precedes"):
        require_day_within_ccmp_nrt(dt.date(2010, 1, 1))

    def get_fn(url: str, **kwargs: object) -> bytes:
        raise AssertionError("should not fetch")

    with pytest.raises(ValueError, match="precedes"):
        fetch_winds_for_day(
            dt.date(2010, 1, 1),
            (32.0, 35.0, -121.0, -117.0),
            purpose="training",
            get_fn=get_fn,
        )
