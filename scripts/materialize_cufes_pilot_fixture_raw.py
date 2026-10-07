#!/usr/bin/env python3
"""Write ERDDAP-shaped yearly CSVs from tests/fixtures/cufes_pilot_distances.csv.

The fixture is the public CalCOFI CUFES pilot-bbox table (see
scripts/generate_cufes_pilot_fixture.py). Used when NOAA ERDDAP endpoints return
504/timeouts but the training-table contract must be rebuilt locally.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "cufes_pilot_distances.csv"
UNITS_TEMPLATE = REPO / "tests" / "fixtures" / "calcofi_cufes_with_units_row.csv"
RAW_DIR = REPO / "data" / "raw" / "calcofi_cufes"

ERDDAP_COLUMNS = (
    "cruise",
    "ship_code",
    "sample_number",
    "time",
    "latitude",
    "longitude",
    "start_pump_speed",
    "stop_time",
    "stop_latitude",
    "stop_longitude",
    "stop_pump_speed",
    "sardine_eggs",
    "anchovy_eggs",
    "jack_mackerel_eggs",
    "hake_eggs",
    "squid_eggs",
    "other_fish_eggs",
)


def _units_row() -> dict[str, str]:
    with UNITS_TEMPLATE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        units = next(reader)
    return {k: units.get(k, "") for k in ERDDAP_COLUMNS}


def main() -> int:
    if not FIXTURE.is_file():
        raise SystemExit(f"missing fixture: {FIXTURE}")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    by_year: dict[int, list[dict[str, str]]] = defaultdict(list)
    with FIXTURE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            t = row.get("time") or ""
            year = datetime.fromisoformat(t.replace("Z", "+00:00")).year
            out = {col: row.get(col, "") for col in ERDDAP_COLUMNS}
            by_year[year].append(out)
    units = _units_row()
    for year in sorted(by_year):
        dest = RAW_DIR / f"erdCalCOFIcufes_{year}.csv"
        with dest.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(ERDDAP_COLUMNS))
            writer.writeheader()
            writer.writerow(units)
            writer.writerows(by_year[year])
        print(f"wrote {dest.name} rows={len(by_year[year])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
