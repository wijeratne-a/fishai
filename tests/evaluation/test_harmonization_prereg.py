"""Harmonization WCOFS/GLORYS prereg load and scoring gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import (
    HarmonizationPreregNotReadyError,
    PLACEHOLDER_TOKEN,
    assert_harmonization_prereg_ready_for_scoring,
    load_harmonization_prereg,
    run_harmonization_scoring,
)

REPO = Path(__file__).resolve().parents[2]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"
RESOLUTION_EXACT = "WCOFS coarsened to GLORYS grid, area-weighted, wet-masked"


def test_prereg_temporal_split_dates_resolution_and_shared_functions() -> None:
    doc = load_harmonization_prereg(PREREG)
    split = doc["harmonization_wcofs_glorys"]["temporal_split"]
    assert split["overlap_start"] == "2024-09-01"
    assert split["overlap_end"] == "2026-06-23"
    assert split["fit_start"] == "2024-09-01"
    assert split["fit_end"] == "2025-08-31"
    assert split["test_start"] == "2025-09-01"
    assert split["test_end"] == "2026-06-23"
    assert split["resolution"] == RESOLUTION_EXACT
    shared = split["shared_functions"]
    assert shared["module"] == "fishai.ingestion.physics.wcofs_glorys_grid"
    assert shared["coarsen_wcofs_to_glorys"] == "coarsen_wcofs_to_glorys"
    assert shared["compute_wcofs_covariates_on_glorys_grid"] == "compute_wcofs_covariates_on_glorys_grid"
    assert split["notes"]["last_fit_day"] == "2025-08-31"
    assert split["notes"]["first_test_day"] == "2025-09-01"


def test_mapping_artifact_section_and_fit_date_range_matches_split() -> None:
    doc = load_harmonization_prereg(PREREG)
    block = doc["harmonization_wcofs_glorys"]
    split = block["temporal_split"]
    artifact = block.get("mapping_artifact")
    assert isinstance(artifact, dict)
    assert artifact.get("fitted_by") == "bot3"
    assert "wcofs_to_glorys_map/v1" in artifact.get("frozen_directory", "")
    manifest = artifact.get("manifest") or {}
    assert manifest.get("filename") == "manifest.json"
    assert "fitting_commit_sha" in manifest.get("records", [])
    assert "fit_split_parquet_sha256" in manifest.get("records", [])
    assert "prereg_commit_sha" in manifest.get("records", [])
    assert "variables_mapped" in manifest.get("records", [])
    assert "fit_date_range" in manifest.get("records", [])
    fit_range = artifact.get("fit_date_range") or {}
    assert fit_range.get("fit_start") == split["fit_start"]
    assert fit_range.get("fit_end") == split["fit_end"]


def test_native_wcofs_diagnostic_never_through_harmonization_map() -> None:
    doc = load_harmonization_prereg(PREREG)
    candidates = doc["harmonization_wcofs_glorys"]["models_scored"]["candidates"]
    native = next(c for c in candidates if c["id"] == "wcofs_native")
    assert native.get("harmonization_map") == "never"
    assert native.get("role") == "diagnostic_only"


def test_scoring_entry_point_raises_while_placeholders_unset() -> None:
    doc = load_harmonization_prereg(PREREG)
    with pytest.raises(HarmonizationPreregNotReadyError, match="unset prereg fields"):
        assert_harmonization_prereg_ready_for_scoring(doc)
    with pytest.raises(HarmonizationPreregNotReadyError, match="shoreline_sha256"):
        run_harmonization_scoring(PREREG)


def test_nearshore_bot2_pr7_fields_and_pending_placeholders() -> None:
    doc = load_harmonization_prereg(PREREG)
    near = doc["harmonization_wcofs_glorys"]["nearshore"]
    assert near["shoreline_source"] == "Natural Earth ne_10m_land"
    assert near["shoreline_version"] == "5.1.1"
    assert near["license"] == "public domain"
    assert near["clip"]["lat_min"] == 31
    assert near["clip"]["lon_max"] == -116
    assert near["clip"]["includes_channel_islands"] is True
    assert near["shoreline_path"] == "data/reference/shoreline/ne_10m_land_pilot_clip.json"
    assert near["cutoff_km"] == 20
    assert "Geodesic on WGS84" in near["distance"]
    assert near["shoreline_sha256"] == PLACEHOLDER_TOKEN
    assert near["shoreline_simplification_check"] == PLACEHOLDER_TOKEN


def test_scoring_entry_point_passes_gate_when_placeholders_replaced(tmp_path: Path) -> None:
    doc = load_harmonization_prereg(PREREG)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    block["nearshore"]["shoreline_sha256"] = "deadbeef"
    block["nearshore"]["shoreline_simplification_check"] = {
        "max_coastline_displacement_m": 0.0,
        "nearshore_flag_diff_cell_count": 0,
    }
    block["pass_fail_thresholds"]["cutoffs"] = {"auditbot1": "v1-placeholder-not-gating"}
    patched = {"schema_version": 1, "harmonization_wcofs_glorys": block}
    path = tmp_path / "prereg.yaml"
    path.write_text(yaml.dump(patched), encoding="utf-8")
    assert_harmonization_prereg_ready_for_scoring(patched)
    with pytest.raises(NotImplementedError):
        run_harmonization_scoring(path)


def test_committed_prereg_still_has_expected_placeholders() -> None:
    doc = load_harmonization_prereg(PREREG)
    near = doc["harmonization_wcofs_glorys"]["nearshore"]
    assert near["shoreline_sha256"] == PLACEHOLDER_TOKEN
    assert near["shoreline_simplification_check"] == PLACEHOLDER_TOKEN
    assert doc["harmonization_wcofs_glorys"]["pass_fail_thresholds"]["cutoffs"] == PLACEHOLDER_TOKEN
