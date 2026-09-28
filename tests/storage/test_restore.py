"""Restore checksum tests. No survey coordinates."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT = REPO_ROOT / "docs" / "archive" / "audit" / "storage"


class RestoreVerificationTests(unittest.TestCase):
    def test_restore_results_exist_and_one_checksum_matches(self) -> None:
        csv_path = AUDIT / "RESTORE_RESULTS.csv"
        self.assertTrue(csv_path.is_file(), "RESTORE_RESULTS.csv missing")
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        ids = {row["check_id"]: row for row in rows}
        self.assertIn("RV-010", ids)
        self.assertIn("RV-011", ids)
        self.assertEqual(ids["RV-010"]["result"], "PASS")
        self.assertEqual(ids["RV-011"]["result"], "PASS")
        self.assertEqual(ids["RV-010"]["sha256_original"], ids["RV-010"]["sha256_restored"])
        self.assertTrue(ids["RV-010"]["sha256_original"])
        text = (AUDIT / "RESTORE_VERIFICATION.md").read_text(encoding="utf-8")
        self.assertIn("PASS", text)
        self.assertIn("Coordinates in this report", text)
        self.assertNotIn("latitude", text.lower())
        self.assertNotIn("longitude", text.lower())


if __name__ == "__main__":
    unittest.main()
