#!/usr/bin/env python3
"""Download the newest NCRMP reef-fish year, and one earlier year, per region.

Florida Keys files already acquired by download_noaa_rvc.py are not fetched again.
Outputs stay under data/raw/biological/noaa-ncrmp/ (gitignored).
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "raw" / "biological" / "noaa-ncrmp"
MANIFEST = ROOT / "data" / "manifests" / "structured-survey-manifest.csv"
UA = "FishAI-internal-research/1.0 (public ERDDAP; internal feasibility)"

# Newest year plus one earlier year for a temporal comparison.
PLAN = {
    "CRCP_Reef_Fish_Surveys_Puerto_Rico": ("YEAR", [2023, 2021, 2019, 2016], "atlantic"),
    "CRCP_Reef_Fish_Surveys_USVI": ("YEAR", [2023, 2021, 2019, 2017], "atlantic"),
    "CRCP_Reef_Fish_Surveys_Flower_Gardens": ("YEAR", [2024, 2023, 2022, 2018], "atlantic"),
    "CRCP_Reef_Fish_Surveys_Hawaii": ("OBS_YEAR", [2024, 2019], "pacific"),
    "CRCP_Reef_Fish_Surveys_American_Samoa": ("OBS_YEAR", [2023, 2018], "pacific"),
    "CRCP_Reef_Fish_Surveys_CNMI_Guam": ("OBS_YEAR", [2022, 2017], "pacific"),
    "CRCP_Reef_Fish_Surveys_PRIAs": ("OBS_YEAR", [2023, 2018], "pacific"),
}

ATLANTIC = [
    "time", "latitude", "longitude", "YEAR", "MONTH", "DAY", "PRIMARY_SAMPLE_UNIT",
    "STATION_NR", "SAMPLE_DEPTH", "UNDERWATER_VISIBILITY", "HABITAT_CD", "REGION",
    "SUB_REGION_NAME", "SPECIES_CD", "SCIENTIFIC_NAME", "COMMON_NAME", "LEN", "NUM",
    "accession_url",
]
PACIFIC = [
    "time", "latitude", "longitude", "OBS_YEAR", "DATE_", "REGION_NAME", "ISLAND",
    "SITE", "METHOD", "DEPTH", "VISIBILITY", "SPECIES", "TAXONNAME", "SCIENTIFIC_NAME",
    "COMMON_NAME", "COUNT", "SIZE_", "OBS_TYPE", "accession_url",
]


def available_columns(dataset: str) -> set[str]:
    url = f"https://www.ncei.noaa.gov/erddap/info/{dataset}/index.csv"
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        rows = list(csv.reader(io.StringIO(response.read().decode("latin-1"))))
    return {row[1] for row in rows[1:] if row and row[0] == "variable"}


def build_url(dataset: str, year_field: str, year: int, family: str) -> str:
    wanted = ATLANTIC if family == "atlantic" else PACIFIC
    present = available_columns(dataset)
    chosen = []
    for name in wanted:
        if name in present:
            chosen.append(name)
        elif name == "SAMPLE_DEPTH" and "DEPTH" in present:
            chosen.append("DEPTH")
    if not chosen:
        raise RuntimeError(f"no overlapping columns for {dataset}")
    cols = ",".join(chosen)
    return (
        f"https://www.ncei.noaa.gov/erddap/tabledap/{dataset}.csv?{cols}"
        f"&{year_field}={year}"
    )


def looks_like_html(sample: bytes) -> bool:
    head = sample.lstrip()[:200].lower()
    return head.startswith(b"<") or b"<html" in head


def fetch(url: str, partial: Path) -> tuple[int, str]:
    delay = 2.0
    for attempt in range(1, 5):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=600) as response:
                status = getattr(response, "status", 200)
                ctype = response.headers.get("Content-Type", "")
                if "csv" not in ctype.lower():
                    raise RuntimeError(ctype)
                first = response.read(4096)
                if looks_like_html(first):
                    raise RuntimeError("html")
                partial.parent.mkdir(parents=True, exist_ok=True)
                with partial.open("wb") as handle:
                    handle.write(first)
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
                return status, ctype
        except Exception:
            if partial.exists():
                partial.unlink()
            if attempt == 4:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def row_count(path: Path) -> int:
    with gzip.open(path, "rt", encoding="latin-1", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        next(reader)
        return sum(1 for _ in reader)


def append(row: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    fields = list(row)
    exists = MANIFEST.exists()
    with MANIFEST.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    only = set(sys.argv[1:])
    for dataset, (field, years, family) in PLAN.items():
        if only and dataset not in only and not any(y in only for y in map(str, years)):
            if dataset not in only:
                continue
        for year in years:
            dest = OUT / dataset / f"{year}.csv.gz"
            if dest.exists() and dest.stat().st_size > 1000:
                print(f"skip {dataset} {year}", file=sys.stderr)
                continue
            url = build_url(dataset, field, year, family)
            partial = dest.with_suffix(".partial")
            status, ctype = fetch(url, partial)
            raw_size = partial.stat().st_size
            tmp = dest.with_suffix(".gz.partial")
            with partial.open("rb") as inp, gzip.open(tmp, "wb") as out:
                while True:
                    chunk = inp.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            tmp.replace(dest)
            partial.unlink(missing_ok=True)
            digest = sha256(dest)
            rows = row_count(dest)
            append(
                {
                    "dataset_id": dataset,
                    "year": year,
                    "family": family,
                    "query_url": url,
                    "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "http_status": status,
                    "content_type": ctype,
                    "uncompressed_bytes": raw_size,
                    "compressed_bytes": dest.stat().st_size,
                    "sha256": digest,
                    "data_rows": rows,
                    "path": str(dest.relative_to(ROOT)),
                }
            )
            print(f"{dataset} {year} rows={rows} sha={digest[:12]}", file=sys.stderr)


if __name__ == "__main__":
    main()
