"""Pre-registration hard gate tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import (
    HarmonizationPreregNotReadyError,
    assert_harmonization_prereg_ready_for_scoring,
    load_harmonization_prereg,
)
from fishai.scoring.harmonization.prereg_gate import collect_prereg_gate_violations

REPO = Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


def _ready_block() -> dict:
    doc = load_harmonization_prereg(PREREG)
    return yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]


@pytest.mark.parametrize(
    "field_path,mutator",
    [
        ("temporal_split.fit_end", lambda b: b["temporal_split"].update({"fit_end": ""})),
        ("temporal_split.test_start", lambda b: b["temporal_split"].update({"test_start": None})),
        ("nearshore.shoreline_source", lambda b: b["nearshore"].update({"shoreline_source": "TBD"})),
        ("nearshore.shoreline_sha256", lambda b: b["nearshore"].update({"shoreline_sha256": ""})),
    ],
)
def test_gate_collects_violations(field_path: str, mutator) -> None:
    block = _ready_block()
    mutator(block)
    violations = collect_prereg_gate_violations({"harmonization_wcofs_glorys": block})
    assert any(field_path.split(".")[-1] in v for v in violations)


def test_committed_prereg_passes_gate() -> None:
    doc = load_harmonization_prereg(PREREG)
    assert_harmonization_prereg_ready_for_scoring(doc)


def test_assert_prereg_gate_raises_on_violations() -> None:
    block = _ready_block()
    block["temporal_split"]["test_start"] = ""
    with pytest.raises(HarmonizationPreregNotReadyError):
        assert_harmonization_prereg_ready_for_scoring({"harmonization_wcofs_glorys": block})
