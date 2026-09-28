"""Copernicus Marine GLORYS reanalysis (account required; disabled in pilot manifest)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fishai.ingestion.sources import SourceNotApprovedError, require_approved

SOURCE_MODULE = "glorys"

# Verified product (Copernicus Marine, 2026-09-28): daily means 1993-01-01 .. 2026-06-23.
PRODUCT_ID = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
PRODUCT_TIME_START = dt.date(1993, 1, 1)
PRODUCT_TIME_END = dt.date(2026, 6, 23)

# Native variable names on this product (bottom temperature is ``bottomT``, not ``tob``).
VARIABLES = ("thetao", "so", "bottomT", "mlotst", "uo", "vo", "zos")


def fetch_day(
    date: dt.date,
    bbox: tuple[float, float, float, float],
    variables: tuple[str, ...] = VARIABLES,
    **_: Any,
) -> Any:
    """
    Fetch GLORYS fields for ``date`` via ``copernicusmarine`` (not called in CI).

    Credentials are read from ``~/.copernicusmarine/`` on the runtime host only;
    this module never loads or logs credential paths. The pilot keeps GLORYS
    ``enabled: false`` until license review completes — ``require_approved`` blocks
    all calls here.
    """
    require_approved("glorys")
    raise SourceNotApprovedError("glorys should be blocked by require_approved")
