"""CUFES event covariate contract and join to bot1 ``cufes_events`` tables."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

# Training / hindcast covariates at CUFES event locations (egg-stage model).
CUFES_COVARIATE_FIELDS: tuple[str, ...] = (
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
    "upwelling",
)

REQUIRED_EVENT_COLUMNS: tuple[str, ...] = ("event_id", "time", "latitude", "longitude")

# Stored for diagnostics and alternate models but excluded from the CUFES covariate vector.
FEATURE_STORE_EXTRA_FIELDS: tuple[str, ...] = (
    "bottomT",
    "mlotst_crosscheck",
)

MLD_COVARIATE_SOURCE = "computed_temperature_threshold"
MLDST_FIELD_ROLE = "cross_check_only"


class CufesEventValidationError(ValueError):
    """Invalid ``cufes_events`` input for physics covariate join."""


def validate_cufes_events(events: pd.DataFrame) -> None:
    """Require unique, non-null ``event_id`` and required columns (ids are verbatim from bot1)."""
    missing_cols = [c for c in REQUIRED_EVENT_COLUMNS if c not in events.columns]
    if missing_cols:
        raise CufesEventValidationError(f"missing columns: {missing_cols}")
    if events["event_id"].isna().any():
        raise CufesEventValidationError("event_id must not be null")
    if events["event_id"].astype(str).str.strip().eq("").any():
        raise CufesEventValidationError("event_id must not be empty")
    if events["event_id"].duplicated().any():
        dupes = events.loc[events["event_id"].duplicated(), "event_id"].tolist()
        raise CufesEventValidationError(f"duplicate event_id values: {dupes[:5]}")


def missing_covariate_counts(covariates: pd.DataFrame) -> dict[str, int]:
    """Per-column NaN counts for QC (no imputation)."""
    counts: dict[str, int] = {}
    for col in CUFES_COVARIATE_FIELDS:
        if col in covariates.columns:
            counts[col] = int(covariates[col].isna().sum())
    return counts


def join_covariates_to_events(
    events: pd.DataFrame,
    *,
    sampler: Callable[[pd.Series], dict[str, Any]],
    source: str,
    provenance: str = "",
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Build one covariate row per input ``event_id`` (only join key).

    ``sampler`` returns covariate values for a single event row; missing values
    stay NaN (never imputed). Output order matches input ``events`` row order.
    """
    validate_cufes_events(events)
    rows: list[dict[str, Any]] = []
    for _, event in events.iterrows():
        sampled = sampler(event)
        row: dict[str, Any] = {"event_id": event["event_id"]}
        for field in CUFES_COVARIATE_FIELDS:
            val = sampled.get(field, np.nan)
            row[field] = np.nan if val is None else val
        row["source"] = source
        row["provenance"] = provenance
        rows.append(row)
    out = pd.DataFrame(rows)
    if len(out) != len(events):
        raise CufesEventValidationError("output row count must equal input event count")
    if out["event_id"].tolist() != events["event_id"].tolist():
        raise CufesEventValidationError("output event_id order must match input")
    if set(out["event_id"]) != set(events["event_id"]):
        raise CufesEventValidationError("output event_id set must equal input")
    qc = missing_covariate_counts(out)
    return out, qc
