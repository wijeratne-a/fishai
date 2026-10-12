"""NOAA NCEI THREDDS archive for issued WCOFS fields (2021-03-22 onward)."""

from __future__ import annotations

import datetime as dt

NCEI_ARCHIVE_START = dt.date(2021, 3, 22)
NCEI_FILESERVER_BASE = "https://www.ncei.noaa.gov/thredds/fileServer/model-wcofs-files"


def ncei_fields_basename(cycle: dt.date, lead: str) -> str:
    ymd = cycle.strftime("%Y%m%d")
    return f"nos.wcofs.fields.{lead}.{ymd}.t03z.nc"


def ncei_fields_url(cycle: dt.date, lead: str) -> str:
    """HTTPS fileServer URL for one issued fields lead (ROMS s-coordinates)."""
    return f"{NCEI_FILESERVER_BASE}/{cycle:%Y/%m}/{ncei_fields_basename(cycle, lead)}"


def ncei_cycle_in_archive(cycle: dt.date) -> bool:
    return cycle >= NCEI_ARCHIVE_START
