"""CUFES covariate contract."""

from __future__ import annotations

from fishai.ingestion.physics.covariates import (
    CUFES_COVARIATE_FIELDS,
    FEATURE_STORE_EXTRA_FIELDS,
    MLDST_FIELD_ROLE,
    COL_START_LAT,
    REQUIRED_EVENT_COLUMNS,
)


def test_required_event_columns_for_join() -> None:
    assert "event_id" in REQUIRED_EVENT_COLUMNS
    assert COL_START_LAT in REQUIRED_EVENT_COLUMNS
    assert "sample_id" not in REQUIRED_EVENT_COLUMNS


def test_cufes_covariates_exclude_bottom_t_and_mlotst() -> None:
    assert "T3m" in CUFES_COVARIATE_FIELDS
    assert "bottomT" not in CUFES_COVARIATE_FIELDS
    assert "mlotst" not in CUFES_COVARIATE_FIELDS
    assert "bottomT" in FEATURE_STORE_EXTRA_FIELDS
    assert MLDST_FIELD_ROLE == "cross_check_only"
