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

from fishai.ingestion.physics.wcofs_pull_log import day_outcome_for_date, utc_today
from fishai.ingestion.physics.wcofs_store import DEFAULT_STORE_ROOT, cycle_zarr_path

__all__ = [
    "CycleNotAvailable",
    "DEFAULT_STORE_ROOT",
    "WcofsDayFailed",
    "latest_wcofs_cycle_date",
    "list_wcofs_cycles",
    "open_wcofs_cycle",
    "open_wcofs_cycle_for_operational_day",
]


class CycleNotAvailable(LookupError):
    """Raised when a requested WCOFS cycle is not present in the local processed store."""


class WcofsDayFailed(CycleNotAvailable):
    """Raised when the daily job tombstoned a cycle date (do not use an older cycle instead)."""

    def __init__(self, message: str, *, reason: str, target_date: dt.date) -> None:
        super().__init__(message)
        self.reason = reason
        self.target_date = target_date


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


def _raise_if_day_failed(cycle_date: dt.date, store_root: Path) -> None:
    outcome, record = day_outcome_for_date(cycle_date, out_root=store_root)
    if outcome != "failed":
        return
    reason = str((record or {}).get("reason", "wcofs_nowcast_missing"))
    raise WcofsDayFailed(
        f"WCOFS cycle {cycle_date.isoformat()} failed on last daily attempt ({reason})",
        reason=reason,
        target_date=cycle_date,
    )


def latest_wcofs_cycle_date(
    store_root: Path | str | None = None,
    *,
    as_of: dt.date | None = None,
) -> dt.date:
    """
    Resolve the processed-store cycle for operational ``as_of`` (default: UTC today).

    Never falls back to an older cycle when ``as_of`` has no store. Tombstoned days
    raise ``WcofsDayFailed``.
    """
    root = _resolve_store_root(store_root)
    day = as_of or utc_today()
    _raise_if_day_failed(day, root)
    path = cycle_zarr_path(day, root)
    if path.is_dir():
        return day
    raise CycleNotAvailable(f"no processed WCOFS cycle for {day.isoformat()}")


def open_wcofs_cycle_for_operational_day(
    cycle_date: dt.date | None = None,
    *,
    store_root: Path | str | None = None,
    variables: Sequence[str] | None = None,
    lead_hours: Sequence[int] | None = None,
) -> xr.Dataset:
    """Open WCOFS for an operational calendar day without substituting an older cycle."""
    root = _resolve_store_root(store_root)
    day = cycle_date or utc_today()
    _raise_if_day_failed(day, root)
    return open_wcofs_cycle(
        day,
        store_root=root,
        variables=variables,
        lead_hours=lead_hours,
    )


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
    root = _resolve_store_root(store_root)
    _raise_if_day_failed(cycle_date, root)
    path = cycle_zarr_path(cycle_date, root)
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
