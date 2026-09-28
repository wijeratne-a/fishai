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

    cv = sub.add_parser("cv", help="Spatial-block and LFO cross-validation")
    cv.add_argument("--config", default=str(DEFAULT_SARDINE))

    predict = sub.add_parser("predict", help="Predict egg encounter surfaces")
    predict.add_argument("--config", default=str(DEFAULT_SARDINE))
    predict.add_argument(
        "--artifact",
        default=str(REPO_ROOT / "artifacts/models/sardine/fit.rds"),
        help="Frozen/fit RDS artifact",
    )

    ns = parser.parse_args(argv)
    if ns.command == "train":
        return _run_r("train.R", [ns.config])
    if ns.command == "cv":
        return _run_r("cv.R", [ns.config])
    if ns.command == "predict":
        return _run_r("predict.R", [ns.config, ns.artifact])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
