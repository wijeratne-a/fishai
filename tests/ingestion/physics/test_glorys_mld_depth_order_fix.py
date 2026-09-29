"""Regression tests for GLORYS shallow-first depth ordering in ``glorys_column_features`` (b394309)."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.sources.glorys import glorys_column_features
from fishai.ingestion.physics.vertical import mld


def _reference_mld_deep_first_z_levels(
    z_levels_positive_down: np.ndarray,
    temp: np.ndarray,
) -> float:
    """Reference MLD using deep-first positive depths (legacy test convention)."""
    z = -np.asarray(z_levels_positive_down, dtype=float)
    temp = np.asarray(temp, dtype=float)
    z3d = z[:, None, None]
    t3d = temp[:, None, None]
    return float(mld(z3d, t3d)[0, 0])


def _glorys_mld_pre_fix_shallow_first(
    z_levels_shallow_first: np.ndarray,
    temp: np.ndarray,
    salt: np.ndarray,
) -> float:
    """Reproduce pre-b394309 behavior (no depth reorder before ``mld``)."""
    z = -np.asarray(z_levels_shallow_first, dtype=float)
    temp = np.asarray(temp, dtype=float)
    z3d = z[:, None, None]
    t3d = temp[:, None, None]
    return float(mld(z3d, t3d)[0, 0])


def test_glorys_mld_shallow_first_matches_deep_first_reference() -> None:
    # Same physical column: surface warm, cold deep. Deep-first levels (existing compliance test).
    z_deep = np.array([50.0, 20.0, 10.0, 5.0, 0.0])
    temp = np.array([10.0, 15.0, 17.8, 17.9, 18.0])
    salt = np.full_like(temp, 33.5)
    expected = _reference_mld_deep_first_z_levels(z_deep, temp)
    assert np.isfinite(expected)

    # GLORYS native shallow-first ordering (ascending depth, surface at index 0).
    z_shallow = z_deep[::-1]
    temp_shallow = temp[::-1]
    feats = glorys_column_features(z_shallow, temp_shallow, salt[::-1], mlotst_native=12.0)
    assert np.isfinite(feats["MLD_m"])
    assert abs(feats["MLD_m"] - expected) < 1e-6


def test_glorys_mld_shallow_first_without_reorder_is_nan() -> None:
    z_shallow = np.array([0.0, 5.0, 10.0, 20.0, 50.0])
    temp = np.array([18.0, 17.9, 17.8, 15.0, 10.0])
    salt = np.full_like(temp, 33.5)
    pre_fix = _glorys_mld_pre_fix_shallow_first(z_shallow, temp, salt)
    assert np.isnan(pre_fix)
    post_fix = glorys_column_features(z_shallow, temp, salt, mlotst_native=12.0)["MLD_m"]
    assert np.isfinite(post_fix)
