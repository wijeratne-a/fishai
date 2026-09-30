"""Longitude convention for GLORYS-grid sampling."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.bathymetry import nearest_glorys_cell_indices, normalize_lon_for_axis


def test_normalize_lon_for_0_360_grid() -> None:
    lon_axis = np.array([0.0, 60.0, 120.0, 180.0, 240.0, 300.0])
    assert normalize_lon_for_axis(-120.0, lon_axis) == 240.0


def test_nearest_cell_on_0_360_grid() -> None:
    lat_axis = np.linspace(33.0, 34.0, 5)
    lon_axis = np.linspace(0.0, 360.0, 13)
    j_neg, i_neg = nearest_glorys_cell_indices(33.5, -120.0, lat_axis, lon_axis)
    j_pos, i_pos = nearest_glorys_cell_indices(33.5, 240.0, lat_axis, lon_axis)
    assert j_neg == j_pos
    assert i_neg == i_pos
