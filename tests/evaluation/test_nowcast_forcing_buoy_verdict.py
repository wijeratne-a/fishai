"""Tests for NDBC buoy nowcast-forcing verdict evaluation."""

from __future__ import annotations

import dataclasses
import itertools
import re
from pathlib import Path

import yaml

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg
from fishai.evaluation.nowcast_forcing_buoy import (
    FAIL_HOLDOUT_REASON,
    BuoyGateThresholds,
    BuoyStratumMetrics,
    buoy_gate_thresholds_from_prereg,
    evaluate_buoy_stratum_verdict,
)

REPO = Path(__file__).resolve().parents[2]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"

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


def test_pearson_r_margin_yaml_has_single_numeric_key_and_loads_threshold() -> None:
    doc = load_harmonization_prereg(PREREG)
    raw_yaml = PREREG.read_text(encoding="utf-8")
    assert "pass_min_vs_glorys_r" not in raw_yaml
    pearson = doc["harmonization_wcofs_glorys"]["nowcast_forcing_grading"]["buoy_gate"]["pearson_r"]
    assert set(pearson.keys()) == {"max_deficit_vs_glorys_r", "degraded_band"}
    thresholds = buoy_gate_thresholds_from_prereg(doc)
    assert thresholds.pearson_r_max_deficit_vs_glorys == 0.10


def test_pearson_r_max_deficit_from_yaml_changes_verdict(tmp_path: Path) -> None:
    doc = yaml.safe_load(yaml.dump(load_harmonization_prereg(PREREG)))
    base_path = tmp_path / "prereg_base.yaml"
    base_path.write_text(yaml.dump(doc), encoding="utf-8")
    base_loaded = load_harmonization_prereg(base_path)
    metrics = BuoyStratumMetrics(
        rmse_ratio=1.0,
        rmse_ratio_bootstrap_upper_95=1.2,
        absolute_bias_c=0.2,
        pearson_r=0.78,
        glorys_pearson_r=0.85,
    )
    assert (
        evaluate_buoy_stratum_verdict(metrics, doc=base_loaded).verdict == "PASS"
    )
    tight = yaml.safe_load(yaml.dump(doc))
    tight["harmonization_wcofs_glorys"]["nowcast_forcing_grading"]["buoy_gate"]["pearson_r"][
        "max_deficit_vs_glorys_r"
    ] = 0.05
    tight_path = tmp_path / "prereg_tight.yaml"
    tight_path.write_text(yaml.dump(tight), encoding="utf-8")
    tight_loaded = load_harmonization_prereg(tight_path)
    result = evaluate_buoy_stratum_verdict(metrics, doc=tight_loaded)
    assert result.verdict == "UNKNOWN"
    assert result.reason == FAIL_HOLDOUT_REASON


def test_buoy_evaluator_has_no_hardcoded_numeric_cutoff_literals() -> None:
    module_path = REPO / "src" / "fishai" / "evaluation" / "nowcast_forcing_buoy.py"
    source = module_path.read_text(encoding="utf-8")
    for field in dataclasses.fields(BuoyGateThresholds):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
    numeric_field_defaults = re.findall(
        r"^\s+(?:rmse_ratio|absolute_bias|pearson_r)[^\n]*=\s*[\d.]+",
        source,
        flags=re.MULTILINE,
    )
    assert numeric_field_defaults == []
    thresholds = buoy_gate_thresholds_from_prereg()
    assert thresholds.pearson_r_max_deficit_vs_glorys == float(
        load_harmonization_prereg(PREREG)["harmonization_wcofs_glorys"][
            "nowcast_forcing_grading"
        ]["buoy_gate"]["pearson_r"]["max_deficit_vs_glorys_r"]
    )


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
