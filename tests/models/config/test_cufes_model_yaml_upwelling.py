"""Pilot production CUFES model YAMLs drop upwelling (prereg amendment path B)."""

from __future__ import annotations

import csv
import unittest
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_CONFIG_DIR = REPO_ROOT / "configs" / "models"
AMENDMENT = REPO_ROOT / "prereg" / "pilot_model_upwelling_amendment.md"
DOCKERFILE = REPO_ROOT / "Dockerfile"
PILOT_EVENTS = REPO_ROOT / "tests" / "fixtures" / "cufes_pilot_distances.csv"
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

    def test_time_idx_epoch_precedes_tracked_pilot_minimum(self) -> None:
        with PILOT_EVENTS.open(newline="", encoding="utf-8") as handle:
            first_event = min(row["time"] for row in csv.DictReader(handle))
        self.assertEqual(first_event[:10], "1996-03-15")
        pilot_min = date.fromisoformat(first_event[:10])
        for name in PRODUCTION_YAMLS:
            origin = date.fromisoformat(str(_load(name)["data"]["time_idx_origin"]))
            self.assertEqual(origin, date(1990, 1, 1), name)
            self.assertLess(origin, pilot_min, name)

    def test_amendment_documents_reintroduction_rule(self) -> None:
        text = AMENDMENT.read_text(encoding="utf-8")
        self.assertIn("14,592", text)
        self.assertIn("never imputed", text)
        self.assertIn("later prereg amendment", text)
        self.assertIn("publicly licensed", text)

    @unittest.skipUnless(DOCKERFILE.is_file(), "Dockerfile is not part of the image")
    def test_docker_image_copies_amendment_artifact(self) -> None:
        copied = [
            line.split()[1].rstrip("/")
            for line in DOCKERFILE.read_text(encoding="utf-8").splitlines()
            if line.startswith("COPY ")
        ]
        rel = AMENDMENT.relative_to(REPO_ROOT).as_posix()
        self.assertTrue(
            any(rel == src or rel.startswith(src + "/") for src in copied),
            f"Dockerfile must COPY {rel}",
        )


if __name__ == "__main__":
    unittest.main()
