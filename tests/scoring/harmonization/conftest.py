"""Shared fixtures for harmonization holdout scoring tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg

REPO = Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


@pytest.fixture
def ready_prereg_path(tmp_path: Path) -> Path:
    doc = load_harmonization_prereg(PREREG)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    ndbc = block["observations"]["ndbc_hull_temperature"]["forcing_gate"]["gradability"]
    ndbc["min_matched_daily_values"] = 10
    ndbc["min_distinct_buoys"] = 3
    strata = block["pass_fail_thresholds"]["cutoffs"]["strata"]["gradability"]
    strata["min_matched_daily_values"] = 10
    strata["min_distinct_buoys"] = 3
    path = tmp_path / "prereg.yaml"
    path.write_text(yaml.dump({"schema_version": 1, "harmonization_wcofs_glorys": block}), encoding="utf-8")
    return path
