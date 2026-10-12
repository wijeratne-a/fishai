"""Physics event frames for adult CPS hauls and nearshore sets."""

from __future__ import annotations

from typing import Any

import pandas as pd

from fishai.ingestion.physics.covariates import (
    COL_EVENT_ID,
    COL_START_LAT,
    COL_START_LON,
    COL_START_TIME,
    COL_STOP_LAT,
    COL_STOP_LON,
    COL_STOP_TIME,
)


def _parse_time_series(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def trawl_hauls_to_physics_events(hauls: pd.DataFrame) -> pd.DataFrame:
    """Map ``cps_trawl_hauls.parquet`` rows to the CUFES physics join contract."""
    if hauls.empty:
        return pd.DataFrame(
            columns=[
                COL_EVENT_ID,
                COL_START_TIME,
                COL_STOP_TIME,
                COL_START_LAT,
                COL_START_LON,
                COL_STOP_LAT,
                COL_STOP_LON,
                "observation_source",
                "effort_duration_min",
            ]
        )
    out = pd.DataFrame(
        {
            COL_EVENT_ID: hauls["haul_id"].astype(str),
            COL_START_TIME: _parse_time_series(hauls["time"]),
            COL_STOP_TIME: _parse_time_series(hauls["haulback_time"]),
            COL_START_LAT: hauls["lat"].astype(float),
            COL_START_LON: hauls["lon"].astype(float),
            COL_STOP_LAT: hauls["stop_lat"].astype(float),
            COL_STOP_LON: hauls["stop_lon"].astype(float),
            "observation_source": "swfsc_cps_trawl_haul_catch",
            "effort_duration_min": hauls["tow_duration_min"].astype(float),
        }
    )
    return out


def nearshore_sets_to_physics_events(sets: pd.DataFrame) -> pd.DataFrame:
    """Map nearshore set rows to physics events (point: start equals stop)."""
    if sets.empty:
        return pd.DataFrame(
            columns=[
                COL_EVENT_ID,
                COL_START_TIME,
                COL_STOP_TIME,
                COL_START_LAT,
                COL_START_LON,
                COL_STOP_LAT,
                COL_STOP_LON,
                "observation_source",
                "effort_duration_min",
                "effort_duration_null_reason",
            ]
        )
    when = _parse_time_series(sets["time_utc"])
    out = pd.DataFrame(
        {
            COL_EVENT_ID: sets["set_id"].astype(str),
            COL_START_TIME: when,
            COL_STOP_TIME: when,
            COL_START_LAT: sets["latitude"].astype(float),
            COL_START_LON: sets["longitude"].astype(float),
            COL_STOP_LAT: sets["latitude"].astype(float),
            COL_STOP_LON: sets["longitude"].astype(float),
            "observation_source": "swfsc_cps_nearshore_set_catch",
            "effort_duration_min": sets.get("effort_duration_min"),
            "effort_duration_null_reason": sets.get("effort_duration_null_reason"),
        }
    )
    return out


def merge_adult_physics_events(trawl: pd.DataFrame, nearshore: pd.DataFrame) -> pd.DataFrame:
    """One row per ``event_id`` across trawl hauls and nearshore sets."""
    frames = [df for df in (trawl, nearshore) if not df.empty]
    if not frames:
        return trawl_hauls_to_physics_events(pd.DataFrame())
    out = pd.concat(frames, ignore_index=True)
    if out[COL_EVENT_ID].duplicated().any():
        dupes = out.loc[out[COL_EVENT_ID].duplicated(), COL_EVENT_ID].tolist()
        raise ValueError(f"duplicate adult event_id values: {dupes[:5]}")
    return out


def event_midpoint_in_pilot_bbox(
    event: pd.Series,
    *,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
) -> bool:
    lat = (float(event[COL_START_LAT]) + float(event[COL_STOP_LAT])) / 2.0
    lon = (float(event[COL_START_LON]) + float(event[COL_STOP_LON])) / 2.0
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


def filter_events_to_pilot_bbox(
    events: pd.DataFrame,
    *,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (kept events, dropped event_id rows with reason)."""
    if events.empty:
        return events, pd.DataFrame(columns=["event_id", "reason"])
    keep_mask = events.apply(
        event_midpoint_in_pilot_bbox,
        axis=1,
        lat_min=lat_min,
        lat_max=lat_max,
        lon_min=lon_min,
        lon_max=lon_max,
    )
    dropped = events.loc[~keep_mask, [COL_EVENT_ID]].rename(columns={COL_EVENT_ID: "event_id"})
    dropped["reason"] = "outside_pilot_bbox"
    return events.loc[keep_mask].reset_index(drop=True), dropped
