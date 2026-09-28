"""Tests for preferential-sampling diagnostic (report-only)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from fishai.offload_sdmtmb.preferential_sampling_diagnostic import (
    compute_preferential_sampling_report,
)

REPO = Path(__file__).resolve().parents[2]
CLI = REPO / "scripts" / "offload_sdmtmb" / "preferential_sampling_diagnostic.py"


def test_preferential_sampling_report_detects_high_bias(tmp_path: Path) -> None:
    grid = np.linspace(-2.0, 2.0, 200)
    sampled = np.linspace(1.0, 2.0, 30)
    report = compute_preferential_sampling_report(sampled, grid)
    assert report.mean_covariate_sampled > report.mean_covariate_grid
    assert report.sampled_to_grid_mean_ratio > 1.0
    out = tmp_path / "preferential_sampling_report.json"
    out.write_text(json.dumps(report.to_dict()), encoding="utf-8")
    assert "report_only" in out.read_text(encoding="utf-8")


def test_preferential_sampling_cli_writes_json(tmp_path: Path) -> None:
    out = tmp_path / "diag.json"
    proc = subprocess.run(
        [sys.executable, str(CLI), "--output", str(out), "--seed", "1"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["label"] == "preferential_sampling_diagnostic_report_only"
