"""SYNTHETIC timing benchmark for delta-gamma sdmTMB barrier fits (report-only)."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
R_BENCHMARK_SCRIPT = (
    REPO_ROOT / "src" / "models" / "offload_sdmtmb" / "SYNTHETIC_barrier_delta_gamma_timing.R"
)
SYNTHETIC_BARRIER_TIMING_BASENAME = "SYNTHETIC_sdmtmb_barrier_delta_gamma_timing"


def run_synthetic_barrier_delta_gamma_timing_benchmark(
    output_dir: Path | str,
    *,
    rscript: str | None = None,
    clock: Callable[[], float] | None = None,
) -> dict[str, Any]:
    """
    Run the SYNTHETIC barrier delta-gamma timing benchmark.

    Writes ``SYNTHETIC_sdmtmb_barrier_delta_gamma_timing.json`` under ``output_dir``.
    When R/sdmTMB is unavailable, records ``status: skipped`` without failing.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / f"{SYNTHETIC_BARRIER_TIMING_BASENAME}.json"
    tick = clock or time.perf_counter
    t0 = tick()
    rscript_bin = rscript or shutil.which("Rscript")
    payload: dict[str, Any] = {
        "label": "SYNTHETIC",
        "benchmark": "delta_gamma_barrier_fit",
        "report_path": str(report_path),
        "status": "skipped",
        "reason": None,
        "timings_sec": {},
        "wall_sec": None,
    }
    if rscript_bin is None or not R_BENCHMARK_SCRIPT.is_file():
        payload["reason"] = "Rscript or SYNTHETIC R benchmark script unavailable"
        payload["wall_sec"] = tick() - t0
        report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload
    try:
        proc = subprocess.run(
            [rscript_bin, str(R_BENCHMARK_SCRIPT), str(report_path)],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        payload["reason"] = str(exc)
        payload["wall_sec"] = tick() - t0
        report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload
    if proc.returncode != 0:
        payload["reason"] = (proc.stderr or proc.stdout or "Rscript failed").strip()[:500]
        payload["wall_sec"] = tick() - t0
        report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload
    if report_path.is_file():
        loaded = json.loads(report_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            loaded.setdefault("label", "SYNTHETIC")
            payload = loaded
    payload["wall_sec"] = tick() - t0
    if "SYNTHETIC" not in report_path.name:
        raise ValueError("benchmark report path must include SYNTHETIC in the filename")
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
