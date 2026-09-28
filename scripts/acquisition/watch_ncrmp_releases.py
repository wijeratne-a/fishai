#!/usr/bin/env python3
"""Check whether a 2025 NCRMP fish year is public. Does not download unchanged files."""

from __future__ import annotations

import csv
import io
import json
import urllib.request

UA = "FishAI-internal-research/1.0"
DATASETS = [
    "CRCP_Reef_Fish_Surveys_Florida",
    "CRCP_Reef_Fish_Surveys_Puerto_Rico",
    "CRCP_Reef_Fish_Surveys_USVI",
    "CRCP_Reef_Fish_Surveys_Flower_Gardens",
]


def years(dataset: str) -> list[str]:
    url = f"https://www.ncei.noaa.gov/erddap/tabledap/{dataset}.csv?YEAR&distinct()"
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=180) as response:
        rows = list(csv.reader(io.StringIO(response.read().decode("latin-1"))))
    return [row[0] for row in rows[2:] if row and row[0].strip()]


def main() -> None:
    found = {}
    for dataset in DATASETS:
        vals = years(dataset)
        found[dataset] = vals
        print(dataset, vals, "HAS_2025" if "2025" in vals else "SURVEY_COMPLETED_DATA_NOT_YET_PUBLIC_OR_NOT_IN_TABLE")
    if not any("2025" in vals for vals in found.values()):
        print("NO_2025_FILE_IN_THESE_ERDDAP_DATASETS")


if __name__ == "__main__":
    main()
