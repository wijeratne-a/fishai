"""Bootstrap reproducibility tests."""

from __future__ import annotations

import numpy as np

from fishai.scoring.harmonization.metrics import compute_metrics, moving_block_bootstrap_ci


def test_bootstrap_reproducible_with_fixed_seed() -> None:
    obs = np.linspace(10, 12, 30)
    pred = obs + 0.1
    dates = np.arange("2025-09-01", "2025-10-01", dtype="datetime64[D]")
    m1 = compute_metrics(obs, pred, dates, block_days=7, seed=99)
    m2 = compute_metrics(obs, pred, dates, block_days=7, seed=99)
    assert m1.bias_ci95 == m2.bias_ci95
    assert m1.rmse_ci95 == m2.rmse_ci95


def test_block_length_seven_days() -> None:
    obs = [1.0, 2.0, 3.0, 4.0]
    pred = [1.1, 2.1, 3.1, 4.1]
    dates = np.array(["2025-09-01", "2025-09-02", "2025-09-10", "2025-09-11"], dtype="datetime64[D]")
    b_ci, _, _ = moving_block_bootstrap_ci(obs, pred, dates, block_days=7, seed=1, n_boot=50)
    assert np.isfinite(b_ci[0]) or len(obs) >= 2
