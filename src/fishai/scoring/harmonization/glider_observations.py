"""Spray glider profile metrics for harmonization holdout (observation side)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

from fishai.ingestion.physics.vertical import MLD_NOT_REACHED, mld_from_profile
from fishai.ingestion.physics.wcofs_glorys_grid import (
    HARMONIZATION_GLIDER_PROXY_DEPTH_M,
    harmonization_tracer_at_depth_below_surface,
)

GLIDER_PROXY_LABEL = "proxy_for_3m"
DOXY_REPORTED_ONLY = "assimilated_reported_only"


def spray_profile_observation_rows(profiles: pd.DataFrame) -> pd.DataFrame:
    """
    One row per profile with MLD and 10 m T/S proxy (observation values only).

    Profiles with ``mld_not_reached`` are included with ``mld_m`` NaN and
    ``mld_exclude_reason`` set for counting.
    """
    rows: list[dict] = []
    for profile_id, grp in profiles.groupby("profile_id"):
        depth = grp["depth"].astype(float).values
        temp = grp["temperature_c"].astype(float).values
        salt = grp["salinity_psu"].astype(float).values if "salinity_psu" in grp else np.full_like(temp, np.nan)
        mld_m, mld_reason = mld_from_profile(depth, temp)
        t10 = harmonization_tracer_at_depth_below_surface(
            depth, temp, depth_m=HARMONIZATION_GLIDER_PROXY_DEPTH_M
        )
        s10 = harmonization_tracer_at_depth_below_surface(
            depth, salt, depth_m=HARMONIZATION_GLIDER_PROXY_DEPTH_M
        )
        doxy = float(np.nanmean(grp["doxy"])) if "doxy" in grp.columns else float("nan")
        day = pd.to_datetime(grp["time"].iloc[0]).date()
        rows.append(
            {
                "profile_id": profile_id,
                "mission": str(grp["mission"].iloc[0]),
                "date": day.isoformat(),
                "latitude": float(np.nanmean(grp["latitude"])),
                "longitude": float(np.nanmean(grp["longitude"])),
                "obs_mld_m": mld_m,
                "mld_exclude_reason": mld_reason,
                "obs_T3m_proxy": t10,
                "obs_S3m_proxy": s10,
                "obs_doxy": doxy,
                "T3m_label": GLIDER_PROXY_LABEL,
                "S3m_label": GLIDER_PROXY_LABEL,
            }
        )
    return pd.DataFrame(rows)
