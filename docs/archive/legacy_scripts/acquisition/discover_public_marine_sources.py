#!/usr/bin/env python3
"""Discover public marine survey leads via NCEI ERDDAP (CalCOFI family).

Queries NCEI first. If CalCOFI is absent there, also records CoastWatch ERDDAP
CalCOFI search hits as metadata-only discovery leads (no bulk download).
Writes data/manifests/discovery-candidates.csv.
"""

from __future__ import annotations

import csv
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "manifests" / "discovery-candidates.csv"
UA = "FishAI-internal-research/1.0"
FAMILY = "CalCOFI"
NCEI_SEARCH = "https://www.ncei.noaa.gov/erddap/search/index.json"
COASTWATCH_SEARCH = "https://coastwatch.pfeg.noaa.gov/erddap/search/index.json"


def get_json(url: str) -> Tuple[int, Optional[Dict[str, Any]], str]:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(body), ""
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:500]
        return err.code, None, detail
    except Exception as err:  # noqa: BLE001 — record any network failure for the manifest
        return 0, None, str(err)


def search_rows(base_url: str, query: str, provider: str) -> List[Dict[str, str]]:
    params = urllib.parse.urlencode(
        {"searchFor": query, "itemsPerPage": 50, "page": 1}
    )
    url = f"{base_url}?{params}"
    status, payload, detail = get_json(url)
    retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if status != 200 or payload is None:
        return [
            {
                "family": FAMILY,
                "dataset_id": "",
                "title": "",
                "institution": "",
                "provider": provider,
                "search_url": url,
                "http_status": str(status),
                "tabledap_url": "",
                "info_url": "",
                "summary": detail.replace("\n", " ")[:400],
                "retrieved_utc": retrieved,
                "on_disk": "no",
                "notes": "no_matching_results_or_error",
            }
        ]

    cols = payload["table"]["columnNames"]
    id_i = cols.index("Dataset ID")
    title_i = cols.index("Title")
    inst_i = cols.index("Institution")
    summary_i = cols.index("Summary")
    info_i = cols.index("Info")
    tabledap_i = cols.index("tabledap")
    rows = []
    for item in payload["table"]["rows"]:
        dataset_id = item[id_i]
        rows.append(
            {
                "family": FAMILY,
                "dataset_id": dataset_id,
                "title": item[title_i],
                "institution": item[inst_i],
                "provider": provider,
                "search_url": url,
                "http_status": "200",
                "tabledap_url": item[tabledap_i],
                "info_url": item[info_i],
                "summary": (item[summary_i] or "").replace("\n", " ")[:400],
                "retrieved_utc": retrieved,
                "on_disk": "no",
                "notes": "metadata_only_discovery",
            }
        )
    return rows


def main() -> None:
    fieldnames = [
        "family",
        "dataset_id",
        "title",
        "institution",
        "provider",
        "search_url",
        "http_status",
        "tabledap_url",
        "info_url",
        "summary",
        "retrieved_utc",
        "on_disk",
        "notes",
    ]
    rows = search_rows(NCEI_SEARCH, FAMILY, "NOAA NCEI ERDDAP")
    # NCEI currently has no CalCOFI tabledap family; CoastWatch hosts official SWFSC CalCOFI.
    ncei_hits = [r for r in rows if r["dataset_id"]]
    if not ncei_hits:
        rows.extend(
            search_rows(COASTWATCH_SEARCH, FAMILY, "NOAA CoastWatch ERDDAP (PFEG)")
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    hits = sum(1 for r in rows if r["dataset_id"])
    print(f"wrote {len(rows)} discovery rows ({hits} dataset hits) to {OUT}")


if __name__ == "__main__":
    main()
