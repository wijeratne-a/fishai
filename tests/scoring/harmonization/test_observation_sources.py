"""Holdout observation source registry wiring."""

from __future__ import annotations

from fishai.scoring.harmonization.observation_sources import (
    holdout_validation_registry_ids,
    observation_source_by_registry_id,
)


def test_spray_glider_source_reserved_not_enabled() -> None:
    glider = observation_source_by_registry_id("spray_glider_profiles")
    assert glider is not None
    assert glider.pairing_kind == "profile_gridded_by_depth"
    assert glider.enabled_for_holdout_validation is False
    assert "spray_glider_profiles" not in holdout_validation_registry_ids()
