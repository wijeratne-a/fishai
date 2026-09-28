#!/usr/bin/env python3
"""Bounded OBIS occurrence fetch. One request at a time. Presence evidence only."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "data" / "raw" / "biological" / "obis" / "florida-keys-last-90d.json"
URL = "https://api.obis.org/v3/occurrence?" + urllib.parse.urlencode({
    "geometry": "POLYGON((-83.2 24.4,-80.0 24.4,-80.0 25.8,-83.2 25.8,-83.2 24.4))",
    "startdate": "2026-06-26",
    "size": "500",
})


def main() -> None:
    if DEST.exists() and DEST.stat().st_size > 1000:
        print(f"skip existing {DEST}")
        return
    request = urllib.request.Request(URL, headers={"User-Agent": "FishAI-internal-research/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode())
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps({"total": data.get("total"), "results": data.get("results")}), encoding="utf-8")
    print(f"total={data.get('total')} saved={len(data.get('results') or [])}")


if __name__ == "__main__":
    main()
