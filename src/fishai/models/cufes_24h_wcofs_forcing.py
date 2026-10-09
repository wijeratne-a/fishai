"""24-hour WCOFS forecast forcing for CUFES egg-encounter holdout and grid maps."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd
import xarray as xr

from fishai.ingestion.physics.bathymetry import sample_wcofs_h_bottom_depth_m
from fishai.ingestion.physics.wcofs_h_glorys_store import load_wcofs_h_glorys_grid
from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.ingestion.physics.wcofs_glorys_grid import (
    compute_wcofs_covariates_on_glorys_grid,
    coarsen_wcofs_to_glorys,
    min_wet_fraction_from_config,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import depth_grid_m, load_overlap_config
from fishai.ingestion.physics.wcofs_pds_store import CycleNotAvailable, cycle_available, open_wcofs_cycle
from fishai.physics.store import CycleNotAvailable as StoreCycleNotAvailable

ForcingSource = Literal["wcofs_forecast", "proxy_fallback"]

# Public PDS fields archives used in PR #36 overlap work; egg scoring ends 2022-04-27.
WCOFS_FIELDS_EARLIEST = dt.date(2024, 7, 1)
HORIZON_24H_LEAD = "f024"
CUFES_TEST_END = dt.date(2022, 4, 27)

UPSTREAM_TO_MODEL = {
    "T3m": "temp_3m",
    "S3m": "sal_3m",
    "MLD_m": "mld",
    "sst_grad": "sst_grad",
    "front_distance_km": "dist_front",
}


@dataclass(frozen=True)
class ForcingResolution:
    source: ForcingSource
    reason: str
    cycle_date: dt.date | None = None
    lead_tag: str | None = None
    s3_key: str | None = None


def wcofs_fields_reachable(cycle_date: dt.date, *, lead: str = HORIZON_24H_LEAD) -> bool:
    """True when the public PDS exposes ``fields.{lead}`` for ``cycle_date``."""
    if cycle_date < WCOFS_FIELDS_EARLIEST:
        return False
    try:
        return cycle_available(cycle_date, lead=lead)
    except (CycleNotAvailable, OSError, RuntimeError):
        return False


def resolve_24h_forcing(cutoff_day: dt.date, event_day: dt.date) -> ForcingResolution:
    """
    Decide whether a holdout row can use issued WCOFS 24 h forecast forcing.

    Cutoff ``D`` with holdout on ``D+1`` uses cycle ``D`` lead ``f024`` (valid ≈ D+1 03Z).
    """
    horizon = (event_day - cutoff_day).days
    if horizon != 1:
        return ForcingResolution(
            source="proxy_fallback",
            reason=f"only_24h_horizon_supported_not_{horizon}d",
        )
    if event_day > CUFES_TEST_END:
        return ForcingResolution(
            source="proxy_fallback",
            reason="event_after_cufes_test_end",
        )
    if cutoff_day < WCOFS_FIELDS_EARLIEST:
        return ForcingResolution(
            source="proxy_fallback",
            reason="wcofs_fields_archive_starts_2024-07",
            cycle_date=cutoff_day,
            lead_tag=HORIZON_24H_LEAD,
        )
    if not wcofs_fields_reachable(cutoff_day):
        return ForcingResolution(
            source="proxy_fallback",
            reason="wcofs_fields_unreachable",
            cycle_date=cutoff_day,
            lead_tag=HORIZON_24H_LEAD,
        )
    return ForcingResolution(
        source="wcofs_forecast",
        reason="wcofs_fields_f024",
        cycle_date=cutoff_day,
        lead_tag=HORIZON_24H_LEAD,
    )


def open_wcofs_24h_forecast_fields(
    cutoff_day: dt.date,
    *,
    bbox: tuple[float, float, float, float] | None = None,
) -> xr.Dataset:
    """Load WCOFS ``fields.f024`` for cutoff-day cycle ``D`` (24 h lead from 03Z run)."""
    ds = open_wcofs_cycle(cutoff_day, product="fields", lead=HORIZON_24H_LEAD)
    if bbox is not None:
        ds = wcofs_src.subset_bbox(ds, bbox)
    return ds


def wcofs_covariates_on_target_grid(
    ds_wcofs: xr.Dataset,
    *,
    config: dict[str, Any] | None = None,
    lat_dst: np.ndarray | None = None,
    lon_dst: np.ndarray | None = None,
) -> tuple[xr.Dataset, dict[str, Any]]:
    cfg = config or load_overlap_config()
    if lat_dst is None or lon_dst is None:
        bbox = cfg["pilot_bbox"]
        lat_dst, lon_dst = glorys_target_grid(
            float(bbox["lat_min"]),
            float(bbox["lat_max"]),
            float(bbox["lon_min"]),
            float(bbox["lon_max"]),
        )
    depth = depth_grid_m(cfg)
    min_wf = min_wet_fraction_from_config(cfg)
    gridded = coarsen_wcofs_to_glorys(
        ds_wcofs,
        lat_dst,
        lon_dst,
        depth,
        min_wet_fraction=min_wf,
    )
    fields = compute_wcofs_covariates_on_glorys_grid(gridded)
    ds = xr.Dataset(
        {name: (("lat", "lon"), arr) for name, arr in fields.items()},
        coords={"lat": gridded.lat, "lon": gridded.lon},
    )
    meta = {
        "wcofs_s3_key": ds_wcofs.attrs.get("wcofs_s3_key"),
        "cycle": ds_wcofs.attrs.get("cycle"),
        "lead_tag": HORIZON_24H_LEAD,
        "min_wet_fraction": min_wf,
    }
    return ds, meta


def _nearest_grid_value(ds: xr.Dataset, var: str, lat: float, lon: float) -> float:
    if var not in ds:
        return float("nan")
    da = ds[var]
    j = int(np.argmin(np.abs(da["lat"].values - lat)))
    i = int(np.argmin(np.abs(da["lon"].values - lon)))
    if abs(float(da["lat"].values[j]) - lat) > 0.2 or abs(float(da["lon"].values[i]) - lon) > 0.2:
        return float("nan")
    val = float(da.values[j, i])
    return val


def sample_event_forcing_from_wcofs(
    ds_wcofs: xr.Dataset,
    *,
    lat: float,
    lon: float,
    log_depth: float | None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Sample model covariate slugs at one point after coarsening WCOFS to the GLORYS grid."""
    grid_ds, meta = wcofs_covariates_on_target_grid(ds_wcofs, config=config)
    row: dict[str, Any] = {"forcing_source": "wcofs_forecast", **meta}
    for upstream, slug in UPSTREAM_TO_MODEL.items():
        row[slug] = _nearest_grid_value(grid_ds, upstream, lat, lon)
    if log_depth is not None and np.isfinite(log_depth):
        row["log_depth"] = float(log_depth)
    else:
        cfg = config or load_overlap_config()
        min_wf = min_wet_fraction_from_config(cfg)
        hgrid = load_wcofs_h_glorys_grid()
        depth_m, _reason = sample_wcofs_h_bottom_depth_m(
            lat,
            lon,
            hgrid.h_m,
            hgrid.lat,
            hgrid.lon,
            has_source=hgrid.has_source,
            wet_fraction=hgrid.wet_fraction,
            min_wet_fraction=min_wf,
        )
        if np.isfinite(depth_m) and depth_m > 0:
            row["log_depth"] = float(np.log(depth_m))
        else:
            row["log_depth"] = float("nan")
    return row


def build_holdout_forcing_table(
    holdout: pd.DataFrame,
    cutoff_day: dt.date,
    *,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Build per-row forcing metadata and optional WCOFS covariates for 24 h holdout events.

    ``holdout`` must include ``event_id``, ``event_day`` (or infer from ``time_idx``),
    ``start_lat``/``start_lon`` or ``lat``/``lon``, and optional ``log_depth``.
    """
    cfg = config or load_overlap_config()
    rows: list[dict[str, Any]] = []
    resolution_counts: dict[str, int] = {"wcofs_forecast": 0, "proxy_fallback": 0}
    ds_wcofs: xr.Dataset | None = None
    for rec in holdout.to_dict(orient="records"):
        event_day = rec.get("event_day")
        if event_day is None:
            raise ValueError("holdout rows require event_day")
        if not isinstance(event_day, dt.date):
            event_day = pd.Timestamp(event_day).date()
        lat = rec.get("start_lat", rec.get("lat"))
        lon = rec.get("start_lon", rec.get("lon"))
        if lat is None or lon is None:
            raise ValueError("holdout rows require lat/lon")
        res = resolve_24h_forcing(cutoff_day, event_day)
        resolution_counts[res.source] += 1
        base = {
            "event_id": rec["event_id"],
            "cutoff_day": cutoff_day.isoformat(),
            "event_day": event_day.isoformat(),
            "horizon_hours": 24,
            "forcing_source": res.source,
            "forcing_reason": res.reason,
            "wcofs_cycle_date": res.cycle_date.isoformat() if res.cycle_date else None,
            "wcofs_lead_tag": res.lead_tag,
        }
        if res.source == "wcofs_forecast":
            if ds_wcofs is None:
                try:
                    ds_wcofs = open_wcofs_24h_forecast_fields(cutoff_day)
                except (CycleNotAvailable, StoreCycleNotAvailable, OSError) as exc:
                    res = ForcingResolution(
                        source="proxy_fallback",
                        reason=f"wcofs_open_failed:{exc}",
                        cycle_date=cutoff_day,
                        lead_tag=HORIZON_24H_LEAD,
                    )
                    base["forcing_source"] = res.source
                    base["forcing_reason"] = res.reason
                else:
                    base["wcofs_s3_key"] = ds_wcofs.attrs.get("wcofs_s3_key")
            if ds_wcofs is not None and base["forcing_source"] == "wcofs_forecast":
                sampled = sample_event_forcing_from_wcofs(
                    ds_wcofs,
                    lat=float(lat),
                    lon=float(lon),
                    log_depth=rec.get("log_depth"),
                    config=cfg,
                )
                base.update({k: sampled.get(k) for k in list(UPSTREAM_TO_MODEL.values()) + ["log_depth"]})
                base["wcofs_s3_key"] = sampled.get("wcofs_s3_key")
        rows.append(base)
    out = pd.DataFrame(rows)
    out.attrs["resolution_counts"] = resolution_counts
    return out


def pooled_forcing_label(cutoff_days: list[dt.date]) -> ForcingSource:
    """Aggregate label for a validation run (all cutoffs must agree for wcofs_forecast)."""
    labels = {resolve_24h_forcing(d, d + dt.timedelta(days=1)).source for d in cutoff_days}
    if labels == {"wcofs_forecast"}:
        return "wcofs_forecast"
    return "proxy_fallback"
