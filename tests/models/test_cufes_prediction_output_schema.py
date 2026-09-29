"""JSON schema for CUFES prediction grid rows."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO / "configs" / "schemas" / "cufes_prediction_output.schema.json"
DOC_PATH = REPO / "docs" / "CUFES_PREDICTION_OUTPUT_CONTRACT.md"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_file_exists_and_lists_five_evidence_states() -> None:
    schema = load_schema()
    states = schema["properties"]["evidence_state"]["enum"]
    assert len(states) == 5
    assert "UNKNOWN" in states
    assert "HINDCAST_GLORYS" in states


def test_doc_mentions_required_contract_fields() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for field in (
        "p_encounter",
        "p_lo90",
        "p_hi90",
        "ood_level",
        "evidence_state",
        "unknown_reason",
        "lead_days",
        "forecast_age_hours",
        "source_run_time",
        "fallback_used",
        "valid_time",
    ):
        assert field in text


def test_example_dry_run_row_validates() -> None:
    schema = load_schema()
    row = {
        "cell_id": "g1_2",
        "species": "sardine",
        "valid_day": "2020-06-01",
        "p_encounter": 0.12,
        "p_lo90": 0.05,
        "p_hi90": 0.2,
        "ood_level": 0,
        "evidence_state": "HINDCAST_GLORYS",
        "unknown_reason": None,
        "lead_days": 0,
        "forecast_age_hours": None,
        "source_run_time": None,
        "fallback_used": False,
        "valid_time": None,
        "dry_run": True,
    }
    jsonschema.validate(row, schema)


def test_production_yaml_does_not_commit_dry_run_paths() -> None:
    for name in ("cufes_sardine_synthetic.yaml", "cufes_anchovy_synthetic.yaml"):
        path = REPO / "configs" / "models" / name
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        cfg = doc.get("fishai_engine_config") or doc
        out = (cfg.get("output") or {}).get("dir", "")
        assert "DRY_RUN" not in str(out)
