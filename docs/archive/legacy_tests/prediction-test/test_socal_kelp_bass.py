import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("socal_kelp_bass", ROOT / "scripts" / "modeling" / "socal_kelp_bass.py")
sc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sc)
HAVE_RAW = sc.FISH_CSV.is_file() and sc.FISH_EML.is_file() and sc.KELP_CSV.is_file()


def fish_row(site="AAAA", transect="1", day="2010-07-20", sp="PCLA", count="0", size="-99999", vis="5", **kw):
    row = {"SURVEY": "FISH", "YEAR": day[:4], "DATE": day, "AREA": "80", "SITE": site, "TRANSECT": transect,
           "VIS": vis, "SP_CODE": sp, "COUNT": count, "SIZE": size}
    row.update(kw)
    return row


def transect_rows(site, transect, pcla_counts, vis="5", day="2010-07-20"):
    rows = [fish_row(site, transect, day, "OTHR", "1", "20", vis)]
    for count, size in pcla_counts:
        rows.append(fish_row(site, transect, day, "PCLA", count, size, vis))
    return rows


def synthetic_rows(n=400, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        vis = float(rng.uniform(1, 12))
        kelp = float(rng.uniform(0, 2))
        temp = float(rng.uniform(12, 20))
        eta = -1.0 + 0.2 * vis + 0.8 * kelp
        y = int(rng.random() < 1 / (1 + np.exp(-eta)))
        rows.append({"year": 2010, "month": 7, "vis": vis, "kelp": kelp, "temp": temp, "habitat": sc.HABITAT,
                     "block": f"site{i % 5}", "site": f"site{i % 5}", "y": y, "date": "2010-07-20"})
    return rows


class LabelGuards(unittest.TestCase):
    def test_detection_zero_and_missing_semantics(self):
        rows = (
            transect_rows("A", "1", [("0", "-99999")])
            + transect_rows("A", "2", [("2", "25"), ("0", "-99999")])
            + transect_rows("A", "3", [("-99999", "-99999")])
            + transect_rows("A", "4", [("-99999", "-99999"), ("1", "30")])
        )
        ev = {e["transect"]: e for e in sc.events_from_rows(rows, 2010, "PCLA")}
        self.assertEqual(ev["A:1"]["y"], 0)
        self.assertEqual(ev["A:2"]["y"], 1)
        self.assertIsNone(ev["A:3"]["y"])
        self.assertEqual(ev["A:3"]["label_state"], "NOT_EVALUATED")
        self.assertEqual(ev["A:4"]["y"], 1)

    def test_missing_visibility_is_none_not_zero(self):
        ev = sc.events_from_rows(transect_rows("A", "1", [("0", "-99999")], vis="-99999"), 2010, "PCLA")
        self.assertIsNone(ev[0]["vis"])
        self.assertFalse(sc.complete({**ev[0], "kelp": 0.5, "temp": 15.0}))

    def test_dropped_zero_rows_fail_loudly(self):
        rows = transect_rows("A", "1", [("1", "20")])
        for t in range(2, 10):
            rows += [fish_row("A", str(t), sp="OTHR", count="1", size="20")]
        with self.assertRaisesRegex(RuntimeError, "zero rows may have been dropped"):
            sc.events_from_rows(rows, 2010, "PCLA")

    def test_species_not_on_list_refused(self):
        with self.assertRaisesRegex(RuntimeError, "not on the 2010 species list"):
            sc.events_from_rows(transect_rows("A", "1", [("0", "-99999")]), 2010, "PNEB")

    def test_size_count_confusion_refused(self):
        with self.assertRaisesRegex(RuntimeError, "swapped"):
            sc.events_from_rows(transect_rows("A", "1", [("0", "25")]), 2010, "PCLA")
        with self.assertRaisesRegex(RuntimeError, "swapped"):
            sc.events_from_rows(transect_rows("A", "1", [("1", "900")]), 2010, "PCLA")
        with self.assertRaises(RuntimeError):
            sc.events_from_rows(transect_rows("A", "1", [("2.5", "25")]), 2010, "PCLA")

    def test_protocol_mix_refused(self):
        rows = transect_rows("A", "1", [("0", "-99999")]) + [fish_row("A", "1", AREA="20")]
        with self.assertRaisesRegex(RuntimeError, "protocol"):
            sc.events_from_rows(rows, 2010, "PCLA")

    def test_cryptic_rows_ignored(self):
        rows = transect_rows("A", "1", [("0", "-99999")]) + [fish_row("A", "1", count="3", size="10", SURVEY="CRYPTIC FISH", AREA="20")]
        self.assertEqual(sc.events_from_rows(rows, 2010, "PCLA")[0]["y"], 0)


class KelpGuards(unittest.TestCase):
    def kelp_rows(self, fronds=("4", "0", "2", "6"), day="2010-07-20"):
        secs = [("20", "I"), ("20", "O"), ("40", "I"), ("40", "O")]
        return [{"SP_CODE": "MAPY", "YEAR": "2010", "SITE": "A", "TRANSECT": "1", "DATE": day, "QUAD": q, "SIDE": s,
                 "AREA": "20", "FRONDS": f} for (q, s), f in zip(secs, fronds)]

    def test_kelp_value_and_refusals(self):
        idx = sc.kelp_index_from_rows(self.kelp_rows())
        value, why = sc.kelp_value(idx[(2010, "A", "1")], "2010-07-20")
        self.assertEqual(why, "OK")
        self.assertAlmostEqual(value, np.log1p(12 / 80))
        self.assertEqual(sc.kelp_value(idx[(2010, "A", "1")], "2010-07-21")[1], "KELP_NOT_SAME_DAY")
        self.assertEqual(sc.kelp_value(None, "2010-07-20")[1], "NO_KELP_SURVEY")
        missing = sc.kelp_index_from_rows(self.kelp_rows(("4", "-99999", "2", "6")))
        self.assertEqual(sc.kelp_value(missing[(2010, "A", "1")], "2010-07-20"), (None, "KELP_COUNT_MISSING"))
        partial = sc.kelp_index_from_rows(self.kelp_rows()[:2])
        self.assertEqual(sc.kelp_value(partial[(2010, "A", "1")], "2010-07-20"), (None, "KELP_AREA_INCOMPLETE"))


class DesignGuards(unittest.TestCase):
    def test_no_year_feature_and_test_year_not_trained(self):
        self.assertNotIn(sc.TEST_YEAR, sc.TRAIN_YEARS)
        self.assertLess(max(sc.TRAIN_YEARS), sc.TEST_YEAR)
        spec = sc.fk.make_spec(synthetic_rows(), ["vis", "kelp", "temp"])
        row = synthetic_rows(1)[0]
        self.assertEqual(sc.fk.design_row({**row, "year": 2099}, spec), sc.fk.design_row(row, spec))
        self.assertEqual(len(sc.fk.design_row(row, spec)), 4)
        self.assertNotIn("year", sc.BASE_FEATURES)

    def test_design_refuses_missing_covariates(self):
        spec = sc.fk.make_spec(synthetic_rows(), ["vis", "kelp", "temp"])
        for f in ("vis", "kelp", "temp"):
            with self.assertRaises(ValueError):
                sc.fk.design_row({**synthetic_rows(1)[0], f: None}, spec)
            self.assertFalse(sc.complete({**synthetic_rows(1)[0], f: None}))

    def test_site_grouped_cv_holds_out_each_site(self):
        cv = sc.fk.spatial_cv(synthetic_rows(800), ["vis", "kelp"])
        self.assertEqual(sorted(f["block"] for f in cv["folds"]), [f"site{i}" for i in range(5)])

    def test_feasibility_verdict(self):
        counts = {str(y): {"detected": 0} for y in (*sc.TRAIN_YEARS, sc.TEST_YEAR)}
        self.assertEqual(sc.feasibility_verdict(counts)["verdict"], "INSUFFICIENT_DETECTIONS")
        counts = {str(y): {"detected": 5} for y in (*sc.TRAIN_YEARS, sc.TEST_YEAR)}
        self.assertEqual(sc.feasibility_verdict(counts)["verdict"], "INSUFFICIENT_DETECTIONS")
        counts = {str(y): {"detected": 10} for y in (*sc.TRAIN_YEARS, sc.TEST_YEAR)}
        self.assertEqual(sc.feasibility_verdict(counts)["verdict"], "FEASIBLE")

    def test_substitution_is_labelled(self):
        self.assertIn("USER MUST CONFIRM", sc.SPECIES["barred_sand_bass"]["substitution"])
        self.assertIsNone(sc.SPECIES["kelp_bass"]["substitution"])


class TemperatureGuards(unittest.TestCase):
    def test_future_field_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = sc.HYCOM_DIR
            sc.HYCOM_DIR = Path(tmp)
            try:
                (Path(tmp) / "2010-07-20.nc").write_bytes(b"x")
                (Path(tmp) / "2010-07-20.json").write_text(json.dumps({"status": "ok", "offset_days": -1}))
                self.assertIsNone(sc.load_hycom("2010-07-20"))
            finally:
                sc.HYCOM_DIR = old


class OutputGuards(unittest.TestCase):
    def test_outputs_refuse_coordinates(self):
        for bad in ({"a": [{"latitude": 34.4}]}, {"lon": -119.8}, {"x": {"_lat": 1}}):
            with self.assertRaises(RuntimeError):
                sc.assert_no_coordinates(bad)

    @unittest.skipUnless(HAVE_RAW, "SBC LTER raw files not present")
    def test_text_with_site_coordinate_refused(self):
        site = next(iter(sc.sbc_sites().values()))
        with self.assertRaises(RuntimeError):
            sc.assert_text_has_no_site_coordinates(f"near {site['_lat']:.3f}")
        sc.assert_text_has_no_site_coordinates("Brier 0.12345")
        self.assertNotIn("_lat", json.dumps(sc.site_depth_table()))

    @unittest.skipUnless(HAVE_RAW, "SBC LTER raw files not present")
    def test_real_metadata_parses(self):
        self.assertEqual(len(sc.sbc_sites()), 11)
        self.assertEqual(sc.verify_eml_units()["COUNT"], "number")


class PhaseGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = (sc.OUT_ROOT, sc.MODELS_DIR)
        sc.OUT_ROOT = Path(self.tmp.name) / "audit"
        sc.MODELS_DIR = Path(self.tmp.name) / "models"
        self.p = sc.paths("kelp_bass")
        self.p["out"].mkdir(parents=True)

    def tearDown(self):
        sc.OUT_ROOT, sc.MODELS_DIR = self.saved
        self.tmp.cleanup()

    def test_score_requires_preregistration(self):
        with self.assertRaisesRegex(RuntimeError, "no PREREGISTRATION"):
            sc.score("kelp_bass")

    def test_score_refuses_after_lock(self):
        self.p["lock"].write_text("x")
        with self.assertRaisesRegex(RuntimeError, "already been scored"):
            sc.score("kelp_bass")

    def test_score_refuses_other_test_year(self):
        with self.assertRaises(RuntimeError):
            sc.score("kelp_bass", test_year=2021)
        with self.assertRaisesRegex(RuntimeError, "training year"):
            sc.score("kelp_bass", test_year=sc.TEST_YEAR, rehearsal=True)

    def test_tampered_preregistration_refused(self):
        self.p["prereg"].write_text("{}")
        self.p["sha"].write_text("0" * 64)
        with self.assertRaisesRegex(RuntimeError, "modified"):
            sc.load_prereg("kelp_bass")

    def test_mismatched_preregistration_refused(self):
        text = json.dumps({"species": "kelp_bass", "train_years": list(sc.TRAIN_YEARS), "test_year": 2021})
        self.p["prereg"].write_text(text)
        self.p["sha"].write_text(sc.fk.sha256_bytes(text.encode()))
        with self.assertRaisesRegex(RuntimeError, "does not match"):
            sc.load_prereg("kelp_bass")

    def test_freeze_refuses_twice(self):
        self.p["prereg"].write_text("{}")
        with self.assertRaises(RuntimeError):
            sc.freeze("kelp_bass")

    def test_unknown_species_refused(self):
        with self.assertRaises(RuntimeError):
            sc.freeze("morone_saxatilis")


class PredictGuards(unittest.TestCase):
    def artifact(self):
        rows = synthetic_rows(600)
        spec = sc.fk.make_spec(rows, ["vis", "kelp", "temp"])
        X, y = sc.fk.matrix(rows, spec)
        return {
            "coefficients": list(sc.fk.fit_logistic(X, y)), "spec": spec,
            "support": {f: {"min": min(r[f] for r in rows), "max": max(r[f] for r in rows)} for f in spec["numeric"]},
            "survey_months": [7, 8], "common_name": "x", "scientific_name": "y", "model_version": "t",
            "test_decision": "t", "publication_status": "NOT_PUBLISHED", "output_meaning": "m", "substitution": None,
        }

    def test_predict_in_support(self):
        out = sc.predict({"vis": 6, "kelp": 1.0, "temp": 15, "month": 7}, self.artifact())
        self.assertEqual(out["status"], "OK")
        self.assertTrue(0 < out["probability"] < 1)
        self.assertEqual(out["publication_status"], "NOT_PUBLISHED")

    def test_predict_refuses_out_of_support(self):
        art = self.artifact()
        for bad in ({"vis": 40}, {"temp": 25}, {"kelp": 5.0}, {"month": 1}, {"vis": None}, {"temp": None}):
            out = sc.predict({"vis": 6, "kelp": 1.0, "temp": 15, "month": 7, **bad}, art)
            self.assertEqual(out["status"], "UNSUPPORTED")
            self.assertIsNone(out["probability"])


if __name__ == "__main__":
    unittest.main()
