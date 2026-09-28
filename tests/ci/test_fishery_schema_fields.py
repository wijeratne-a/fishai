"""Unit tests for fishery-dependent schema/column name guard."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "ci"))

from check_fishery_schema_fields import forbidden_in_name  # noqa: E402


class FisheryFieldGuardTests(unittest.TestCase):
    def test_flags_vessel_and_logbook(self) -> None:
        self.assertIn("vessel_id", forbidden_in_name("vessel_id"))
        self.assertIn("logbook", forbidden_in_name("e_logbook_id"))

    def test_flags_fishery_observer_not_recorder(self) -> None:
        self.assertIn("fishery_observer", forbidden_in_name("observer_id"))
        self.assertEqual(forbidden_in_name("recorder_or_instrument_type"), [])

    def test_landings_without_documentation_url(self) -> None:
        self.assertIn("landings", forbidden_in_name("commercial_landings"))
        self.assertEqual(forbidden_in_name("documentation_url"), [])

    def test_flags_mmsi_imo_call_sign(self) -> None:
        self.assertIn("mmsi", forbidden_in_name("vessel_mmsi"))
        self.assertIn("imo", forbidden_in_name("imo_number"))
        self.assertIn("call_sign", forbidden_in_name("call_sign"))


if __name__ == "__main__":
    unittest.main()
