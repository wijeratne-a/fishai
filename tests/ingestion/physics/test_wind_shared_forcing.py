"""Training upwelling policy: no wind product wired in this PR (follow-up selects product)."""

from __future__ import annotations

from fishai.ingestion.physics.features import upwelling_covariate_metadata
from fishai.ingestion.physics.wind_shared_forcing import (
    UPWELLING_STATUS_NO_CONSISTENT_WIND,
    UPWELLING_WIND_FORCING_ENABLED,
)


def test_upwelling_wind_forcing_disabled_for_training() -> None:
    assert UPWELLING_WIND_FORCING_ENABLED is False
    assert UPWELLING_STATUS_NO_CONSISTENT_WIND == "no_consistent_wind_product"


def test_metadata_records_fallback_status() -> None:
    meta = upwelling_covariate_metadata("ccmp_winds")
    assert meta["upwelling_shared_forcing"] is False
    assert meta["upwelling_status"] == UPWELLING_STATUS_NO_CONSISTENT_WIND
