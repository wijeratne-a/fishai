"""Shoreline SHA gate: frozen_shoreline_reference_sha256() vs vendored file."""

from __future__ import annotations

import copy

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import (
    HarmonizationPreregNotReadyError,
    frozen_shoreline_reference_sha256,
    load_harmonization_prereg,
)
from fishai.scoring.harmonization.prereg_gate import collect_prereg_gate_violations
from fishai.scoring.harmonization.shoreline_gate import (
    collect_shoreline_sha256_gate_violations,
    sha256_file,
    shoreline_file_path_from_prereg,
)

REPO = __import__("pathlib").Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


def _doc_copy() -> dict:
    return copy.deepcopy(load_harmonization_prereg(PREREG))


def test_shoreline_hash_matches_vendored_file() -> None:
    doc = _doc_copy()
    expected = frozen_shoreline_reference_sha256(doc)
    path = shoreline_file_path_from_prereg(doc)
    assert sha256_file(path).lower() == expected.lower()
    assert collect_shoreline_sha256_gate_violations(doc) == []


def test_shoreline_hash_mismatch_refuses_scoring() -> None:
    doc = _doc_copy()
    block = doc["harmonization_wcofs_glorys"]
    wrong = "a" * 64
    block["frozen_shoreline_reference"]["sha256"] = wrong
    block["nearshore"]["shoreline_sha256"] = wrong
    violations = collect_shoreline_sha256_gate_violations(doc)
    assert "shoreline_file_sha256_mismatch_frozen_shoreline_reference" in violations


def test_frozen_shoreline_sha256_unavailable_refuses_scoring() -> None:
    doc = _doc_copy()
    del doc["harmonization_wcofs_glorys"]["frozen_shoreline_reference"]["sha256"]
    with pytest.raises(ValueError, match="malformed"):
        frozen_shoreline_reference_sha256(doc)
    violations = collect_shoreline_sha256_gate_violations(doc)
    assert violations == ["frozen_shoreline_reference_sha256_unavailable"]
