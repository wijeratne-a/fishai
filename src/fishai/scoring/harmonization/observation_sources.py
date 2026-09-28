"""
Holdout observation sources (pairing layer).

Each in-situ source maps to one ``assimilated_sources.yaml`` registry entry.
New sources (e.g. Spray glider profiles gridded by depth) add a row here and a
registry block — no scorer restructure required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PairingKind = Literal["point_daily_mean", "profile_gridded_by_depth"]


@dataclass(frozen=True)
class HoldoutObservationSource:
    source_id: str
    registry_id: str
    pairing_kind: PairingKind
    enabled_for_holdout_validation: bool
    display_name: str


# Canonical holdout validation sources (enabled subset drives preflight + buoy grading).
HOLDOUT_OBSERVATION_SOURCES: tuple[HoldoutObservationSource, ...] = (
    HoldoutObservationSource(
        source_id="ndbc_buoy_temperature",
        registry_id="ndbc_buoy_temperature",
        pairing_kind="point_daily_mean",
        enabled_for_holdout_validation=True,
        display_name="NDBC buoy temperature",
    ),
    HoldoutObservationSource(
        source_id="spray_glider_profiles",
        registry_id="spray_glider_profiles",
        pairing_kind="profile_gridded_by_depth",
        enabled_for_holdout_validation=False,
        display_name="Spray glider profiles (depth-gridded)",
    ),
)


def holdout_validation_registry_ids() -> tuple[str, ...]:
    return tuple(
        s.registry_id for s in HOLDOUT_OBSERVATION_SOURCES if s.enabled_for_holdout_validation
    )


def observation_source_by_registry_id(registry_id: str) -> HoldoutObservationSource | None:
    for src in HOLDOUT_OBSERVATION_SOURCES:
        if src.registry_id == registry_id:
            return src
    return None


def primary_buoy_validation_registry_id() -> str:
    """Registry id used for sea-surface temperature buoy grading today."""
    ids = holdout_validation_registry_ids()
    if not ids:
        raise RuntimeError("no holdout validation observation sources enabled")
    return ids[0]
