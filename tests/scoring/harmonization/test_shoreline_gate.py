"""Shoreline SHA gate vs overlap config vendored file."""

from __future__ import annotations

import yaml

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg
from fishai.scoring.harmonization.prereg_gate import collect_prereg_gate_violations
from fishai.scoring.harmonization.shoreline_gate import pilot_shoreline_sha256_from_overlap_config
from tests.scoring.harmonization._shoreline_fixtures import pilot_shoreline_sha_for_tests

REPO = __import__("pathlib").Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


def test_pilot_shoreline_sha_matches_pr7_readme_fingerprint() -> None:
    sha = pilot_shoreline_sha256_from_overlap_config()
    assert sha.startswith("2f677a16")
    assert sha.endswith("20996c")


def test_gate_rejects_shoreline_sha_mismatch() -> None:
    doc = load_harmonization_prereg(PREREG)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    block["nearshore"]["shoreline_sha256"] = "deadbeef"
    violations = collect_prereg_gate_violations({"harmonization_wcofs_glorys": block})
    assert "nearshore.shoreline_sha256_mismatch_overlap_config" in violations


def test_gate_accepts_matching_shoreline_sha() -> None:
    doc = load_harmonization_prereg(PREREG)
    violations = collect_prereg_gate_violations(doc)
    assert "nearshore.shoreline_sha256_mismatch_overlap_config" not in violations
