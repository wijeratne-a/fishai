#!/usr/bin/env python3
"""Write the NCRMP catalog from the live NCEI ERDDAP search and info pages."""

from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "manifests" / "latest-source-status.csv"
UA = "FishAI-internal-research/1.0"


def get(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read().decode("latin-1")


def main() -> None:
    search = json.loads(get(
        "https://www.ncei.noaa.gov/erddap/search/index.json?searchFor=CRCP_Reef_Fish&itemsPerPage=100&page=1"
    ))
    cols = search["table"]["columnNames"]
    id_i = cols.index("Dataset ID")
    rows = []
    for item in search["table"]["rows"]:
        dataset = item[id_i]
        info = get(f"https://www.ncei.noaa.gov/erddap/info/{dataset}/index.csv")
        attrs = {}
        for record in csv.reader(io.StringIO(info)):
            if len(record) >= 5 and record[1] == "NC_GLOBAL":
                attrs[record[2]] = record[4]
        end = attrs.get("time_coverage_end", "")
        year = end[:4]
        rows.append({
            "source_id": dataset,
            "provider": "NOAA NCEI ERDDAP",
            "region": dataset.removeprefix("CRCP_Reef_Fish_Surveys_"),
            "dataset_title": attrs.get("title", dataset),
            "latest_observation_date": end,
            "latest_published_year": year,
            "remote_modified_date": attrs.get("date_created", ""),
            "local_latest_year": "",
            "update_available": "",
            "access_class": "AUTO_ACQUIRE_INTERNAL_ONLY",
            "protocol": "see schema family in structured-survey-manifest",
            "download_endpoint": f"https://www.ncei.noaa.gov/erddap/tabledap/{dataset}.csv",
            "next_action": "compare local manifest before another full-year download",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} datasets to {OUT}")


if __name__ == "__main__":
    main()
