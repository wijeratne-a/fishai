"""Offload diagnostics and benchmarks for the sdmTMB-core workstream (PR #5)."""

from fishai.offload_sdmtmb.preferential_sampling_diagnostic import (
    PreferentialSamplingReport,
    compute_preferential_sampling_report,
)
from fishai.offload_sdmtmb.synthetic_barrier_timing import (
    SYNTHETIC_BARRIER_TIMING_BASENAME,
    ZERO_BARRIER_TRIANGLES_REASON,
    run_synthetic_barrier_delta_gamma_timing_benchmark,
    validate_synthetic_barrier_benchmark_report,
)

__all__ = [
    "PreferentialSamplingReport",
    "SYNTHETIC_BARRIER_TIMING_BASENAME",
    "ZERO_BARRIER_TRIANGLES_REASON",
    "compute_preferential_sampling_report",
    "run_synthetic_barrier_delta_gamma_timing_benchmark",
    "validate_synthetic_barrier_benchmark_report",
]
