"""Pilot CUFES model YAML invariants (configs/models/*.yaml)."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_CONFIG_DIR = REPO_ROOT / "configs" / "models"


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
        self.assertEqual(failures, [], "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
