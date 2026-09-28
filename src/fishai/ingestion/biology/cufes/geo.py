"""Great-circle distance helpers for CUFES track metrics."""

from __future__ import annotations

from fishai.ingestion.physics.geo_distance import haversine_distance_nm


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
