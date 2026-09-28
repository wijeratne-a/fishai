"""
Pair WCOFS daily ``avg.nowcast`` with GLORYS daily means on the pilot overlap window.

Network downloads are orchestrated here but never run in CI (inject ``fetch_*`` mocks).
"""

from __future__ import annotations

import datetime as dt
import json
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
import xarray as xr

from fishai.ingestion.copernicus_compliance import append_pull_log, build_pull_record
from fishai.ingestion.physics.coast_distance import distance_to_coast_km
from fishai.ingestion.physics.features import front_distance_km, sst_gradient
from fishai.ingestion.physics.harmonize import area_weighted_regrid, glorys_target_grid
from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID,
    glorys_column_features,
)
from fishai.ingestion.physics.vertical import (
    interp_at_depth_from_z_levels,
    mld,
    s_to_z,
)
from fishai.ingestion.physics.wcofs_pull_log import append_wcofs_pull_log, build_wcofs_pull_record
from fishai.ingestion.physics.wcofs_pds_store import open_wcofs_cycle
from fishai.ingestion.sources import REPO_ROOT, attribution_for

DEFAULT_CONFIG = REPO_ROOT / "data" / "config" / "wcofs_glorys_overlap.yaml"


class DailyRequestBudgetExceeded(RuntimeError):
    """Raised when the configured daily HTTP request cap is exceeded."""


class _DailyRequestBudget:
    def __init__(self, max_per_day: int) -> None:
        self._max = int(max_per_day)
        self._day: dt.date | None = None
        self._count = 0

    def charge(self, when: dt.date | None = None, n: int = 1) -> None:
        today = when or dt.date.today()
        if self._day != today:
            self._day = today
            self._count = 0
        self._count += int(n)
        if self._count > self._max:
            raise DailyRequestBudgetExceeded(f"exceeded {self._max} requests on {today}")


def load_overlap_config(path: Path | str | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path is not None else DEFAULT_CONFIG
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


def overlap_dates(config: dict[str, Any]) -> list[dt.date]:
    start = dt.date.fromisoformat(str(config["overlap"]["start"]))
    end = dt.date.fromisoformat(str(config["overlap"]["end"]))
    days: list[dt.date] = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += dt.timedelta(days=1)
    return days


def split_label(day: dt.date, config: dict[str, Any]) -> str:
    fit_end = dt.date.fromisoformat(str(config["split"]["fit_end"]))
    test_start = dt.date.fromisoformat(str(config["split"]["test_start"]))
    if day <= fit_end:
        return "fit"
    if day >= test_start:
        return "test"
    return "holdout"


def meteorological_season(day: dt.date) -> str:
    month = day.month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


def depth_grid_m(config: dict[str, Any]) -> np.ndarray:
    spec = config["depth_grid_m"]
    start = int(spec["start"])
    end = int(spec["end"])
    step = int(spec["step"])
    return np.arange(start, end + step, step, dtype=float)


def _surface_slab(ds: xr.Dataset) -> xr.Dataset:
    return ds.isel(ocean_time=0) if "ocean_time" in ds.dims else ds


def wcofs_profiles_positive_down(
    slab: xr.Dataset,
    depth_grid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (depth_grid, temp_profile, salt_profile) on ``depth_grid`` (1d)."""
    ref = _surface_slab(slab)
    h = ref.h.values
    zeta = ref.zeta.values
    temp = ref.temp.values
    salt = ref.salt.values
    if temp.ndim == 4:
        temp = temp[0]
        salt = salt[0]
    s_rho = ref.s_rho.values
    hc = float(ref.hc.values)
    cs_r = ref.Cs_r.values if "Cs_r" in ref else None
    z_roms = s_to_z(h, zeta, s_rho, hc, cs_r=cs_r)
    depth = -z_roms
    ny, nx, nz = depth.shape[1], depth.shape[2], depth.shape[0]
    temp_out = np.full((ny, nx, depth_grid.size), np.nan)
    salt_out = np.full((ny, nx, depth_grid.size), np.nan)
    for j in range(ny):
        for i in range(nx):
            dcol = depth[:, j, i]
            tcol = temp[:, j, i]
            scol = salt[:, j, i]
            order = np.argsort(dcol)
            d_sorted = dcol[order]
            t_sorted = tcol[order]
            s_sorted = scol[order]
            temp_out[j, i, :] = np.interp(depth_grid, d_sorted, t_sorted, left=np.nan, right=np.nan)
            salt_out[j, i, :] = np.interp(depth_grid, d_sorted, s_sorted, left=np.nan, right=np.nan)
    return depth_grid, temp_out, salt_out


def wcofs_column_metrics(
    depth_grid: np.ndarray,
    temp_profile: np.ndarray,
    salt_profile: np.ndarray,
) -> dict[str, float]:
    z3d = (-depth_grid)[:, None, None]
    t3d = temp_profile[:, None, None]
    mld_m = float(mld(z3d, t3d)[0, 0])
    return {
        "wcofs_T3m": interp_at_depth_from_z_levels(depth_grid, temp_profile, 3.0),
        "wcofs_S3m": interp_at_depth_from_z_levels(depth_grid, salt_profile, 3.0),
        "wcofs_MLD_m": mld_m,
    }


def glorys_profiles_on_depth_grid(
    z_levels: np.ndarray,
    temp: np.ndarray,
    salt: np.ndarray,
    depth_grid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(z_levels)
    z_sorted = z_levels[order]
    t_sorted = temp[order]
    s_sorted = salt[order]
    return (
        np.interp(depth_grid, z_sorted, t_sorted, left=np.nan, right=np.nan),
        np.interp(depth_grid, z_sorted, s_sorted, left=np.nan, right=np.nan),
    )


def coarsen_wcofs_surface_fields(
    slab: xr.Dataset,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
) -> dict[str, np.ndarray]:
    ref = _surface_slab(slab)
    lat = ref.lat_rho.values
    lon = ref.lon_rho.values
    lon = np.where(lon > 180, lon - 360, lon)
    wet = ref.mask_rho.values == 1
    temp_da = ref.temp
    if "ocean_time" in temp_da.dims:
        temp_da = temp_da.isel(ocean_time=0)
    sst = temp_da.isel(s_rho=-1).values
    sst_coarse = area_weighted_regrid(sst, lat, lon, lat_dst, lon_dst, wet_mask=wet)
    grad = sst_gradient(sst_coarse, lat_dst, lon_dst)
    lat2d, lon2d = np.meshgrid(lat_dst, lon_dst, indexing="ij")
    front_km = front_distance_km(grad, lat2d, lon2d)
    return {"wcofs_sst_grad": grad, "wcofs_front_distance_km": front_km}


def pair_day_cell(
    day: dt.date,
    j: int,
    i: int,
    lat: float,
    lon: float,
    wcofs_metrics: dict[str, float],
    glorys_metrics: dict[str, float],
    wcofs_surface: dict[str, float],
    glorys_surface: dict[str, float],
    *,
    config: dict[str, Any],
    nearshore: bool,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "day": day.isoformat(),
        "glorys_j": j,
        "glorys_i": i,
        "lat": lat,
        "lon": lon,
        "split": split_label(day, config),
        "season": meteorological_season(day),
        "nearshore": bool(nearshore),
        **wcofs_metrics,
        **glorys_metrics,
        **wcofs_surface,
        **glorys_surface,
    }
    return row


def build_overlap_metadata(config: dict[str, Any]) -> dict[str, Any]:
    glorys_cfg = config["glorys"]
    return {
        "schema_version": "wcofs_glorys_overlap_v1",
        "overlap_start": config["overlap"]["start"],
        "overlap_end": config["overlap"]["end"],
        "expected_days": int(config["overlap"]["expected_days"]),
        "glorys_product_id": glorys_cfg["product_id"],
        "glorys_production_status": glorys_cfg["production_status"],
        "glorys_copernicus_doi": glorys_cfg["copernicus_doi"],
        "wcofs_attribution": attribution_for("wcofs"),
        "glorys_attribution": attribution_for("glorys"),
    }


def write_overlap_parquet(df: pd.DataFrame, path: Path, metadata: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    meta_json = json.dumps(metadata, sort_keys=True)
    df.to_parquet(path, index=False, custom_metadata={"overlap": meta_json.encode()})
    return path


def _glorys_to_wcofs_indices(
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    lat_rho: np.ndarray,
    lon_rho: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    lon_rho = np.where(lon_rho > 180, lon_rho - 360, lon_rho)
    jj = np.zeros((lat_dst.size, lon_dst.size), dtype=int)
    ii = np.zeros((lat_dst.size, lon_dst.size), dtype=int)
    for j, la in enumerate(lat_dst):
        for i, lo in enumerate(lon_dst):
            flat = np.argmin((lat_rho - la) ** 2 + (lon_rho - lo) ** 2)
            jj[j, i], ii[j, i] = np.unravel_index(flat, lat_rho.shape)
    return jj, ii


def pair_overlap_from_synthetic(
    day: dt.date,
    wcofs_slab: xr.Dataset,
    glorys_thetao: np.ndarray,
    glorys_so: np.ndarray,
    z_levels: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Test helper: one day, full GLORYS subgrid."""
    config = config or load_overlap_config()
    depth_grid = depth_grid_m(config)
    _, temp_vol, salt_vol = wcofs_profiles_positive_down(wcofs_slab, depth_grid)
    ref = _surface_slab(wcofs_slab)
    w_jj, w_ii = _glorys_to_wcofs_indices(
        lat_dst, lon_dst, ref.lat_rho.values, ref.lon_rho.values
    )
    surface = coarsen_wcofs_surface_fields(wcofs_slab, lat_dst, lon_dst)
    coast_path = REPO_ROOT / str(config["coastline_fixture"])
    lat2d, lon2d = np.meshgrid(lat_dst, lon_dst, indexing="ij")
    coast_km = distance_to_coast_km(lat2d, lon2d, coastline_fixture=coast_path)
    nearshore = coast_km <= float(config["nearshore_km"])
    rows: list[dict[str, Any]] = []
    for j, la in enumerate(lat_dst):
        for i, lo in enumerate(lon_dst):
            wj, wi = int(w_jj[j, i]), int(w_ii[j, i])
            wcofs_metrics = wcofs_column_metrics(
                depth_grid, temp_vol[wj, wi, :], salt_vol[wj, wi, :]
            )
            g_temp, g_salt = glorys_profiles_on_depth_grid(
                z_levels, glorys_thetao[:, j, i], glorys_so[:, j, i], depth_grid
            )
            glorys_metrics = {
                f"glorys_{k}": v
                for k, v in glorys_column_features(z_levels, glorys_thetao[:, j, i], glorys_so[:, j, i], None).items()
                if k != "mlotst_crosscheck"
            }
            wcofs_surface = {
                "wcofs_sst_grad": float(surface["wcofs_sst_grad"][j, i]),
                "wcofs_front_distance_km": float(surface["wcofs_front_distance_km"][j, i]),
            }
            glorys_surface = {
                "glorys_sst_grad": float("nan"),
                "glorys_front_distance_km": float("nan"),
            }
            rows.append(
                pair_day_cell(
                    day,
                    j,
                    i,
                    float(la),
                    float(lo),
                    wcofs_metrics,
                    glorys_metrics,
                    wcofs_surface,
                    glorys_surface,
                    config=config,
                    nearshore=bool(nearshore[j, i]),
                )
            )
    return pd.DataFrame(rows)


def run_overlap_pairing(
    *,
    config: dict[str, Any] | None = None,
    days: Sequence[dt.date] | None = None,
    wcofs_open: Callable[[dt.date], xr.Dataset] | None = None,
    glorys_fetch: Callable[[dt.date], dict[str, Any]] | None = None,
    budget: _DailyRequestBudget | None = None,
    wcofs_log: Path | None = None,
    glorys_log: Path | None = None,
    output_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Build the overlap table (live downloads when ``wcofs_open`` / ``glorys_fetch`` omitted).

    GLORYS subsets must be requested server-side (Copernicus Marine toolbox); inject
    ``glorys_fetch`` in tests.
    """
    config = config or load_overlap_config()
    days = list(days) if days is not None else overlap_dates(config)
    expected = int(config["overlap"]["expected_days"])
    if days is not None and len(days) == expected and len(overlap_dates(config)) != expected:
        raise ValueError("configured overlap.expected_days does not match date span")
    bbox = config["pilot_bbox"]
    lat_dst, lon_dst = glorys_target_grid(
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )
    rate = config.get("rate_limits") or {}
    budget = budget or _DailyRequestBudget(int(rate.get("max_requests_per_day", 200)))
    wcofs_log = wcofs_log or REPO_ROOT / str(config["pull_logs"]["wcofs"])
    glorys_log = glorys_log or REPO_ROOT / str(config["pull_logs"]["glorys"])
    all_rows: list[dict[str, Any]] = []
    for day in days:
        if wcofs_open is None:
            budget.charge(day, 1)
            ds = open_wcofs_cycle(day, product="avg_nowcast")
        else:
            ds = wcofs_open(day)
        key = str(ds.attrs.get("wcofs_s3_key", ""))
        append_wcofs_pull_log(
            build_wcofs_pull_record(
                cycle_date=day.isoformat(),
                s3_key=key,
                attribution=attribution_for("wcofs"),
            ),
            log_path=wcofs_log,
        )
        if glorys_fetch is None:
            raise RuntimeError("glorys_fetch is required for live overlap pairing")
        budget.charge(day, 1)
        glorys_payload = glorys_fetch(day)
        append_pull_log(
            build_pull_record(
                dataset_id=PRODUCT_ID,
                date_start=day.isoformat(),
                date_end=day.isoformat(),
                variables=("thetao", "so"),
                bbox=(
                    float(bbox["lat_min"]),
                    float(bbox["lat_max"]),
                    float(bbox["lon_min"]),
                    float(bbox["lon_max"]),
                ),
            ),
            log_path=glorys_log,
        )
        frame = pair_overlap_from_synthetic(
            day,
            ds,
            glorys_payload["thetao"],
            glorys_payload["so"],
            glorys_payload["depth"],
            lat_dst,
            lon_dst,
            config=config,
        )
        all_rows.extend(frame.to_dict(orient="records"))
    df = pd.DataFrame(all_rows)
    metadata = build_overlap_metadata(config)
    metadata["glorys_production_status"] = str(config["glorys"]["production_status"])
    if output_path is not None:
        write_overlap_parquet(df, output_path, metadata)
    return df, metadata
