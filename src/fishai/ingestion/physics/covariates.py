"""CUFES model covariate contract vs broader feature-store fields."""

from __future__ import annotations

# Training / hindcast covariates sampled along CUFES tracks (egg-stage model).
CUFES_COVARIATE_FIELDS: tuple[str, ...] = (
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
    "upwelling",
)

# Stored for diagnostics and alternate models but excluded from the CUFES covariate vector.
FEATURE_STORE_EXTRA_FIELDS: tuple[str, ...] = (
    "bottomT",
    "mlotst_crosscheck",
)

# GLORYS native mixed-layer thickness is never a model covariate (cross-check only).
MLD_COVARIATE_SOURCE = "computed_temperature_threshold"
MLDST_FIELD_ROLE = "cross_check_only"
