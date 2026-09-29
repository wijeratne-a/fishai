"""Holdout grading must load thresholds from prereg, not literals in grading.py."""

from __future__ import annotations

import re
from pathlib import Path

GRADING_PY = (
    Path(__file__).resolve().parents[3] / "src" / "fishai" / "scoring" / "harmonization" / "grading.py"
)


def test_grading_module_has_no_hardcoded_numeric_cutoffs() -> None:
    source = GRADING_PY.read_text(encoding="utf-8")
    cutoff_key_literals = re.findall(
        r'"(?:rmse_ratio|bias_abs|pearson_r|input_rmse|glider_|min_matched|min_buoys)[^"]*":\s*([\d.]+)',
        source,
    )
    assert cutoff_key_literals == []
    assert "bootstrap_seed" not in source
    assert re.search(r":\s*42(?:\.0)?\b", source) is None
