"""Tests for scientific safe-failure policy."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from safe_failure import SAFE_TOKENS, resolve_model_result, safe_failure


class SafeFailurePolicyTest(unittest.TestCase):
    def test_all_required_tokens_defined(self):
        required = {
            "UNKNOWN",
            "UNAVAILABLE",
            "INSUFFICIENT_DATA",
            "STALE",
            "UNSUPPORTED",
            "WITHHELD",
        }
        self.assertEqual(SAFE_TOKENS, required)

    def test_safe_failure_emits_token_not_probability(self):
        out = safe_failure(
            "UNAVAILABLE",
            species_code="STE PART",
            reason="artifact_missing",
        )
        self.assertEqual(out["status"], "UNAVAILABLE")
        self.assertIsNone(out["probability"])
        self.assertIsNone(out["substitute_species"])
        self.assertEqual(out["species_code"], "STE PART")

    def test_failed_model_not_replaced_by_another_species(self):
        alternate = {
            "species_code": "SPA AURO",
            "status": "OK",
            "probability": 0.42,
            "output_class": "INTERNAL_MODEL_OUTPUT",
        }
        out = resolve_model_result(
            requested_species="STE PART",
            model_ok=False,
            failure_token="INSUFFICIENT_DATA",
            failure_reason="non_numeric_scores",
            alternate_species_result=alternate,
        )
        self.assertEqual(out["species_code"], "STE PART")
        self.assertEqual(out["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(out["probability"])
        self.assertIsNone(out["substitute_species"])
        self.assertNotEqual(out.get("species_code"), "SPA AURO")
        self.assertNotEqual(out.get("probability"), 0.42)

    def test_each_token_accepted(self):
        for token in sorted(SAFE_TOKENS):
            out = safe_failure(token, species_code="EPI ITAJ", reason="unit_test")
            self.assertEqual(out["status"], token)

    def test_reject_invented_token(self):
        with self.assertRaises(ValueError):
            safe_failure("LOOKS_FINE", species_code="X", reason="no")

    def test_ok_path_keeps_requested_species(self):
        out = resolve_model_result(
            requested_species="STE PART",
            model_ok=True,
            probability=0.2,
        )
        self.assertEqual(out["status"], "OK")
        self.assertEqual(out["species_code"], "STE PART")
        self.assertEqual(out["probability"], 0.2)


if __name__ == "__main__":
    unittest.main()
