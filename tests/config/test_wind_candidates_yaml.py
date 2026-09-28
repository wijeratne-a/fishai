"""Wind candidate registry YAML — parse and required metadata fields."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WIND_CANDIDATES_PATH = REPO_ROOT / "config" / "wind_candidates.yaml"

REQUIRED_FIELDS = ("start", "end", "latency", "licence")


class WindCandidatesYamlTests(unittest.TestCase):
    def test_wind_candidates_yaml_parses_and_required_fields(self) -> None:
        raw = WIND_CANDIDATES_PATH.read_text(encoding="utf-8")
        doc = yaml.safe_load(raw)
        self.assertIsInstance(doc, dict)
        candidates = doc.get("candidates")
        self.assertIsInstance(candidates, list)
        self.assertGreaterEqual(len(candidates), 5, "survey should list all vetted candidates")

        for entry in candidates:
            self.assertIsInstance(entry, dict, msg=f"expected mapping, got {type(entry)}")
            entry_id = entry.get("id", "<missing id>")
            for field in REQUIRED_FIELDS:
                value = entry.get(field)
                self.assertIsNotNone(value, msg=f"{entry_id}: missing {field}")
                self.assertIsInstance(value, str, msg=f"{entry_id}: {field} must be a string")
                self.assertTrue(value.strip(), msg=f"{entry_id}: {field} must be non-empty")


if __name__ == "__main__":
    unittest.main()
