"""NDBC buoy nowcast-forcing gate verdicts (prereg harmonization_wcofs_glorys)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg

NowcastForcingVerdict = Literal["PASS", "DEGRADED", "UNKNOWN"]
FAIL_HOLDOUT_REASON = "nowcast_forcing_failed_holdout"


class _MetricBand(Enum):
    PASS = "PASS"
    DEGRADED = "DEGRADED"
    FAIL = "FAIL"


@dataclass(frozen=True)
class BuoyGateThresholds:
    rmse_ratio_pass_max: float = 1.2
    rmse_ratio_bootstrap_upper_95_pass_max: float = 1.5
    rmse_ratio_degraded_min_exclusive: float = 1.2
    rmse_ratio_degraded_max_inclusive: float = 1.5
    absolute_bias_pass_max_c: float = 0.5
    absolute_bias_degraded_min_exclusive_c: float = 0.5
    absolute_bias_degraded_max_inclusive_c: float = 1.0
    pearson_r_max_deficit_vs_glorys: float = 0.10
    fail_verdict: NowcastForcingVerdict = "UNKNOWN"
    fail_reason: str = FAIL_HOLDOUT_REASON


@dataclass(frozen=True)
class BuoyStratumMetrics:
    rmse_ratio: float
    rmse_ratio_bootstrap_upper_95: float
    absolute_bias_c: float
    pearson_r: float
    glorys_pearson_r: float


@dataclass(frozen=True)
class BuoyStratumVerdictResult:
    verdict: NowcastForcingVerdict
    reason: str | None = None


def buoy_gate_thresholds_from_prereg(doc: dict[str, Any] | None = None) -> BuoyGateThresholds:
    """Load numeric buoy gate cutoffs from ``prereg/harmonization_wcofs_glorys.yaml``."""
    raw = doc if doc is not None else load_harmonization_prereg()
    gate = raw["harmonization_wcofs_glorys"]["nowcast_forcing_grading"]["buoy_gate"]
    rmse = gate["rmse_ratio_to_glorys"]
    bias = gate["absolute_bias_C"]
    fail = gate["fail_outcome"]
    return BuoyGateThresholds(
        rmse_ratio_pass_max=float(rmse["pass"]["ratio_max"]),
        rmse_ratio_bootstrap_upper_95_pass_max=float(rmse["pass"]["bootstrap_upper_95_max"]),
        rmse_ratio_degraded_min_exclusive=float(rmse["degraded"]["ratio_min_exclusive"]),
        rmse_ratio_degraded_max_inclusive=float(rmse["degraded"]["ratio_max_inclusive"]),
        absolute_bias_pass_max_c=float(bias["pass_max"]),
        absolute_bias_degraded_min_exclusive_c=float(bias["degraded_min_exclusive"]),
        absolute_bias_degraded_max_inclusive_c=float(bias["degraded_max_inclusive"]),
        fail_verdict=str(fail["verdict"]),
        fail_reason=str(fail["reason"]),
    )


def _classify_rmse_ratio(
    metrics: BuoyStratumMetrics,
    thresholds: BuoyGateThresholds,
) -> _MetricBand:
    ratio = metrics.rmse_ratio
    upper = metrics.rmse_ratio_bootstrap_upper_95
    if ratio <= thresholds.rmse_ratio_pass_max and upper <= thresholds.rmse_ratio_bootstrap_upper_95_pass_max:
        return _MetricBand.PASS
    if (
        thresholds.rmse_ratio_degraded_min_exclusive < ratio <= thresholds.rmse_ratio_degraded_max_inclusive
    ):
        return _MetricBand.DEGRADED
    return _MetricBand.FAIL


def _classify_absolute_bias(metrics: BuoyStratumMetrics, thresholds: BuoyGateThresholds) -> _MetricBand:
    bias = abs(metrics.absolute_bias_c)
    if bias <= thresholds.absolute_bias_pass_max_c:
        return _MetricBand.PASS
    if (
        thresholds.absolute_bias_degraded_min_exclusive_c
        < bias
        <= thresholds.absolute_bias_degraded_max_inclusive_c
    ):
        return _MetricBand.DEGRADED
    return _MetricBand.FAIL


def _classify_pearson_r(metrics: BuoyStratumMetrics, thresholds: BuoyGateThresholds) -> _MetricBand:
    if metrics.pearson_r >= metrics.glorys_pearson_r - thresholds.pearson_r_max_deficit_vs_glorys:
        return _MetricBand.PASS
    return _MetricBand.FAIL


def _aggregate_metric_bands(bands: tuple[_MetricBand, ...], thresholds: BuoyGateThresholds) -> BuoyStratumVerdictResult:
    """Worst metric band wins; FAIL bands use the prereg catch-all UNKNOWN outcome."""
    if _MetricBand.FAIL in bands:
        return BuoyStratumVerdictResult(
            verdict=thresholds.fail_verdict,
            reason=thresholds.fail_reason,
        )
    if _MetricBand.DEGRADED in bands:
        return BuoyStratumVerdictResult(verdict="DEGRADED")
    return BuoyStratumVerdictResult(verdict="PASS")


def evaluate_buoy_stratum_verdict(
    metrics: BuoyStratumMetrics,
    *,
    thresholds: BuoyGateThresholds | None = None,
    doc: dict[str, Any] | None = None,
) -> BuoyStratumVerdictResult:
    """
    Classify one buoy stratum (pooled / nearshore / offshore) for nowcast forcing.

    Any metric that fails PASS and does not fall in a defined DEGRADED band is a FAIL
    band internally and resolves to UNKNOWN with ``nowcast_forcing_failed_holdout``.
    """
    t = thresholds if thresholds is not None else buoy_gate_thresholds_from_prereg(doc)
    bands = (
        _classify_rmse_ratio(metrics, t),
        _classify_absolute_bias(metrics, t),
        _classify_pearson_r(metrics, t),
    )
    return _aggregate_metric_bands(bands, t)
