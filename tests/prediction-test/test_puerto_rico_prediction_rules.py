"""Synthetic-only tests for the Puerto Rico internal prediction test helpers.

No real survey coordinates. Does not read data/raw gzip files.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "modeling" / "run_puerto_rico_prediction_test.py"


def load_module():
    spec = importlib.util.spec_from_file_location("pr_prediction_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PuertoRicoPredictionTestRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def test_holdout_year_not_in_training_mask(self) -> None:
        years = [2016, 2019, 2021, 2023, 2023]
        mask = self.mod.training_mask(years, holdout_year=2023)
        self.assertEqual(mask, [True, True, True, False, False])
        for year, is_train in zip(years, mask):
            if year == 2023:
                self.assertFalse(is_train)
            else:
                self.assertTrue(is_train)

    def test_missing_species_without_frame_is_not_zero(self) -> None:
        # Species absent from the year's list → not evaluable (None), not a zero.
        universe = {2019: {"STE PART"}, 2021: {"STE PART", "SPA AURO"}}
        rec = {"year": 2019, "pos": set()}
        label = self.mod.label_event_for_species(rec, "SPA AURO", universe)
        self.assertIsNone(label)
        self.assertNotEqual(label, 0)

        # On-list with no positive NUM → survey non-detection zero, still not absence claim.
        on_list = self.mod.label_event_for_species(
            {"year": 2021, "pos": set()}, "SPA AURO", universe
        )
        self.assertEqual(on_list, 0)

        detected = self.mod.label_event_for_species(
            {"year": 2021, "pos": {"SPA AURO"}}, "SPA AURO", universe
        )
        self.assertEqual(detected, 1)

    def test_output_records_have_no_lat_lon_keys(self) -> None:
        dirty = {
            "species_code": "STE PART",
            "holdout_brier_model": 0.2,
            "latitude": 18.1,
            "longitude": -66.5,
            "lat": 18.1,
            "lon": -66.5,
        }
        clean = self.mod.sanitize_record(dirty)
        for key in ("latitude", "longitude", "lat", "lon", "LATITUDE", "LONGITUDE"):
            self.assertNotIn(key, clean)
        self.assertEqual(clean["species_code"], "STE PART")
        self.assertEqual(clean["holdout_brier_model"], 0.2)

        # Synthetic evaluate path also must not emit coordinates.
        events = {
            (2016, "U1", "1", "t0"): {
                "year": 2016,
                "block": "A",
                "habitat": "H1",
                "depth": 10.0,
                "vis": 12.0,
                "pos": {"STE PART"},
                "name": {"STE PART": "Stegastes partitus"},
            },
            (2019, "U2", "1", "t1"): {
                "year": 2019,
                "block": "B",
                "habitat": "H1",
                "depth": 12.0,
                "vis": 14.0,
                "pos": set(),
                "name": {},
            },
            (2021, "U3", "1", "t2"): {
                "year": 2021,
                "block": "A",
                "habitat": "H2",
                "depth": 8.0,
                "vis": 10.0,
                "pos": {"STE PART"},
                "name": {},
            },
            (2023, "U4", "1", "t3"): {
                "year": 2023,
                "block": "B",
                "habitat": "H1",
                "depth": 11.0,
                "vis": 13.0,
                "pos": set(),
                "name": {},
            },
        }
        # Enough synthetic rows for folds: duplicate across blocks/years
        for i in range(10):
            events[(2016, f"A{i}", "1", "t")] = {
                "year": 2016,
                "block": "A",
                "habitat": "H1",
                "depth": 9.0 + i * 0.1,
                "vis": 11.0,
                "pos": {"STE PART"} if i % 2 == 0 else set(),
                "name": {},
            }
            events[(2019, f"B{i}", "1", "t")] = {
                "year": 2019,
                "block": "B",
                "habitat": "H2",
                "depth": 10.0 + i * 0.1,
                "vis": 12.0,
                "pos": {"STE PART"} if i % 3 == 0 else set(),
                "name": {},
            }
            events[(2021, f"A{i}", "2", "t")] = {
                "year": 2021,
                "block": "A",
                "habitat": "H1",
                "depth": 11.0,
                "vis": 13.0,
                "pos": set() if i % 2 else {"STE PART"},
                "name": {},
            }
            events[(2023, f"B{i}", "2", "t")] = {
                "year": 2023,
                "block": "B",
                "habitat": "H1",
                "depth": 12.0,
                "vis": 14.0,
                "pos": {"STE PART"} if i % 4 == 0 else set(),
                "name": {},
            }
        universe = {
            2016: {"STE PART"},
            2019: {"STE PART"},
            2021: {"STE PART"},
            2023: {"STE PART"},
        }
        out = self.mod.evaluate_species(
            "STE PART", "Stegastes partitus", events, universe
        )
        for key in ("latitude", "longitude", "lat", "lon"):
            self.assertNotIn(key, out)

    def test_sst_acceptance_rule_requires_both_scores_and_calibration(self) -> None:
        # Better Brier and log loss, calibrated → accept.
        self.assertTrue(
            self.mod.accept_sst_model(
                survey_brier=0.20,
                survey_logloss=0.55,
                sst_brier=0.19,
                sst_logloss=0.54,
                mean_pred=0.40,
                holdout_prevalence=0.42,
            )
        )
        # Equal allowed.
        self.assertTrue(
            self.mod.accept_sst_model(
                survey_brier=0.20,
                survey_logloss=0.55,
                sst_brier=0.20,
                sst_logloss=0.55,
                mean_pred=0.50,
                holdout_prevalence=0.50,
            )
        )
        # Worse log loss → reject even if Brier improves.
        self.assertFalse(
            self.mod.accept_sst_model(
                survey_brier=0.20,
                survey_logloss=0.55,
                sst_brier=0.19,
                sst_logloss=0.56,
                mean_pred=0.40,
                holdout_prevalence=0.42,
            )
        )
        # Wild calibration → reject.
        self.assertFalse(
            self.mod.accept_sst_model(
                survey_brier=0.20,
                survey_logloss=0.55,
                sst_brier=0.19,
                sst_logloss=0.54,
                mean_pred=0.80,
                holdout_prevalence=0.40,
            )
        )

    def test_design_with_sst_rejects_missing_values(self) -> None:
        rec = {
            "year": 2019,
            "habitat": "H1",
            "depth": 10.0,
            "vis": 12.0,
            "sst": None,
        }
        with self.assertRaises(ValueError):
            self.mod.design(rec, ["H1", "H2"], [2016, 2019], include_sst=True)
        rec["sst"] = 28.5
        x = self.mod.design(rec, ["H1", "H2"], [2016, 2019], include_sst=True)
        self.assertAlmostEqual(x[-1], (28.5 - 28.0) / 3.0)

    def test_sanitize_strips_coordinate_aliases_from_nested_dicts(self) -> None:
        clean = self.mod.sanitize_record(
            {
                "species_code": "SPA AURO",
                "LATITUDE": 18.0,
                "LONGITUDE": -66.0,
                "model_retained": "survey_only",
            }
        )
        self.assertNotIn("LATITUDE", clean)
        self.assertNotIn("LONGITUDE", clean)
        self.assertEqual(clean["model_retained"], "survey_only")


if __name__ == "__main__":
    unittest.main()
