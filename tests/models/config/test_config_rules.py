"""Model experiment config rules — synthetic configs only; no real experiments."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "models" / "config"
SCHEMA_PATH = CONFIG_DIR / "MODEL_EXPERIMENT_SCHEMA.json"
TEMPLATE_PATH = CONFIG_DIR / "EXPERIMENT_TEMPLATE.yaml"


def load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_template() -> dict:
    with TEMPLATE_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_experiment_config(config: dict[str, Any]) -> list[str]:
    """Return rule + schema error tokens; empty means accept."""
    errors: list[str] = []
    schema = load_schema()
    validator = jsonschema.Draft7Validator(schema)
    for err in validator.iter_errors(config):
        path = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"schema:{path}:{err.message}")

    # Presence-only must not be treated as absence
    if config.get("label_semantics") == "PRESENCE_ONLY_NO_ABSENCE":
        if config.get("treat_presence_only_as_absence") is True:
            errors.append("presence_only_treated_as_absence")
    if config.get("treat_presence_only_as_absence") is True:
        errors.append("presence_only_treated_as_absence")

    # Baseline required (beyond schema, catch empty/omitted kind explicitly)
    baseline = config.get("baseline")
    if baseline is None:
        errors.append("baseline_omitted")
    elif not isinstance(baseline, dict):
        errors.append("baseline_omitted")
    else:
        if not baseline.get("baseline_id"):
            errors.append("baseline_omitted")
        if not baseline.get("baseline_kind"):
            errors.append("baseline_omitted")

    # Must not tune on final holdout year
    holdout = config.get("holdout_year")
    tuning_years = config.get("tuning_years") or []
    if holdout is not None and holdout in tuning_years:
        errors.append("tune_on_final_holdout_year")
    if config.get("allow_tune_on_holdout") is True:
        errors.append("tune_on_final_holdout_year")

    extra_protocols = config.get("additional_protocol_ids") or []
    if extra_protocols or config.get("mix_protocols") is True:
        errors.append("mixed_protocols")

    if config.get("require_run_manifest") is not True:
        errors.append("run_manifest_required")

    return sorted(set(errors))


def valid_config(**overrides: Any) -> dict[str, Any]:
    cfg = {
        "experiment_id": "syn_cfg_1",
        "taxon_id": "urn:lsid:marinespecies.org:taxname:SYN",
        "region_id": "puerto_rico_rvc",
        "protocol_id": "RVC_STATIONARY_PLOT",
        "label_semantics": "SURVEY_DETECTION_WITH_NONDETECTION",
        "treat_presence_only_as_absence": False,
        "baseline": {
            "baseline_id": "prevalence_train_years",
            "baseline_kind": "PREVALENCE",
        },
        "train_years": [2016, 2019, 2021],
        "tuning_years": [2016, 2019],
        "holdout_year": 2023,
        "allow_tune_on_holdout": False,
        "publish_status": "NOT_PUBLISHED",
        "additional_protocol_ids": [],
        "mix_protocols": False,
        "require_run_manifest": True,
        "notes": "synthetic",
    }
    cfg.update(overrides)
    return cfg


class ConfigRulesTests(unittest.TestCase):
    def test_template_is_valid_and_locks_pr_2023(self):
        template = load_template()
        errors = validate_experiment_config(template)
        self.assertEqual(errors, [], errors)
        self.assertEqual(template["holdout_year"], 2023)
        self.assertEqual(template["region_id"], "puerto_rico_rvc")
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn("Puerto Rico 2023", text)
        self.assertIn("locked example holdout", text.lower())
        self.assertIn("not a refit", text.lower())

    def test_valid_config_passes(self):
        self.assertEqual(validate_experiment_config(valid_config()), [])

    def test_rejects_presence_only_as_absence(self):
        cfg = valid_config(
            label_semantics="PRESENCE_ONLY_NO_ABSENCE",
            treat_presence_only_as_absence=True,
        )
        errors = validate_experiment_config(cfg)
        self.assertIn("presence_only_treated_as_absence", errors)

    def test_rejects_omitted_baseline(self):
        cfg = valid_config()
        del cfg["baseline"]
        errors = validate_experiment_config(cfg)
        self.assertTrue(
            any(e == "baseline_omitted" or e.startswith("schema:") for e in errors),
            errors,
        )

    def test_rejects_tune_on_final_holdout_year(self):
        cfg = valid_config(tuning_years=[2019, 2023], holdout_year=2023)
        errors = validate_experiment_config(cfg)
        self.assertIn("tune_on_final_holdout_year", errors)

    def test_rejects_allow_tune_on_holdout_flag(self):
        cfg = valid_config(allow_tune_on_holdout=True)
        errors = validate_experiment_config(cfg)
        self.assertIn("tune_on_final_holdout_year", errors)

    def test_rejects_mixed_protocols(self):
        cfg = valid_config(mix_protocols=True, additional_protocol_ids=["BOTTOM_TRAWL"])
        errors = validate_experiment_config(cfg)
        self.assertIn("mixed_protocols", errors)

    def test_rejects_missing_run_manifest_requirement(self):
        cfg = valid_config()
        cfg["require_run_manifest"] = False
        errors = validate_experiment_config(cfg)
        self.assertTrue(
            any(e == "run_manifest_required" or e.startswith("schema:") for e in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
