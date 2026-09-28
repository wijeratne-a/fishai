"""SYNTHETIC delta-gamma barrier timing benchmark tests."""

from __future__ import annotations

import json
from pathlib import Path

from fishai.offload_sdmtmb.synthetic_barrier_timing import (
    SYNTHETIC_BARRIER_TIMING_BASENAME,
    run_synthetic_barrier_delta_gamma_timing_benchmark,
)


def test_synthetic_barrier_timing_writes_labeled_report(tmp_path: Path) -> None:
    payload = run_synthetic_barrier_delta_gamma_timing_benchmark(
        tmp_path,
        rscript="/nonexistent/Rscript",
        clock=lambda: 0.0,
    )
    report_path = tmp_path / f"{SYNTHETIC_BARRIER_TIMING_BASENAME}.json"
    assert report_path.is_file()
    assert "SYNTHETIC" in report_path.name
    assert payload["label"] == "SYNTHETIC"
    assert payload["benchmark"] == "delta_gamma_barrier_fit"
    on_disk = json.loads(report_path.read_text(encoding="utf-8"))
    assert on_disk["label"] == "SYNTHETIC"
