"""Frozen experiment rules — synthetic only. Invalid configs and leakage fail closed.

No new real-species fit. No coordinates.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tests" / "models" / "config"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "modeling"))

from test_config_rules import valid_config, validate_experiment_config  # noqa: E402
from write_run_manifest import build_manifest, validate_manifest, write_manifest  # noqa: E402


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_units = _load("syn_units", "tests/measurements/test_units.py")
_time = _load("syn_time", "tests/time/test_temporal_integrity.py")
_pipe = _load("syn_pipe", "tests/end-to-end-scientific/test_synthetic_pipeline.py")
validate_measurement = _units.validate_measurement
validate_temporal_record = _time.validate_temporal_record
apply_support_mask = _pipe.apply_support_mask
join_feature = _pipe.join_feature
label_survey_event = _pipe.label_survey_event


class FrozenProtocolRejects(unittest.TestCase):
    def test_presence_only_as_absence_fails_closed(self):
        cfg = valid_config(
            label_semantics="PRESENCE_ONLY_NO_ABSENCE",
            treat_presence_only_as_absence=True,
        )
        self.assertIn("presence_only_treated_as_absence", validate_experiment_config(cfg))

    def test_mixed_protocols_fail_closed(self):
        cfg = valid_config(mix_protocols=True, additional_protocol_ids=["TRAWL"])
        self.assertIn("mixed_protocols", validate_experiment_config(cfg))

    def test_omitted_baseline_fails_closed(self):
        cfg = valid_config()
        del cfg["baseline"]
        errors = validate_experiment_config(cfg)
        self.assertTrue(any("baseline" in e for e in errors), errors)

    def test_tune_on_locked_year_fails_closed(self):
        cfg = valid_config(tuning_years=[2019, 2023], holdout_year=2023)
        self.assertIn("tune_on_final_holdout_year", validate_experiment_config(cfg))

    def test_future_leakage_fails_closed(self):
        event = datetime(2021, 6, 1, tzinfo=timezone.utc)
        future = datetime(2023, 6, 1, tzinfo=timezone.utc)
        self.assertIsNone(join_feature(event, future, 27.0))
        temporal = validate_temporal_record(
            {
                "lane": "operational",
                "event_time_utc": "2021-06-01T00:00:00Z",
                "feature_available_at_utc": "2023-06-01T00:00:00Z",
            }
        )
        self.assertIn("TI-POST-EVENT-FEATURE", temporal)

    def test_missing_to_absence_fails_closed(self):
        event = {"event_id": "SYN-E", "effort_completed": True, "counts": {"SP_A": 1}}
        labeled = label_survey_event(event, "SP_MISSING", frame_codes=None)
        self.assertEqual(labeled["label"], "NOT_EVALUATED")
        self.assertNotEqual(labeled["label"], "SURVEY_NONDETECTION")

    def test_unit_mixup_fails_closed(self):
        errors = validate_measurement(
            {
                "measurement_type": "atlantic_rvc_num",
                "quantity": "real_valued_average",
                "measurement_value": 2.35,
                "treated_as_integer_fish_count": True,
            }
        )
        self.assertIn("UC-NUM-AS-INTEGER-COUNT", errors)

    def test_unsupported_cell_fails_closed(self):
        self.assertEqual(apply_support_mask(40.0, vmin=20.0, vmax=28.0), "UNSUPPORTED")


class SyntheticRunEmitsManifest(unittest.TestCase):
    def test_synthetic_run_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "RUN_MANIFEST.json"
            fixture = Path(tmp) / "synth.csv"
            fixture.write_text("a,b\n1,2\n", encoding="utf-8")
            manifest = build_manifest(
                experiment_id="syn_frozen_protocol_1",
                random_seed=20260926,
                train_years=[2016, 2019, 2021],
                holdout_year=2023,
                input_paths=[fixture],
                notes="synthetic",
            )
            write_manifest(dest, manifest)
            self.assertTrue(dest.is_file())
            self.assertEqual(validate_manifest(manifest), [])
            self.assertEqual(manifest["publish_status"], "NOT_PUBLISHED")
            self.assertIn("synth.csv", manifest["input_checksums"])
            self.assertNotIn(2023, manifest["train_years"])


if __name__ == "__main__":
    unittest.main()
