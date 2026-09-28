"""SYNTHETIC delta-gamma barrier timing benchmark tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fishai.offload_sdmtmb.synthetic_barrier_timing import (
    SYNTHETIC_BARRIER_TIMING_BASENAME,
    ZERO_BARRIER_TRIANGLES_REASON,
    run_synthetic_barrier_delta_gamma_timing_benchmark,
    validate_synthetic_barrier_benchmark_report,
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


def test_zero_barrier_triangle_guard_accepts_mock_error_report() -> None:
    mock = {
        "label": "SYNTHETIC",
        "benchmark": "delta_gamma_barrier_fit",
        "status": "error",
        "reason": ZERO_BARRIER_TRIANGLES_REASON,
        "barrier_triangle_count": 0,
    }
    validate_synthetic_barrier_benchmark_report(mock)


def test_zero_barrier_triangle_guard_rejects_ok_with_zero_count() -> None:
    mock = {
        "label": "SYNTHETIC",
        "status": "ok",
        "barrier_triangle_count": 0,
    }
    with pytest.raises(ValueError, match="status error"):
        validate_synthetic_barrier_benchmark_report(mock)
