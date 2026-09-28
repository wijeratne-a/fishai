"""CUFES covariate contract."""

from __future__ import annotations

from fishai.ingestion.physics.covariates import (
    CUFES_COVARIATE_FIELDS,
    FEATURE_STORE_EXTRA_FIELDS,
    MLDST_FIELD_ROLE,
)


def test_cufes_covariates_exclude_bottom_t_and_mlotst() -> None:
    assert "T3m" in CUFES_COVARIATE_FIELDS
    assert "bottomT" not in CUFES_COVARIATE_FIELDS
    assert "mlotst" not in CUFES_COVARIATE_FIELDS
    assert "bottomT" in FEATURE_STORE_EXTRA_FIELDS
    assert MLDST_FIELD_ROLE == "cross_check_only"
