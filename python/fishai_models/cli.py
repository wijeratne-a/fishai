"""Thin Python CLI wrapping FishAI sdmTMB R entry points."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_DIR = REPO_ROOT / "src" / "models" / "inst" / "cli"
DEFAULT_SARDINE = REPO_ROOT / "configs" / "models" / "cufes_sardine.yaml"
DEFAULT_ANCHOVY = REPO_ROOT / "configs" / "models" / "cufes_anchovy.yaml"


def _run_r(script: str, args: list[str]) -> int:
    cmd = ["Rscript", str(CLI_DIR / script), *args]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    return int(proc.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-models", description="FishAI sdmTMB modeling CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    train = sub.add_parser("train", help="Fit delta sdmTMB model")
    train.add_argument(
        "--config",
        default=str(DEFAULT_SARDINE),
        help="YAML config (default: cufes_sardine.yaml)",
    )
    train.add_argument(
        "--min-duration-min",
        type=float,
        default=None,
        help="Optional sensitivity refit excluding events shorter than N minutes",
    )

    cv = sub.add_parser("cv", help="Spatial-block and LFO cross-validation")
    cv.add_argument("--config", default=str(DEFAULT_SARDINE))
    cv.add_argument(
        "--min-duration-min",
        type=float,
        default=None,
        help="Optional sensitivity refit excluding events shorter than N minutes",
    )

    predict = sub.add_parser("predict", help="Predict egg encounter surfaces")
    predict.add_argument("--config", default=str(DEFAULT_SARDINE))
    predict.add_argument(
        "--artifact",
        default=str(REPO_ROOT / "artifacts/models/sardine/fit.rds"),
        help="Frozen/fit RDS artifact",
    )

    sens = sub.add_parser(
        "sensitivity-short-samples",
        help="Run pre-registered short-sample duration refit pass/fail tests",
    )
    sens.add_argument(
        "--protocol",
        default=str(REPO_ROOT / "configs/sensitivity_short_samples.yaml"),
        help="Pre-registered sensitivity protocol YAML",
    )

    ns = parser.parse_args(argv)

    def _r_args(config: str, min_duration_min: float | None) -> list[str]:
        args = [config]
        if min_duration_min is not None:
            args.append(f"--min-duration-min={min_duration_min}")
        return args

    if ns.command == "train":
        return _run_r("train.R", _r_args(ns.config, ns.min_duration_min))
    if ns.command == "cv":
        return _run_r("cv.R", _r_args(ns.config, ns.min_duration_min))
    if ns.command == "predict":
        return _run_r("predict.R", [ns.config, ns.artifact])
    if ns.command == "sensitivity-short-samples":
        return _run_r("short_sample_sensitivity.R", [ns.protocol])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
