#!/usr/bin/env python3
"""Forecast refresh. This pass did not find a working CoastWatch RTOFS search."""

from __future__ import annotations

import sys


def main() -> None:
    print("NO_FORECAST_ENDPOINT_CONFIRMED")
    print("CoastWatch ERDDAP search for RTOFS forecast returned HTTP 404.")
    print("No forecast file was written. A species layer is not a forecast.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
