"""Wind pull log status record when upwelling wind forcing is disabled."""

from __future__ import annotations

import json
from pathlib import Path

from fishai.ingestion.physics.cufes_training_covariates import record_upwelling_wind_status_pull_log


def test_upwelling_status_record_in_wind_pull_log(tmp_path: Path) -> None:
    log_path = tmp_path / "wind.jsonl"
    record_upwelling_wind_status_pull_log(log_path=log_path)
    line = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert line["record_type"] == "upwelling_wind_status"
    assert line["upwelling_status"] == "no_consistent_wind_product"
    assert line["wind_fetch_performed"] is False
    assert "upwelling_wind_audit" in line
