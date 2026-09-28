"""Copernicus Marine GLORYS (account required; disabled in pilot manifest)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fishai.ingestion.sources import SourceNotApprovedError, require_approved

SOURCE_MODULE = "glorys"

PRODUCT_ID = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
VARIABLES = ("thetao", "so", "tob", "mlotst")


def fetch_day(
    date: dt.date,
    bbox: tuple[float, float, float, float],
    variables: tuple[str, ...] = VARIABLES,
    **_: Any,
) -> Any:
    """
    Fetch GLORYS fields for ``date`` (not called without Copernicus credentials).

    Always enforces ``require_approved('glorys')``; the pilot manifest keeps this
    source disabled.
    """
    require_approved("glorys")
    raise SourceNotApprovedError("glorys should be blocked by require_approved")
