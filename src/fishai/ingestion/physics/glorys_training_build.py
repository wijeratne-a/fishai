"""Fail-closed GLORYS training table build (no synthetic covariates in production)."""

from __future__ import annotations

import datetime as dt
from typing import Any

# Covariate values stamped with Copernicus / GLORYS parquet metadata must use this source only.
GLORYS_COVARIATE_SOURCE_COPERNICUS = "copernicus_marine"
SYNTHETIC_TEST_FIXTURE_SOURCE = "synthetic_test_fixture"

REASON_CREDENTIALS_MISSING = "glorys_credentials_missing"
REASON_DATASET_NOT_IN_CATALOG = "glorys_dataset_not_in_catalog"
REASON_DOWNLOAD_FAILED = "glorys_download_failed"
REASON_DATE_NOT_COVERED = "glorys_date_not_covered"
REASON_SYNTHETIC_PROVENANCE_FORBIDDEN = "glorys_synthetic_provenance_forbidden"
REASON_WCOFS_BATHYMETRY_ARTIFACT_MISSING = "wcofs_bathymetry_artifact_missing"
REASON_WCOFS_BATHYMETRY_PLACEHOLDER = "wcofs_bathymetry_placeholder_forbidden"

COPERNICUS_ENV_VAR_NAMES: tuple[str, ...] = (
    "COPERNICUSMARINE_SERVICE_USERNAME",
    "COPERNICUSMARINE_SERVICE_PASSWORD",
    "COPERNICUSMARINE_USERNAME",
    "COPERNICUSMARINE_PASSWORD",
    "CMEMS_USERNAME",
    "CMEMS_PASSWORD",
)


class GlorysTrainingBuildError(RuntimeError):
    """Production build aborted; no training table must be written."""

    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        super().__init__(f"{reason_code}: {message}")


def assert_copernicus_env_credentials() -> None:
    import os

    user = os.environ.get("COPERNICUSMARINE_SERVICE_USERNAME")
    password = os.environ.get("COPERNICUSMARINE_SERVICE_PASSWORD")
    if not user or not password:
        raise GlorysTrainingBuildError(
            REASON_CREDENTIALS_MISSING,
            "set COPERNICUSMARINE_SERVICE_USERNAME and COPERNICUSMARINE_SERVICE_PASSWORD "
            "(never commit credential files)",
        )


def classify_copernicus_subset_error(exc: BaseException) -> str:
    """Map toolbox / HTTP failures to stable reason codes (no secrets in messages)."""
    text = str(exc).lower()
    if "not found" in text or "not in catalog" in text:
        return REASON_DATASET_NOT_IN_CATALOG
    if "401" in text or "403" in text or "unauthorized" in text or "credential" in text:
        return REASON_CREDENTIALS_MISSING
    return REASON_DOWNLOAD_FAILED


def assert_store_ready_for_copernicus_export(store: Any, days: list[dt.date]) -> None:
    source = getattr(store, "covariate_data_source", "")
    if source != GLORYS_COVARIATE_SOURCE_COPERNICUS:
        raise GlorysTrainingBuildError(
            REASON_SYNTHETIC_PROVENANCE_FORBIDDEN,
            "covariate_data_source must be copernicus_marine before writing GLORYS attribution",
        )
    day_map = getattr(store, "days", {})
    missing = sorted(d for d in days if d not in day_map)
    if missing:
        raise GlorysTrainingBuildError(
            REASON_DATE_NOT_COVERED,
            f"missing GLORYS fields for {len(missing)} event day(s), e.g. {missing[0].isoformat()}",
        )


def is_allowed_wcofs_hmin_source(hmin_source: str) -> bool:
    """True when ``hmin_source`` came from a real WCOFS ROMS export (not a placeholder)."""
    if not hmin_source or not str(hmin_source).strip():
        return False
    lowered = hmin_source.lower()
    if "placeholder" in lowered or "synthetic" in lowered or "fixture" in lowered:
        return False
    return (
        hmin_source.startswith("netcdf_global_attr_")
        or hmin_source.startswith("netcdf_variable_")
        or hmin_source == "wet_cell_minimum_h"
    )


def assert_wcofs_bathymetry_hmin_source(hmin_source: str) -> None:
    if not is_allowed_wcofs_hmin_source(hmin_source):
        raise GlorysTrainingBuildError(
            REASON_WCOFS_BATHYMETRY_PLACEHOLDER,
            f"refusing WCOFS bathymetry with hmin_source={hmin_source!r}",
        )


def assert_wcofs_bathymetry_store(store: Any) -> None:
    assert_wcofs_bathymetry_hmin_source(str(getattr(store, "hmin_source", "")))


def assert_may_write_glorys_training_parquet(store: Any | None) -> None:
    if store is None:
        raise GlorysTrainingBuildError(
            REASON_SYNTHETIC_PROVENANCE_FORBIDDEN,
            "GlorysFieldStore is required to write Copernicus-attributed training parquet",
        )
    source = getattr(store, "covariate_data_source", "")
    if source == SYNTHETIC_TEST_FIXTURE_SOURCE:
        raise GlorysTrainingBuildError(
            REASON_SYNTHETIC_PROVENANCE_FORBIDDEN,
            "synthetic_test_fixture cannot be written with GLORYS/Copernicus metadata",
        )
    if source != GLORYS_COVARIATE_SOURCE_COPERNICUS:
        raise GlorysTrainingBuildError(
            REASON_SYNTHETIC_PROVENANCE_FORBIDDEN,
            f"refusing GLORYS attribution for covariate_data_source={source!r}",
        )
    assert_wcofs_bathymetry_store(store)
