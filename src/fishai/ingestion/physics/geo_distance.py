"""Shared great-circle distance (WGS84) for physics and CUFES track metrics."""

from __future__ import annotations

import math

# Match CalCOFI CUFES implied-speed convention (nautical miles on WGS84 sphere).
EARTH_RADIUS_NM = 3440.065
KM_PER_NM = 1.852
EARTH_RADIUS_KM = EARTH_RADIUS_NM * KM_PER_NM


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two WGS84 points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def haversine_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in nautical miles (CUFES reporting)."""
    return haversine_km(lat1, lon1, lat2, lon2) / KM_PER_NM
