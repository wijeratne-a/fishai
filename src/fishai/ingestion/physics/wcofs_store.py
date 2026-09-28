"""Write canonical processed WCOFS Zarr cycles (ingestion only)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from fishai.ingestion.physics.vertical import (
    CUFES_SAMPLE_DEPTH_M,
    interp_at_depth_from_wcofs_column,
    mld,
    s_to_z,
)
from fishai.ingestion.sources import REPO_ROOT, attribution_for

DEFAULT_STORE_ROOT = REPO_ROOT / "data" / "processed" / "physics"


def cycle_zarr_path(cycle_date: dt.date, store_root: Path | None = None) -> Path:
    root = store_root or DEFAULT_STORE_ROOT
    return root / f"wcofs_{cycle_date:%Y%m%d}.zarr"


def package_wcofs_cycle(merged: xr.Dataset, cycle_date: dt.date) -> xr.Dataset:
    """Normalize ``fetch_cycle`` output to the processed-store schema (depth positive down)."""
    def _surface(da: xr.DataArray) -> xr.DataArray:
        return da.isel(ocean_time=0) if "ocean_time" in da.dims else da

    ref = merged.isel(lead_hours=0) if "lead_hours" in merged.dims else merged
    h = ref.h.values
    s_rho = ref.s_rho.values
    hc = float(ref.hc.values)
    cs_r = ref.Cs_r.values if "Cs_r" in ref else None
    wet = ref.mask_rho.values == 1
    lat = ref.lat_rho.values
    lon = ref.lon_rho.values
    lon = np.where(lon > 180, lon - 360, lon)

    lead_values = list(merged.lead_hours.values) if "lead_hours" in merged.dims else [0]
    temp_leads = []
    salt_leads = []
    z_leads = []
    t3m_leads = []
    s3m_leads = []
    mld_leads = []
    times = []
    for lh in lead_values:
        slab = merged.sel(lead_hours=lh) if "lead_hours" in merged.dims else merged
        zeta = _surface(slab.zeta).values
        temp = _surface(slab.temp).values
        salt = _surface(slab.salt).values
        z_roms = s_to_z(h, zeta, s_rho, hc, cs_r=cs_r)
        depth = -z_roms
        temp_leads.append(temp)
        salt_leads.append(salt)
        z_leads.append(depth)
        ny, nx = temp.shape[1], temp.shape[2]
        t3m = np.full((ny, nx), np.nan)
        s3m = np.full((ny, nx), np.nan)
        mld_m = np.where(wet, mld(z_roms, temp), np.nan)
        for j in range(ny):
            for i in range(nx):
                if not wet[j, i]:
                    continue
                t3m[j, i] = interp_at_depth_from_wcofs_column(
                    float(h[j, i]),
                    float(zeta[j, i]),
                    s_rho,
                    hc,
                    temp[:, j, i],
                    cs_r=cs_r,
                    depth_m=CUFES_SAMPLE_DEPTH_M,
                )
                s3m[j, i] = interp_at_depth_from_wcofs_column(
                    float(h[j, i]),
                    float(zeta[j, i]),
                    s_rho,
                    hc,
                    salt[:, j, i],
                    cs_r=cs_r,
                    depth_m=CUFES_SAMPLE_DEPTH_M,
                )
        t3m_leads.append(t3m)
        s3m_leads.append(s3m)
        mld_leads.append(mld_m)
        if "ocean_time" in slab:
            times.append(np.datetime64(_surface(slab.ocean_time).values))
        else:
            times.append(np.datetime64("NaT"))

    out = xr.Dataset(
        data_vars={
            "temp": (("lead_hours", "s_rho", "eta_rho", "xi_rho"), np.stack(temp_leads)),
            "salt": (("lead_hours", "s_rho", "eta_rho", "xi_rho"), np.stack(salt_leads)),
            "z": (("lead_hours", "s_rho", "eta_rho", "xi_rho"), np.stack(z_leads)),
            "T3m": (("lead_hours", "eta_rho", "xi_rho"), np.stack(t3m_leads)),
            "S3m": (("lead_hours", "eta_rho", "xi_rho"), np.stack(s3m_leads)),
            "MLD_m": (("lead_hours", "eta_rho", "xi_rho"), np.stack(mld_leads)),
            "lat": (("eta_rho", "xi_rho"), lat),
            "lon": (("eta_rho", "xi_rho"), lon),
        },
        coords={
            "lead_hours": np.asarray(lead_values, dtype=int),
            "s_rho": s_rho,
            "time": ("lead_hours", np.array(times, dtype="datetime64[ns]")),
        },
    )
    out["z"].attrs.update(units="m", long_name="depth", positive="down")
    out["temp"].attrs.update(units="degC")
    out["salt"].attrs.update(units="PSU")
    out["T3m"].attrs.update(units="degC", depth_m=CUFES_SAMPLE_DEPTH_M)
    out["S3m"].attrs.update(units="PSU", depth_m=CUFES_SAMPLE_DEPTH_M)
    out["MLD_m"].attrs.update(units="m")
    cycle_id = f"{cycle_date.strftime('%Y%m%d')}T03Z"
    out.attrs.update(
        cycle_id=cycle_id,
        cycle=cycle_id,
        source="wcofs",
        attribution=merged.attrs.get("attribution") or attribution_for("wcofs"),
        depth_convention="z_positive_down_metres",
        schema_version="wcofs_processed_v1",
    )
    return out


def write_wcofs_cycle(
    merged: xr.Dataset,
    cycle_date: dt.date,
    store_root: Path | None = None,
    *,
    extra_attrs: dict[str, Any] | None = None,
    packaged: xr.Dataset | None = None,
) -> Path:
    path = cycle_zarr_path(cycle_date, store_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    packaged = packaged or package_wcofs_cycle(merged, cycle_date)
    if extra_attrs:
        packaged.attrs.update(extra_attrs)
    ny = int(packaged.sizes["eta_rho"])
    nx = int(packaged.sizes["xi_rho"])
    ns = int(packaged.sizes["s_rho"])
    tile = min(16, ny, nx)
    encoding = {
        "temp": {"chunks": (1, ns, tile, tile)},
        "salt": {"chunks": (1, ns, tile, tile)},
        "z": {"chunks": (1, ns, tile, tile)},
        "T3m": {"chunks": (1, tile, tile)},
        "S3m": {"chunks": (1, tile, tile)},
        "MLD_m": {"chunks": (1, tile, tile)},
    }
    packaged.attrs.setdefault(
        "zarr_chunks",
        "lead_hours=1, s_rho=full, eta_rho/xi_rho=tile",
    )
    packaged.to_zarr(path, mode="w", consolidated=False, encoding=encoding)
    return path
