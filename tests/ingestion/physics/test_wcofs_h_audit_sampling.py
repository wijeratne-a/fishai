"""Audit-only WCOFS ``h`` sampling at nearest wet coarsened cell."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.bathymetry import sample_wcofs_h_audit_m


def test_audit_h_ignores_min_wet_fraction_at_nearest_cell() -> None:
    lat = np.array([33.0, 33.1])
    lon = np.array([-120.0, -119.9])
    h_m = np.array([[50.0, 200.0], [80.0, 300.0]])
    has_source = np.ones_like(h_m, dtype=bool)
    wet_fraction = np.array([[0.2, 0.9], [0.9, 0.9]])
    val = sample_wcofs_h_audit_m(
        33.0,
        -120.0,
        h_m,
        lat,
        lon,
        has_source=has_source,
        wet_fraction=wet_fraction,
    )
    assert val == 50.0


def test_audit_h_searches_outward_for_nearest_wet_cell() -> None:
    lat = np.array([33.0, 33.1])
    lon = np.array([-120.0, -119.9])
    h_m = np.array([[np.nan, 120.0], [np.nan, 400.0]])
    has_source = np.array([[True, True], [True, True]])
    wet_fraction = np.array([[0.0, 0.6], [0.0, 0.8]])
    val = sample_wcofs_h_audit_m(
        33.0,
        -120.0,
        h_m,
        lat,
        lon,
        has_source=has_source,
        wet_fraction=wet_fraction,
    )
    assert val == 120.0
