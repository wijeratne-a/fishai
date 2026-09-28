#!/usr/bin/env python3
"""CLI: preferential-sampling diagnostic (report-only)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fishai.offload_sdmtmb.preferential_sampling_diagnostic import (
    compute_preferential_sampling_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preferential sampling diagnostic (report-only).")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Write JSON report to this path (use a temp or artifacts path).",
    )
    parser.add_argument("--seed", type=int, default=0, help="RNG seed for demo synthetic arrays.")
    args = parser.parse_args(argv)
    rng = np.random.default_rng(args.seed)
    grid = rng.normal(0.0, 1.0, 500)
    # Preferential draw toward high covariate values (synthetic illustration only).
    weights = np.exp(grid)
    idx = rng.choice(grid.size, size=60, replace=False, p=weights / weights.sum())
    sampled = grid[idx]
    report = compute_preferential_sampling_report(sampled, grid)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
