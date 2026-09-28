"""Shoreline SHA gate vs prereg frozen_shoreline_reference (#9)."""

from __future__ import annotations

import yaml

from fishai.evaluation.harmonization_prereg import (
    frozen_shoreline_reference_sha256,
    load_harmonization_prereg,
)
from fishai.scoring.harmonization.prereg_gate import collect_prereg_gate_violations
from fishai.scoring.harmonization.shoreline_gate import frozen_shoreline_sha256_from_prereg

REPO = __import__("pathlib").Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


def test_frozen_shoreline_sha_from_named_prereg_block() -> None:
    doc = load_harmonization_prereg(PREREG)
    sha = frozen_shoreline_sha256_from_prereg(doc)
    assert sha is not None
    assert sha == frozen_shoreline_reference_sha256(doc)


def test_gate_rejects_shoreline_sha_mismatch() -> None:
    doc = load_harmonization_prereg(PREREG)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    block["nearshore"]["shoreline_sha256"] = "deadbeef"
    violations = collect_prereg_gate_violations({"harmonization_wcofs_glorys": block})
    assert "nearshore.shoreline_sha256_mismatch_frozen_shoreline_reference" in violations


def test_gate_accepts_committed_prereg_shoreline() -> None:
    doc = load_harmonization_prereg(PREREG)
    violations = collect_prereg_gate_violations(doc)
    assert "nearshore.shoreline_sha256_mismatch_frozen_shoreline_reference" not in violations
    assert "frozen_shoreline_reference.sha256_missing_or_invalid" not in violations
