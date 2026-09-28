"""Per-cell forcing_verdict for harmonization holdout map layer."""

from __future__ import annotations

import pandas as pd

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg
from fishai.scoring.harmonization.constants import FAIL_EVIDENCE_REASON, VERDICT_PASS
from fishai.scoring.harmonization.grading import cutoffs_from_prereg
from fishai.scoring.harmonization.input_cell_check import (
    build_input_cell_check_summary,
    forcing_verdict_for_cell,
)

PREREG = (
    __import__("pathlib").Path(__file__).resolve().parents[3] / "prereg" / "harmonization_wcofs_glorys.yaml"
)


def test_forcing_verdict_fail_maps_to_unknown_holdout() -> None:
    fv, ur = forcing_verdict_for_cell("FAIL")
    assert fv == "UNKNOWN"
    assert ur == FAIL_EVIDENCE_REASON


def test_graded_input_fail_cell_emits_forcing_verdict() -> None:
    doc = load_harmonization_prereg(PREREG)
    cutoffs = cutoffs_from_prereg(doc)
    table = pd.DataFrame(
        [
            {
                "stratum": "pooled",
                "variable": "T3m",
                "rmse": 2.0,
                "glorys_spatial_sd": 1.0,
            }
        ]
    )
    _, rows = build_input_cell_check_summary(
        doc, table, "pooled", cutoffs, forecast_group="nowcast"
    )
    t3m = next(r for r in rows if r["variable"] == "T3m")
    assert t3m["verdict"] == "FAIL"
    assert t3m["forcing_verdict"] == "UNKNOWN"
    assert t3m["unknown_reason"] == FAIL_EVIDENCE_REASON
    assert t3m["forecast_group"] == "nowcast"


def test_graded_input_pass_cell_forcing_verdict_pass() -> None:
    doc = load_harmonization_prereg(PREREG)
    cutoffs = cutoffs_from_prereg(doc)
    table = pd.DataFrame(
        [
            {
                "stratum": "offshore",
                "variable": "S3m",
                "rmse": 0.2,
                "glorys_spatial_sd": 1.0,
            }
        ]
    )
    _, rows = build_input_cell_check_summary(doc, table, "offshore", cutoffs)
    s3m = next(r for r in rows if r["variable"] == "S3m")
    assert s3m["forcing_verdict"] == VERDICT_PASS
    assert s3m["unknown_reason"] is None
    assert s3m["verdict"] == VERDICT_PASS
