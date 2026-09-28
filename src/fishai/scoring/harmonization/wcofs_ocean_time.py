"""WCOFS valid time from NetCDF ``ocean_time`` only (never lead tokens or step math)."""

from __future__ import annotations

import pandas as pd

FORBIDDEN_VALID_TIME_SOURCES = frozenset(
    {
        "valid_time",
        "valid_offset_h",
    }
)


def forecast_age_hours_from_ocean_time(
    ocean_time: pd.Timestamp | str,
    source_run_time: pd.Timestamp | str,
) -> float:
    """Hours from WCOFS cycle issue to field valid time (``ocean_time`` − run time)."""
    ot = pd.to_datetime(ocean_time, utc=True)
    rt = pd.to_datetime(source_run_time, utc=True)
    return float((ot - rt).total_seconds() / 3600.0)


def attach_forecast_age_from_ocean_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Set ``forecast_age_hours`` from each row's ``ocean_time`` and ``source_run_time``.

    Pairing tables must carry both columns as read from WCOFS fields files (auditbot1:
    n003 at run−21 h, n024 at run, fNNN at run+NNN h).
    """
    if "ocean_time" not in df.columns:
        raise ValueError("pairing table requires ocean_time for WCOFS–observation pairing")
    if "source_run_time" not in df.columns:
        raise ValueError("pairing table requires source_run_time with ocean_time")
    for col in FORBIDDEN_VALID_TIME_SOURCES:
        if col in df.columns and df[col].notna().any():
            raise ValueError(f"pairing must not use {col} for valid time; use ocean_time only")
    out = df.copy()
    ot = pd.to_datetime(out["ocean_time"], utc=True)
    rt = pd.to_datetime(out["source_run_time"], utc=True)
    out["forecast_age_hours"] = (ot - rt).dt.total_seconds() / 3600.0
    return out


def observation_pairs_with_model_at_ocean_time(
    obs_ocean_time: pd.Timestamp | str,
    model_ocean_times: pd.Series,
) -> pd.Index:
    """Index of model rows whose ``ocean_time`` equals the observation valid time."""
    target = pd.to_datetime(obs_ocean_time, utc=True)
    times = pd.to_datetime(model_ocean_times, utc=True)
    return model_ocean_times.index[times == target]
