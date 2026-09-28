"""
Read-only access to processed WCOFS cycles on local Zarr (written by ``fishai-physics daily``).

This module never downloads data or mutates the store.

Returned ``xarray.Dataset`` schema (``schema_version=wcofs_processed_v1``):

Coordinates / dimensions
  - ``lead_hours`` (int): hours from cycle init (e.g. 3, 6, …, 24 nowcast; 27+ forecast).
  - ``s_rho`` (float): ROMS s-level index (dimension only; depths are in ``z``).
  - ``eta_rho``, ``xi_rho``: curvilinear WCOFS rho-grid indices.
  - ``time`` (datetime64[ns], on ``lead_hours``): valid time per lead.

Data variables
  - ``temp`` (lead_hours, s_rho, eta_rho, xi_rho): potential temperature [degC].
  - ``salt`` (lead_hours, s_rho, eta_rho, xi_rho): salinity [PSU].
  - ``z`` (lead_hours, s_rho, eta_rho, xi_rho): depth [m], **positive downward**.
  - ``T3m``, ``S3m`` (lead_hours, eta_rho, xi_rho): linearly interpolated to 3 m [degC / PSU].
  - ``MLD_m`` (lead_hours, eta_rho, xi_rho): temperature-threshold mixed-layer depth [m].
  - ``lat``, ``lon`` (eta_rho, xi_rho): cell-centre geographic coordinates [degrees].

Global attributes (required for consumers)
  - ``cycle_id`` / ``cycle``: e.g. ``20260928T03Z`` (03z cycle date).
  - ``source``: ``wcofs``.
  - ``attribution``: WCOFS credit string from ``data/SOURCES.yaml``.
  - ``depth_convention``: ``z_positive_down_metres``.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Sequence

import xarray as xr

from fishai.ingestion.physics.wcofs_store import DEFAULT_STORE_ROOT, cycle_zarr_path

__all__ = [
    "CycleNotAvailable",
    "DEFAULT_STORE_ROOT",
    "list_wcofs_cycles",
    "open_wcofs_cycle",
]


class CycleNotAvailable(LookupError):
    """Raised when a requested WCOFS cycle is not present in the local processed store."""


def _resolve_store_root(store_root: Path | str | None) -> Path:
    return Path(store_root) if store_root is not None else DEFAULT_STORE_ROOT


def list_wcofs_cycles(store_root: Path | str | None = None) -> list[dt.date]:
    """List cycle dates available under ``store_root`` (sorted ascending)."""
    root = _resolve_store_root(store_root)
    if not root.is_dir():
        return []
    dates: list[dt.date] = []
    for path in sorted(root.glob("wcofs_*.zarr")):
        stem = path.name.replace("wcofs_", "").replace(".zarr", "")
        try:
            dates.append(dt.datetime.strptime(stem, "%Y%m%d").date())
        except ValueError:
            continue
    return dates


def open_wcofs_cycle(
    cycle_date: dt.date,
    *,
    store_root: Path | str | None = None,
    variables: Sequence[str] | None = None,
    lead_hours: Sequence[int] | None = None,
) -> xr.Dataset:
    """
    Open one processed WCOFS cycle from local Zarr (read-only).

    Parameters
    ----------
    cycle_date:
        UTC date of the 03z WCOFS cycle.
    store_root:
        Processed physics directory (default: ``data/processed/physics``).
    variables:
        Optional subset of data variable names to load.
    lead_hours:
        Optional subset of ``lead_hours`` coordinate values.

    Raises
    ------
    CycleNotAvailable
        If the cycle Zarr store does not exist locally.
    """
    path = cycle_zarr_path(cycle_date, _resolve_store_root(store_root))
    if not path.is_dir():
        raise CycleNotAvailable(f"no processed WCOFS cycle at {path}")
    ds = xr.open_zarr(path, consolidated=False)
    if lead_hours is not None:
        ds = ds.sel(lead_hours=list(lead_hours))
    if variables is not None:
        ds = ds[list(variables)]
    _validate_processed_attrs(ds)
    return ds


def _validate_processed_attrs(ds: xr.Dataset) -> None:
    for key in ("cycle_id", "source", "attribution"):
        if key not in ds.attrs or not str(ds.attrs[key]).strip():
            raise CycleNotAvailable(f"processed store missing attribute: {key}")
