"""Load WCOFS cycle files from the processed physics store for validation commands."""

from __future__ import annotations

import datetime as dt
import logging

import xarray as xr

from fishai.physics.store import CycleNotAvailable, WcofsDayFailed, open_wcofs_cycle

logger = logging.getLogger(__name__)


def load_wcofs_cycle(cycle_yyyymmdd: str) -> xr.Dataset | None:
    """Open one local WCOFS cycle; return None when the cycle is not in the store."""
    try:
        cycle_date = dt.datetime.strptime(cycle_yyyymmdd, "%Y%m%d").date()
    except ValueError as exc:
        raise ValueError(f"cycle must be YYYYMMDD, got {cycle_yyyymmdd!r}") from exc
    try:
        return open_wcofs_cycle(cycle_date)
    except WcofsDayFailed:
        raise
    except CycleNotAvailable:
        logger.warning("WCOFS cycle %s not available in local store; skipping", cycle_yyyymmdd)
        return None
