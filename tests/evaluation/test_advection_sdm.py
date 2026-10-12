"""Tests for advection–taxis grid operator."""

from __future__ import annotations

import numpy as np

from fishai.evaluation.advection_sdm import AdvectionGrid, advection_taxis_field, persistence_at_point


def test_persistence_matches_local_suitability() -> None:
    grid = AdvectionGrid(
        x_km=np.array([0.0, 10.0]),
        y_km=np.array([0.0, 10.0]),
        s=np.array([[0.2, 0.4], [0.6, 0.8]]),
        u_ms=np.zeros((2, 2)),
        v_ms=np.zeros((2, 2)),
    )
    assert persistence_at_point(grid, 0.0, 0.0) == 0.2
    assert persistence_at_point(grid, 10.0, 10.0) == 0.8


def test_advection_field_normalizes_to_one() -> None:
    grid = AdvectionGrid(
        x_km=np.linspace(0, 20, 5),
        y_km=np.linspace(0, 20, 5),
        s=np.full((5, 5), 0.5),
        u_ms=np.full((5, 5), 0.05),
        v_ms=np.zeros((5, 5)),
    )
    field = advection_taxis_field(grid, sigma_km=10.0, alpha=1.0)
    assert np.isclose(field.sum(), 1.0, atol=1e-6)
