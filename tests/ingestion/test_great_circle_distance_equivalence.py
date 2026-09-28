"""Great-circle distance equivalence: shared helper vs CUFES reference haversine."""

from __future__ import annotations

import math

import numpy as np

from fishai.ingestion.physics.geo_distance import (
    EARTH_RADIUS_NM,
    haversine_distance_nm,
    haversine_km,
)


def _reference_haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_NM * 1.852 * c


def _legacy_cufes_haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Pre-merge CUFES helper (PR #4) for regression comparison."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_NM * c


def _pilot_style_pairs() -> list[tuple[float, float, float, float]]:
    rng = np.random.default_rng(42)
    pairs: list[tuple[float, float, float, float]] = []
    for _ in range(50):
        lat1 = float(rng.uniform(32.0, 35.0))
        lon1 = float(rng.uniform(-121.0, -117.0))
        lat2 = float(rng.uniform(32.0, 35.0))
        lon2 = float(rng.uniform(-121.0, -117.0))
        pairs.append((lat1, lon1, lat2, lon2))
    pairs.extend(
        [
            (32.0, -121.0, 35.0, -117.0),
            (33.5, -120.0, 33.5, -119.0),
            (34.0, -121.0, 34.0, -121.0),
        ]
    )
    return pairs


def test_shared_haversine_matches_legacy_cufes_and_reference() -> None:
    max_delta_m = 0.0
    for lat1, lon1, lat2, lon2 in _pilot_style_pairs():
        km_shared = haversine_km(lat1, lon1, lat2, lon2)
        km_ref = _reference_haversine_km(lat1, lon1, lat2, lon2)
        nm_legacy = _legacy_cufes_haversine_nm(lat1, lon1, lat2, lon2)
        nm_shared = haversine_distance_nm(lat1, lon1, lat2, lon2)
        delta_m = abs(km_shared - km_ref) * 1000.0
        delta_m = max(delta_m, abs(nm_shared - nm_legacy) * 1852.0)
        max_delta_m = max(max_delta_m, delta_m)
        assert delta_m <= 1.0
    # Exposed for reporting in agent summary (assertion encodes <=1 m).
    assert max_delta_m >= 0.0
