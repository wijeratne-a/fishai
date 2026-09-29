"""Pilot production CUFES model YAMLs drop upwelling (prereg amendment path B)."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_CONFIG_DIR = REPO_ROOT / "configs" / "models"
AMENDMENT = REPO_ROOT / "prereg" / "pilot_model_upwelling_amendment.md"
PRODUCTION_YAMLS = ("cufes_sardine.yaml", "cufes_anchovy.yaml")


def _load(name: str) -> dict:
    raw = yaml.safe_load((MODEL_CONFIG_DIR / name).read_text(encoding="utf-8"))
    return raw.get("fishai_engine_config") or raw


class CufesModelYamlUpwellingTests(unittest.TestCase):
    def test_production_yamls_have_no_upwelling(self) -> None:
        for name in PRODUCTION_YAMLS:
            cfg = _load(name)
            cov = cfg["covariates"]
            self.assertNotIn("upwelling", cov.get("dynamic") or [], name)
            self.assertNotIn("upwelling", cov.get("static") or [], name)
            self.assertNotIn("upwelling", cov.get("upstream_fields") or {}, name)
            self.assertNotIn("upwelling", cfg["model"]["formula_shared"], name)

    def test_production_yamls_fix_time_idx_origin(self) -> None:
        for name in PRODUCTION_YAMLS:
            origin = _load(name)["data"].get("time_idx_origin")
            self.assertRegex(str(origin), r"^\d{4}-\d{2}-\d{2}$", name)

    def test_amendment_documents_reintroduction_rule(self) -> None:
        text = AMENDMENT.read_text(encoding="utf-8")
        self.assertIn("14,592", text)
        self.assertIn("never imputed", text)
        self.assertIn("later prereg amendment", text)
        self.assertIn("publicly licensed", text)


if __name__ == "__main__":
    unittest.main()
