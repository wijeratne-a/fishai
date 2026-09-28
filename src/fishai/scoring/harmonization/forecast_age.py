"""Forecast-age grouping for holdout scores (never ``valid_offset_h``)."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

NOWCAST_GROUP = "nowcast"
FORBIDDEN_GROUP_COLUMNS = frozenset({"valid_offset_h"})


def lead_days_from_forecast_age_hours(forecast_age_hours: float) -> int:
    """``ceil(forecast_age_hours / 24)`` capped to 1–3 for lead groups."""
    days = int(math.ceil(float(forecast_age_hours) / 24.0))
    return max(1, min(3, days))


def is_nowcast_group(forecast_age_hours: float, fallback_used: bool) -> bool:
    return float(forecast_age_hours) <= 0.0 and not bool(fallback_used)


def forecast_group_label(forecast_age_hours: float, fallback_used: bool) -> str:
    if is_nowcast_group(forecast_age_hours, fallback_used):
        return NOWCAST_GROUP
    return f"lead_days_{lead_days_from_forecast_age_hours(forecast_age_hours)}"


def assert_pairing_uses_ocean_time_only(df: pd.DataFrame) -> None:
    if "ocean_time" not in df.columns:
        raise ValueError("pairing table requires ocean_time for WCOFS–observation pairing")
    if "valid_time" in df.columns and df["valid_time"].notna().any():
        raise ValueError("pairing must use ocean_time only, not valid_time")


def assert_not_grouped_by_valid_offset_h(group_keys: tuple[str, ...]) -> None:
    forbidden = FORBIDDEN_GROUP_COLUMNS.intersection(group_keys)
    if forbidden:
        raise ValueError(f"scores must not group by {sorted(forbidden)}")


def enrich_pairing_forecast_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ``forecast_group``, ``lead_days``, and metadata columns for scoring.

    ``forecast_age_hours`` is derived from ``ocean_time`` − ``source_run_time``.
    """
    from fishai.scoring.harmonization.wcofs_ocean_time import attach_forecast_age_from_ocean_time

    assert_pairing_uses_ocean_time_only(df)
    assert_not_grouped_by_valid_offset_h(tuple(df.columns))
    out = attach_forecast_age_from_ocean_time(df)
    ages = out["forecast_age_hours"].astype(float)
    fallback = out["fallback_used"].astype(bool)
    out["forecast_group"] = [
        forecast_group_label(float(a), bool(f))
        for a, f in zip(ages, fallback, strict=True)
    ]
    out["lead_days"] = [
        None if is_nowcast_group(float(a), bool(f)) else lead_days_from_forecast_age_hours(float(a))
        for a, f in zip(ages, fallback, strict=True)
    ]
    return out


def split_nowcast_and_forecast_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Nowcast rows for scored forcing; forecast steps listed separately."""
    if "forecast_group" not in df.columns:
        df = enrich_pairing_forecast_metadata(df)
    nowcast_mask = df["forecast_group"] == NOWCAST_GROUP
    return df.loc[nowcast_mask].copy(), df.loc[~nowcast_mask].copy()


def grouping_keys_for_scores() -> tuple[str, ...]:
    """Stable score aggregation keys (forecast age, not valid_offset_h)."""
    keys = ("forecast_group", "lead_days")
    assert_not_grouped_by_valid_offset_h(keys)
    return keys
