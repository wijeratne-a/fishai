"""Validate egg-encounter grid rows against the CUFES prediction schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "configs" / "schemas" / "cufes_prediction_output.schema.json"
)

REQUIRED_STATES = {
    "HINDCAST_GLORYS",
    "NOWCAST_UNVALIDATED",
    "FORECAST",
    "DEGRADED",
    "UNKNOWN",
}


def load_schema(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or SCHEMA_PATH).read_text(encoding="utf-8"))


def validate_prediction_rows(rows: list[dict[str, Any]], schema: dict[str, Any] | None = None) -> None:
    """Fail closed unless every row matches the prediction output schema.

    UNKNOWN rows must not carry an encounter probability.
    """
    if not rows:
        raise ValueError("prediction surface has no rows")
    compiled = schema or load_schema()
    for i, row in enumerate(rows):
        jsonschema.validate(row, compiled)
        if row["evidence_state"] not in REQUIRED_STATES:
            raise ValueError(f"row {i} evidence_state is not in the contract enum")
        if row["evidence_state"] == "UNKNOWN":
            if row.get("p_encounter") is not None:
                raise ValueError(f"row {i} UNKNOWN must have null p_encounter")
            if not row.get("unknown_reason"):
                raise ValueError(f"row {i} UNKNOWN requires unknown_reason")
        elif row.get("p_encounter") is None:
            raise ValueError(f"row {i} issued state requires p_encounter")
        if int(row["ood_level"]) >= 2 and row["evidence_state"] != "UNKNOWN":
            raise ValueError(f"row {i} ood_level >= 2 must be UNKNOWN")
