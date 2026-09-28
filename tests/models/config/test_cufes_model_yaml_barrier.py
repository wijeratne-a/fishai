"""Pilot CUFES model YAML invariants (configs/models/*.yaml)."""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_CONFIG_DIR = REPO_ROOT / "configs" / "models"
PR7_SHORELINE_REL = Path("data/reference/shoreline/ne_10m_land_pilot_clip.json")
SHORELINE_SHA256_PLACEHOLDER = "TO_BE_SET_FROM_PR7"


class CufesModelYamlBarrierTests(unittest.TestCase):
    def test_all_model_yamls_enable_barrier_mesh(self) -> None:
        paths = sorted(MODEL_CONFIG_DIR.glob("*.yaml"))
        self.assertGreater(len(paths), 0, "expected configs/models/*.yaml")
        failures: list[str] = []
        for path in paths:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            cfg = raw.get("fishai_engine_config") or raw
            barrier = (cfg.get("mesh") or {}).get("barrier")
            if not isinstance(barrier, dict):
                failures.append(f"{path.name}: mesh.barrier missing")
                continue
            if barrier.get("enabled") is not True:
                failures.append(f"{path.name}: mesh.barrier.enabled is not true")
            rf = barrier.get("range_fraction")
            if rf is None:
                failures.append(f"{path.name}: mesh.barrier.range_fraction missing")
            elif float(rf) != 0.1:
                failures.append(f"{path.name}: mesh.barrier.range_fraction must be 0.1")
            shoreline = barrier.get("shoreline")
            if not isinstance(shoreline, dict):
                failures.append(f"{path.name}: mesh.barrier.shoreline missing")
                continue
            rel_path = shoreline.get("path")
            if rel_path != str(PR7_SHORELINE_REL):
                failures.append(
                    f"{path.name}: mesh.barrier.shoreline.path must be {PR7_SHORELINE_REL}"
                )
            sha = shoreline.get("sha256")
            if not sha or not str(sha).strip():
                failures.append(f"{path.name}: mesh.barrier.shoreline.sha256 must be set")
            elif str(sha).strip() != SHORELINE_SHA256_PLACEHOLDER:
                failures.append(
                    f"{path.name}: expected placeholder sha256 until PR #7 posts final hash"
                )
        self.assertEqual(failures, [], "\n".join(failures))


@pytest.mark.xfail(
    reason="barrier shoreline sha256 still placeholder until PR #7 final hash is posted",
    strict=True,
)
def test_frozen_shoreline_bytes_match_pinned_sha256() -> None:
    """Passes once mesh.barrier.shoreline.sha256 is filled and the PR #7 file is present."""
    path = REPO_ROOT / PR7_SHORELINE_REL
    if not path.is_file():
        pytest.fail(f"missing frozen shoreline artifact: {path}")

    cfg_path = MODEL_CONFIG_DIR / "cufes_sardine.yaml"
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg = raw.get("fishai_engine_config") or raw
    expected = (
        (cfg.get("mesh") or {})
        .get("barrier", {})
        .get("shoreline", {})
        .get("sha256")
    )
    assert expected and str(expected).strip() not in ("", SHORELINE_SHA256_PLACEHOLDER)

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == str(expected).strip().lower()


if __name__ == "__main__":
    unittest.main()
