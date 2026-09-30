"""Regression tests for GLORYS shallow-first depth ordering in ``glorys_column_features`` (b394309)."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.sources.glorys import glorys_column_features
from fishai.ingestion.physics.vertical import mld

# Fixed physical column (surface warm, cold deep) used in both native depth orderings.
KNOWN_Z_LEVELS_DEEP_FIRST_M = np.array([50.0, 20.0, 10.0, 5.0, 0.0])
KNOWN_TEMP_C = np.array([10.0, 15.0, 17.8, 17.9, 18.0])
KNOWN_SAL_PSU = np.full_like(KNOWN_TEMP_C, 33.5)
KNOWN_Z_LEVELS_SHALLOW_FIRST_M = KNOWN_Z_LEVELS_DEEP_FIRST_M[::-1]
KNOWN_TEMP_SHALLOW_FIRST_C = KNOWN_TEMP_C[::-1]
KNOWN_SAL_SHALLOW_FIRST_PSU = KNOWN_SAL_PSU[::-1]


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
) -> float:
    """Reproduce pre-b394309 behavior (no depth reorder before ``mld``)."""
    z = -np.asarray(z_levels_shallow_first, dtype=float)
    temp = np.asarray(temp, dtype=float)
    z3d = z[:, None, None]
    t3d = temp[:, None, None]
    return float(mld(z3d, t3d)[0, 0])


def test_glorys_mld_shallow_first_matches_deep_first_reference() -> None:
    expected = _reference_mld_deep_first_z_levels(KNOWN_Z_LEVELS_DEEP_FIRST_M, KNOWN_TEMP_C)
    assert np.isfinite(expected)

    feats = glorys_column_features(
        KNOWN_Z_LEVELS_SHALLOW_FIRST_M,
        KNOWN_TEMP_SHALLOW_FIRST_C,
        KNOWN_SAL_SHALLOW_FIRST_PSU,
        mlotst_native=12.0,
    )
    assert np.isfinite(feats["MLD_m"])
    assert abs(feats["MLD_m"] - expected) < 1e-6


def test_glorys_mld_shallow_first_without_reorder_is_nan() -> None:
    pre_fix = _glorys_mld_pre_fix_shallow_first(
        KNOWN_Z_LEVELS_SHALLOW_FIRST_M,
        KNOWN_TEMP_SHALLOW_FIRST_C,
    )
    assert np.isnan(pre_fix)
    post_fix = glorys_column_features(
        KNOWN_Z_LEVELS_SHALLOW_FIRST_M,
        KNOWN_TEMP_SHALLOW_FIRST_C,
        KNOWN_SAL_SHALLOW_FIRST_PSU,
        mlotst_native=12.0,
    )["MLD_m"]
    assert np.isfinite(post_fix)
    expected = _reference_mld_deep_first_z_levels(KNOWN_Z_LEVELS_DEEP_FIRST_M, KNOWN_TEMP_C)
    assert abs(post_fix - expected) < 1e-6
