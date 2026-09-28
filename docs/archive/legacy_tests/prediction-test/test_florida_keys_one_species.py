import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "fk_one_species", ROOT / "scripts" / "modeling" / "florida_keys_one_species.py"
)
fk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fk)


def synthetic_rows(n=400, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        depth = float(rng.uniform(1, 30))
        vis = float(rng.uniform(5, 30))
        temp = float(rng.uniform(24, 31))
        hab = ["A", "B", "C"][i % 3]
        eta = 1.5 - 0.05 * depth + (0.8 if hab == "B" else 0.0)
        y = int(rng.random() < 1 / (1 + np.exp(-eta)))
        rows.append({"year": 2014, "depth": depth, "vis": vis, "temp": temp, "habitat": hab,
                     "block": f"blk{i % 4}", "psu": f"p{i // 2}", "y": y, "date": "2014-06-01"})
    return rows


class DesignGuards(unittest.TestCase):
    def test_no_year_feature_and_test_year_not_trained(self):
        self.assertNotIn(fk.TEST_YEAR, fk.TRAIN_YEARS)
        spec = fk.make_spec(synthetic_rows(), ["depth", "vis", "temp"])
        row = {**synthetic_rows(1)[0], "year": 2099}
        self.assertEqual(fk.design_row(row, spec), fk.design_row({**row, "year": 2014}, spec))

    def test_design_refuses_missing_covariates(self):
        spec = fk.make_spec(synthetic_rows(), ["depth", "vis", "temp"])
        for f in ("depth", "vis", "temp"):
            with self.assertRaises(ValueError):
                fk.design_row({**synthetic_rows(1)[0], f: None}, spec)

    def test_scaler_uses_only_rows_given(self):
        train = synthetic_rows(200)
        shifted = [{**r, "depth": r["depth"] + 100} for r in synthetic_rows(200, seed=2)]
        spec = fk.make_spec(train, ["depth"])
        self.assertAlmostEqual(spec["scaler"]["depth"]["mean"], float(np.mean([r["depth"] for r in train])))
        self.assertEqual(spec, fk.make_spec(train, ["depth"]))
        self.assertNotEqual(spec, fk.make_spec(train + shifted, ["depth"]))


class EstimatorGuards(unittest.TestCase):
    def test_fit_recovers_signal_and_beats_prevalence(self):
        rows = synthetic_rows(2000)
        spec = fk.make_spec(rows, ["depth", "vis"])
        X, y = fk.matrix(rows, spec)
        p = fk.predict_proba(X, fk.fit_logistic(X, y))
        self.assertLess(fk.brier(p, y), fk.brier(np.full(len(y), y.mean()), y))

    def test_nonconvergence_raises(self):
        X = np.column_stack([np.ones(4), [0, 1, 2, 3]])
        y = np.array([0, 0, 1, 1], dtype=float)
        with self.assertRaises(RuntimeError):
            fk.fit_logistic(X, y, l2=0.0, max_iter=3)


class TemperatureGuards(unittest.TestCase):
    def test_no_extrapolation_below_valid_column(self):
        depths = np.array([0, 2, 4, 6, 8, 10.0])
        temps = np.array([29, 28.8, 28.5, np.nan, np.nan, np.nan])
        self.assertAlmostEqual(fk.temperature_at_depth(depths, temps, 3.0), 28.65)
        self.assertIsNone(fk.temperature_at_depth(depths, temps, 7.0))
        self.assertIsNone(fk.temperature_at_depth(depths, np.full(6, np.nan), 1.0))

    def test_future_field_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = fk.HYCOM_DIR
            fk.HYCOM_DIR = Path(tmp)
            try:
                (Path(tmp) / "2014-06-01.nc").write_bytes(b"x")
                (Path(tmp) / "2014-06-01.json").write_text(json.dumps({"status": "ok", "offset_days": -1}))
                self.assertIsNone(fk.load_hycom("2014-06-01"))
            finally:
                fk.HYCOM_DIR = old

    def test_outputs_refuse_coordinates(self):
        with self.assertRaises(RuntimeError):
            fk.assert_no_coordinates({"a": [{"latitude": 25.0}]})


class MetricGuards(unittest.TestCase):
    def test_metrics_on_known_values(self):
        y = np.array([1, 0, 1, 1.0])
        p = np.array([0.9, 0.2, 0.6, 0.8])
        self.assertAlmostEqual(fk.brier(p, y), (0.01 + 0.04 + 0.16 + 0.04) / 4)
        self.assertEqual(fk.auc(p, y), 1.0)
        boot = fk.cluster_bootstrap_delta(p, np.full(4, 0.75), y, np.array(["a", "a", "b", "b"]), reps=50)
        self.assertLessEqual(boot["ci95_low"], boot["ci95_high"])
        self.assertTrue(fk.reliability(p, y))
        rng = np.random.default_rng(3)
        pp = rng.uniform(0.05, 0.95, 500)
        yy = (rng.random(500) < pp).astype(float)
        cal = fk.calibration_slope(pp, yy)
        self.assertLess(abs(cal["slope"] - 1.0), 0.4)

    def test_spatial_cv_runs_on_synthetic(self):
        cv = fk.spatial_cv(synthetic_rows(800), ["depth", "vis", "temp"])
        self.assertEqual(len(cv["folds"]), 4)


class PhaseGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = (fk.OUT, fk.PREREG, fk.LOCK)
        fk.OUT = Path(self.tmp.name)
        fk.PREREG = fk.OUT / "PREREGISTRATION.json"
        fk.LOCK = fk.OUT / "SCORED_ONCE.lock"

    def tearDown(self):
        fk.OUT, fk.PREREG, fk.LOCK = self.saved
        self.tmp.cleanup()

    def test_score_requires_preregistration(self):
        with self.assertRaises(RuntimeError):
            fk.score()

    def test_score_refuses_after_lock(self):
        fk.LOCK.write_text("x")
        with self.assertRaisesRegex(RuntimeError, "already been scored"):
            fk.score()

    def test_tampered_preregistration_refused(self):
        fk.PREREG.write_text("{}")
        (fk.OUT / "PREREGISTRATION.sha256").write_text("0" * 64)
        with self.assertRaisesRegex(RuntimeError, "modified"):
            fk.load_prereg()

    def test_freeze_refuses_twice(self):
        fk.PREREG.write_text("{}")
        with self.assertRaises(RuntimeError):
            fk.freeze()


class PredictGuards(unittest.TestCase):
    def artifact(self):
        rows = synthetic_rows(600)
        spec = fk.make_spec(rows, ["depth", "vis", "temp"])
        X, y = fk.matrix(rows, spec)
        return {
            "coefficients": list(fk.fit_logistic(X, y)), "spec": spec,
            "support": {f: {"min": min(r[f] for r in rows), "max": max(r[f] for r in rows)} for f in spec["numeric"]},
            "support_habitats": ["A", "B", "C"], "common_name": "x", "scientific_name": "y",
            "model_version": "t", "test_decision": "t", "publication_status": "NOT_PUBLISHED", "output_meaning": "m",
        }

    def test_predict_in_support(self):
        out = fk.predict({"habitat": "B", "depth": 10, "vis": 15, "temp": 28}, self.artifact())
        self.assertEqual(out["status"], "OK")
        self.assertTrue(0 < out["probability"] < 1)
        self.assertEqual(out["publication_status"], "NOT_PUBLISHED")

    def test_predict_refuses_out_of_support(self):
        art = self.artifact()
        for bad in ({"depth": 60}, {"temp": 35}, {"habitat": "Z"}, {"vis": None}):
            out = fk.predict({"habitat": "B", "depth": 10, "vis": 15, "temp": 28, **bad}, art)
            self.assertEqual(out["status"], "UNSUPPORTED")
            self.assertIsNone(out["probability"])


if __name__ == "__main__":
    unittest.main()
