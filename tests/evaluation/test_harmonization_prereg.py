"""Harmonization WCOFS/GLORYS prereg load and scoring gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import (
    FROZEN_PILOT_SHORELINE_REFERENCE_SHA256,
    HarmonizationPreregNotReadyError,
    PLACEHOLDER_TOKEN,
    assert_harmonization_prereg_ready_for_scoring,
    frozen_shoreline_reference,
    frozen_shoreline_reference_sha256,
    is_valid_frozen_shoreline_sha256,
    load_harmonization_prereg,
    run_harmonization_scoring,
)

REPO = Path(__file__).resolve().parents[2]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"
RESOLUTION_EXACT = "WCOFS coarsened to GLORYS grid, area-weighted, wet-masked"


WCOFS_GLORYS_OVERLAP_CONFIG = REPO / "data" / "config" / "wcofs_glorys_overlap.yaml"


def test_area_weighted_min_wet_fraction_matches_overlap_config_if_present() -> None:
    doc = load_harmonization_prereg(PREREG)
    prereg_min = doc["harmonization_wcofs_glorys"]["horizontal_processing"][
        "area_weighted_definition"
    ]["min_wet_fraction"]
    assert prereg_min == 0.5
    if not WCOFS_GLORYS_OVERLAP_CONFIG.is_file():
        pytest.skip(
            f"{WCOFS_GLORYS_OVERLAP_CONFIG} not present on this branch; "
            "cannot assert equality with regrid.min_wet_fraction"
        )
    cfg = yaml.safe_load(WCOFS_GLORYS_OVERLAP_CONFIG.read_text(encoding="utf-8"))
    cfg_min = cfg.get("regrid", {}).get("min_wet_fraction")
    assert cfg_min == prereg_min


def test_common_support_scoring_and_map_labels() -> None:
    doc = load_harmonization_prereg(PREREG)
    metrics = doc["harmonization_wcofs_glorys"]["metrics"]
    cs = metrics["common_support_scoring"]
    assert "every row has a finite model value" in cs["rule"]
    assert cs["dropped_observations"]["reason_label"] == "insufficient_model_coverage"
    assert "nearshore/offshore" in cs["dropped_observations"]["reporting"]
    assert "common-support" in cs["pass_fail_scope"]
    assert "same observation count n" in cs["test_requirement"]
    maps = doc["harmonization_wcofs_glorys"]["map_product_labeling"]
    assert maps["required_label"] == "egg encounter likelihood"
    assert "spawning locations" in maps["forbidden_labels"]


def test_buoy_matching_all_models_shared_depth() -> None:
    doc = load_harmonization_prereg(PREREG)
    ndbc = doc["harmonization_wcofs_glorys"]["observations"]["ndbc_hull_temperature"]
    bm = ndbc["buoy_matching"]
    assert bm["model_depth_m"] == 0.494
    assert len(bm["applies_to_model_rows"]) == 4
    assert "wcofs_native" in bm["applies_to_model_rows"]
    match = ndbc["match"]
    assert "wcofs_model_level" not in match
    assert match["spatial"] == "nearest_glorys_cell"


def test_wet_fraction_coverage_report_read_only() -> None:
    doc = load_harmonization_prereg(PREREG)
    wf = doc["harmonization_wcofs_glorys"]["wet_fraction_reporting"]
    assert wf["scope"] == "coarsened_wcofs_only"
    assert wf["read_only"] is True
    assert wf["coverage_report_path"] == (
        "artifacts/harmonization/wcofs_glorys_overlap/coverage_report.json"
    )
    field_ids = {f["id"] for f in wf["required_report_fields"]}
    assert "cufes_events_in_wcofs_nan_cells_full" in field_ids
    assert "do not change training exclusions" in wf["report_contents"]
    aw = doc["harmonization_wcofs_glorys"]["horizontal_processing"]["area_weighted_definition"]
    assert aw["applies_to"] == "coarsened_wcofs_only"
    assert "14,592" in aw["glorys_training_note"]


def test_ocean_data_missing_rows_never_zero() -> None:
    doc = load_harmonization_prereg(PREREG)
    rule = doc["harmonization_wcofs_glorys"]["ocean_data_missing_rows"]["rule"]
    assert "excluded = TRUE" in rule
    assert "never converted" in rule
    assert "bot5_sdmTMB" not in yaml.dump(doc)


def test_nowcast_insufficient_coverage_requirement() -> None:
    doc = load_harmonization_prereg(PREREG)
    nc = doc["harmonization_wcofs_glorys"]["nowcast_insufficient_coverage"]
    assert "evidence_state = UNKNOWN" in nc["render_rule"]
    assert nc["render_rule"].count("insufficient_model_coverage") >= 1
    assert "bot2/nowcast" in nc["test_requirement"]


def test_surface_definition_and_glorys_reference_dataset() -> None:
    doc = load_harmonization_prereg(PREREG)
    block = doc["harmonization_wcofs_glorys"]
    surf = block["surface_definition"]
    assert "zeta" in surf["vertical_reference"]
    assert surf["sst"]["target_depth_below_surface_m"] == 0.494
    glorys = block["glorys_reference_dataset"]
    assert glorys["selection_rule"] == "date_based_source_product_column"
    by_date = glorys["products_by_calendar_date"]
    assert by_date[0]["through_date"] == "2021-06-30"
    assert by_date[0]["copernicus_product_id"] == "cmems_mod_glo_phy_my_0.083deg_P1D-m"
    assert by_date[1]["from_date"] == "2021-07-01"
    assert by_date[1]["copernicus_product_id"] == "cmems_mod_glo_phy_myint_0.083deg_P1D-m"
    assert "scoring_nearshore_assignment" in block["nearshore"]


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
    with pytest.raises(HarmonizationPreregNotReadyError, match="shoreline_simplification_check"):
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
    ref = frozen_shoreline_reference(doc)
    assert ref["frozen"] is True
    assert ref["path"] == near["shoreline_path"]
    assert ref["pr7_source_commit"] == "8d4bfae"
    assert "Natural Earth 10 m land" in near["shoreline_simplification_note"]
    assert "0 GLORYS cells" in near["shoreline_simplification_note"]
    assert near["shoreline_simplification_check"] == PLACEHOLDER_TOKEN


def test_frozen_shoreline_reference_sha256_required_and_well_formed() -> None:
    doc = load_harmonization_prereg(PREREG)
    sha = frozen_shoreline_reference_sha256(doc)
    assert is_valid_frozen_shoreline_sha256(sha)
    assert sha == FROZEN_PILOT_SHORELINE_REFERENCE_SHA256
    assert sha.startswith("2f677a16") and sha.endswith("20996c")
    broken = yaml.safe_load(yaml.dump(doc))
    del broken["harmonization_wcofs_glorys"]["frozen_shoreline_reference"]["sha256"]
    with pytest.raises((KeyError, ValueError)):
        frozen_shoreline_reference_sha256(broken)
    broken2 = yaml.safe_load(yaml.dump(doc))
    broken2["harmonization_wcofs_glorys"]["frozen_shoreline_reference"]["sha256"] = "not-a-hash"
    with pytest.raises(ValueError, match="malformed"):
        frozen_shoreline_reference_sha256(broken2)


def test_scoring_entry_point_passes_gate_when_placeholders_replaced(tmp_path: Path) -> None:
    doc = load_harmonization_prereg(PREREG)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    block["nearshore"]["shoreline_simplification_check"] = {
        "max_coastline_displacement_m": 0.0,
        "nearshore_flag_diff_cell_count": 0,
    }
    patched = {"schema_version": 1, "harmonization_wcofs_glorys": block}
    path = tmp_path / "prereg.yaml"
    path.write_text(yaml.dump(patched), encoding="utf-8")
    assert_harmonization_prereg_ready_for_scoring(patched)
    with pytest.raises(NotImplementedError):
        run_harmonization_scoring(path)


def test_committed_prereg_still_has_expected_placeholders() -> None:
    doc = load_harmonization_prereg(PREREG)
    near = doc["harmonization_wcofs_glorys"]["nearshore"]
    assert near["shoreline_simplification_check"] == PLACEHOLDER_TOKEN
    assert "pass_fail_thresholds" not in doc["harmonization_wcofs_glorys"]


def test_nowcast_forcing_grading_blocks() -> None:
    doc = load_harmonization_prereg(PREREG)
    block = doc["harmonization_wcofs_glorys"]
    assert block["models_scored"]["graded_model_row_for_forcing_gate"] == "wcofs_coarsened_mapped"
    grading = block["nowcast_forcing_grading"]
    assert grading["graded_model_row"] == "wcofs_coarsened_mapped"
    assert grading["verdict_rank_worst_first"][0] == "UNKNOWN"
    buoy = grading["buoy_gate"]
    assert buoy["rmse_ratio_to_glorys"]["pass"]["ratio_max"] == 1.2
    assert buoy["fail_outcome"]["reason"] == "nowcast_forcing_failed_holdout"
    inputs = grading["graded_inputs_gate"]
    assert len(inputs["graded_variable_names"]) == 5
    assert inputs["rmse_vs_glorys_sd"]["pass_max_multiple"] == 0.5
    combo = grading["combination_rules"]
    assert combo["no_gradable_independent_check"]["reason"] == "no_independent_obs_check"
    maps = block["map_product_labeling"]
    assert "spawning habitat" in maps["forbidden_labels"]


def test_buoy_and_glider_forcing_gate_observations() -> None:
    doc = load_harmonization_prereg(PREREG)
    obs = doc["harmonization_wcofs_glorys"]["observations"]
    gate = obs["ndbc_hull_temperature"]["forcing_gate"]
    assert gate["grades_model_row"] == "wcofs_coarsened_mapped"
    assert gate["gradability"]["min_matched_daily_values"] == 100
    radar = obs["sccoos_hf_radar"]
    assert radar["forcing_gate_role"] == "report_only"
    gliders = obs["scripps_spray_gliders"]
    assert {d["id"] for d in gliders["datasets"]} == {"binnedCUGN80", "binnedCUGN90"}
    assert gliders["forcing_gate"]["never_grades_model_rows"] == ["glorys"]
    assert gliders["mld_definition"]["function"] == "mld"


def test_upwelling_lags_and_shared_forcing_variable() -> None:
    doc = load_harmonization_prereg(PREREG)
    lags = doc["harmonization_wcofs_glorys"]["upwelling_lags"]
    days = [c["trailing_mean_days"] for c in lags["candidates"]]
    assert days == [0, 7, 14, 28]
    assert lags["selection"]["fit_split_end"] == "2017-12-31"
    assert lags["selection"]["never_reselect_after_freeze"] is True
    vars_by_name = {v["name"]: v for v in doc["harmonization_wcofs_glorys"]["variables"]}
    assert vars_by_name["upwelling"]["role"] == "shared_forcing"
    assert vars_by_name["upwelling"]["blank_when"]["reason"] == "no_consistent_wind_product"
