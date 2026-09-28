"""Great-circle distance helpers for CUFES track metrics."""

from __future__ import annotations

import math

# TODO: After rebasing onto PR #2, switch to the shared great-circle helper from that branch.

_EARTH_RADIUS_NM = 3440.065  # nautical miles


def haversine_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in nautical miles between two WGS84 points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return _EARTH_RADIUS_NM * c


def implied_speed_knots(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    duration_minutes: float,
) -> float | None:
    if duration_minutes <= 0:
        return None
    nm = haversine_distance_nm(lat1, lon1, lat2, lon2)
    hours = duration_minutes / 60.0
    return nm / hours
