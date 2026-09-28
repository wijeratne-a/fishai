"""Guards from the brutal scientific audit. Synthetic only. No raw coordinates."""

from __future__ import annotations

import importlib.util
import math
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PR_SCRIPT = REPO_ROOT / "scripts" / "modeling" / "run_puerto_rico_prediction_test.py"
FIT_SCRIPT = REPO_ROOT / "scripts" / "modeling" / "fit_regional_detection_models.py"
ANSWER_TS = REPO_ROOT / "globe" / "prototype" / "src" / "answer.ts"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CausalSstOffsets(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load(PR_SCRIPT, "pr_prediction_brutal")

    def test_offsets_never_include_future_days(self) -> None:
        offs = self.mod.causal_sst_offsets(2)
        self.assertEqual(offs, [0, -1, -2])
        self.assertTrue(all(o <= 0 for o in offs))

    def test_resolve_skips_future_even_if_only_future_has_sst(self) -> None:
        day = date(2021, 6, 15)
        day_sst = {
            (day + timedelta(days=1)).isoformat(): 29.1,
            (day + timedelta(days=2)).isoformat(): 29.2,
        }
        val, off = self.mod.resolve_sst_for_day(day, day_sst, max_past_days=2)
        self.assertIsNone(val)
        self.assertIsNone(off)

    def test_resolve_uses_same_day_then_past(self) -> None:
        day = date(2021, 6, 15)
        day_sst = {
            day.isoformat(): 28.0,
            (day - timedelta(days=1)).isoformat(): 27.0,
            (day + timedelta(days=1)).isoformat(): 99.0,
        }
        val, off = self.mod.resolve_sst_for_day(day, day_sst, max_past_days=2)
        self.assertEqual(val, 28.0)
        self.assertEqual(off, 0)
        del day_sst[day.isoformat()]
        val, off = self.mod.resolve_sst_for_day(day, day_sst, max_past_days=2)
        self.assertEqual(val, 27.0)
        self.assertEqual(off, 1)


class NoSilentImputation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load(PR_SCRIPT, "pr_prediction_brutal2")
        cls.fit = load(FIT_SCRIPT, "regional_fit_brutal")

    def test_design_refuses_missing_depth_and_visibility(self) -> None:
        rec = {"year": 2019, "habitat": "H1", "depth": None, "vis": 12.0}
        with self.assertRaises(ValueError):
            self.mod.design(rec, ["H1"], [2016, 2019])
        rec = {"year": 2019, "habitat": "H1", "depth": 10.0, "vis": None}
        with self.assertRaises(ValueError):
            self.mod.design(rec, ["H1"], [2016, 2019])
        with self.assertRaises(ValueError):
            self.fit.design(rec, ["H1"], [2016, 2019])

    def test_build_labeled_rows_drops_missing_vis_instead_of_inventing_15(self) -> None:
        events = {
            (2019, "U1", "1", "t"): {
                "year": 2019,
                "block": "A",
                "habitat": "H1",
                "depth": 10.0,
                "vis": None,
                "pos": set(),
            }
        }
        rows = self.mod.build_labeled_rows(events, {2019: {"STE PART"}}, "STE PART")
        self.assertEqual(rows, [])


class TrainingMaskExplicitYears(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load(PR_SCRIPT, "pr_prediction_brutal3")

    def test_interstitial_year_is_not_silently_training(self) -> None:
        years = [2016, 2019, 2021, 2022, 2023]
        mask = self.mod.training_mask(years, holdout_year=2023)
        self.assertEqual(mask, [True, True, True, False, False])


class FiniteFit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load(PR_SCRIPT, "pr_prediction_brutal4")

    def test_nonfinite_coefficients_are_rejected(self) -> None:
        with self.assertRaises(RuntimeError):
            self.mod.require_finite_parameters([0.1, float("nan")])
        with self.assertRaises(RuntimeError):
            self.mod.require_finite_parameters([math.inf])
        self.assertEqual(self.mod.require_finite_parameters([0.0, -0.2]), [0.0, -0.2])


class ResultsLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load(PR_SCRIPT, "pr_prediction_brutal5")

    def test_locked_report_cannot_be_overwritten(self) -> None:
        lock = self.mod.RESULTS_LOCK
        self.assertTrue(lock.is_file(), "RESULTS_LOCKED must exist after this audit")
        with self.assertRaises(RuntimeError):
            self.mod.write_final_report([], {}, [])


class UiClaimGuards(unittest.TestCase):
    def test_answer_strip_does_not_say_where_now(self) -> None:
        text = ANSWER_TS.read_text(encoding="utf-8")
        self.assertNotIn("Where now", text)
        self.assertIn("What is known", text)


if __name__ == "__main__":
    unittest.main()
