"""Tests for NDBC buoy nowcast-forcing verdict evaluation."""

from __future__ import annotations

import itertools
from pathlib import Path

from fishai.evaluation.nowcast_forcing_buoy import (
    FAIL_HOLDOUT_REASON,
    BuoyStratumMetrics,
    evaluate_buoy_stratum_verdict,
)

VERDICTS = frozenset({"PASS", "DEGRADED", "UNKNOWN"})


def test_bootstrap_upper_above_pass_band_yields_unknown_holdout() -> None:
    result = evaluate_buoy_stratum_verdict(
        BuoyStratumMetrics(
            rmse_ratio=1.1,
            rmse_ratio_bootstrap_upper_95=1.51,
            absolute_bias_c=0.1,
            pearson_r=0.85,
            glorys_pearson_r=0.85,
        )
    )
    assert result.verdict == "UNKNOWN"
    assert result.reason == FAIL_HOLDOUT_REASON


def test_pearson_r_more_than_010_below_glorys_yields_unknown_holdout() -> None:
    result = evaluate_buoy_stratum_verdict(
        BuoyStratumMetrics(
            rmse_ratio=1.0,
            rmse_ratio_bootstrap_upper_95=1.2,
            absolute_bias_c=0.2,
            pearson_r=0.74,
            glorys_pearson_r=0.85,
        )
    )
    assert result.verdict == "UNKNOWN"
    assert result.reason == FAIL_HOLDOUT_REASON


def test_buoy_verdict_grid_is_exhaustive_without_exceptions(tmp_path: Path) -> None:
    assert tmp_path.is_dir()
    ratios = (0.8, 1.0, 1.2, 1.21, 1.5, 1.51, 2.0)
    uppers = (1.0, 1.5, 1.51, 2.0)
    biases = (0.0, 0.5, 0.51, 1.0, 1.01)
    glorys_r = 0.8
    pearson_rs = (0.8, 0.71, 0.69, 0.5)
    seen: set[tuple[str, str | None]] = set()
    for ratio, upper, bias, r in itertools.product(ratios, uppers, biases, pearson_rs):
        result = evaluate_buoy_stratum_verdict(
            BuoyStratumMetrics(
                rmse_ratio=ratio,
                rmse_ratio_bootstrap_upper_95=upper,
                absolute_bias_c=bias,
                pearson_r=r,
                glorys_pearson_r=glorys_r,
            )
        )
        assert result.verdict in VERDICTS
        if result.verdict == "UNKNOWN":
            assert result.reason == FAIL_HOLDOUT_REASON
        else:
            assert result.reason is None
        seen.add((result.verdict, result.reason))
    assert "PASS" in {v for v, _ in seen}
    assert "DEGRADED" in {v for v, _ in seen}
    assert "UNKNOWN" in {v for v, _ in seen}
