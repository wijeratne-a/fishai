#!/usr/bin/env python3
"""Download Florida Keys Reef Visual Census rows from the public NCEI ERDDAP table.

Writes gzip CSV under data/raw/biological/. That directory is gitignored.
Does not print coordinates.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "biological"
MANIFEST = ROOT / "data" / "manifests" / "acquisition-manifest.csv"
DATASET = "CRCP_Reef_Fish_Surveys_Florida"
BASE = f"https://www.ncei.noaa.gov/erddap/tabledap/{DATASET}.csv"
USER_AGENT = "FishAI-internal-research/1.0 (public ERDDAP; internal feasibility)"

COLUMNS = [
    "time",
    "latitude",
    "longitude",
    "PRIMARY_SAMPLE_UNIT",
    "YEAR",
    "MONTH",
    "DAY",
    "STATION_NR",
    "DEPTH",
    "UNDERWATER_VISIBILITY",
    "MAPGRID_NR",
    "HABITAT_CD",
    "HABITAT_TYPE",
    "ZONE_NR",
    "ZONE_NAME",
    "RUGOSITY_CD",
    "SUB_REGION_NR",
    "SUB_REGION_NAME",
    "SPECIES_NR",
    "SPECIES_CD",
    "SCIENTIFIC_NAME",
    "COMMON_NAME",
    "length_fish",
    "NUM",
    "TIME_SEEN",
    "TIME_SEEN_DESCR",
    "MPA_NR",
    "MPA_NAME",
    "PROT",
    "STRAT",
    "REGION",
    "REGION_DESCRIPTION",
    "sample_year",
    "accession_url",
]

YEARS = {
    2018: "https://www.ncei.noaa.gov/archive/accession/0208321",
    2022: "https://www.ncei.noaa.gov/archive/accession/0282183",
    2024: "https://www.ncei.noaa.gov/archive/accession/0306184",
}

MANIFEST_FIELDS = [
    "year",
    "query_url",
    "retrieval_timestamp_utc",
    "http_status",
    "content_type",
    "compressed_bytes",
    "uncompressed_bytes",
    "sha256",
    "data_rows",
    "n_columns",
    "accession_urls",
    "download_status",
    "validation_status",
    "path",
]


def build_url(year: int) -> str:
    variables = ",".join(COLUMNS)
    constraints = (
        f'&REGION={urllib.parse.quote(chr(34) + "FLA KEYS" + chr(34))}'
        f"&YEAR={year}"
    )
    return f"{BASE}?{variables}{constraints}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def looks_like_html(sample: bytes) -> bool:
    head = sample.lstrip()[:200].lower()
    return head.startswith(b"<") or b"<html" in head or b"<!doctype" in head


def fetch(url: str, dest_partial: Path, attempts: int = 5) -> tuple[int, str]:
    delay = 2.0
    last_error = "unknown"
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=600) as response:
                status = getattr(response, "status", 200)
                content_type = response.headers.get("Content-Type", "")
                if status != 200:
                    raise urllib.error.HTTPError(url, status, "status", response.headers, None)
                if "csv" not in content_type.lower() and "text/plain" not in content_type.lower():
                    raise RuntimeError(f"unexpected content type {content_type}")
                dest_partial.parent.mkdir(parents=True, exist_ok=True)
                if dest_partial.exists():
                    dest_partial.unlink()
                first = response.read(4096)
                if looks_like_html(first):
                    raise RuntimeError("HTML payload rejected")
                with dest_partial.open("wb") as handle:
                    handle.write(first)
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
                return status, content_type
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if dest_partial.exists():
                dest_partial.unlink()
            if exc.code in {413, 400}:
                raise
            if exc.code == 429 and retry_after and retry_after.isdigit():
                time.sleep(int(retry_after))
            elif exc.code in {429, 500, 502, 503, 504} and attempt < attempts:
                time.sleep(delay)
                delay *= 2
            else:
                raise
        except Exception as exc:
            last_error = str(exc)
            if dest_partial.exists():
                dest_partial.unlink()
            if attempt >= attempts:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(last_error)


def summarize_csv_gz(path: Path) -> tuple[int, int, int, list[str]]:
    accessions: set[str] = set()
    rows = 0
    n_columns = 0
    uncompressed = 0
    with gzip.open(path, "rb") as handle:
        text = io.TextIOWrapper(handle, encoding="latin-1", newline="")
        reader = csv.reader(text)
        header = next(reader)
        n_columns = len(header)
        next(reader)  # units row
        acc_idx = header.index("accession_url")
        for row in reader:
            rows += 1
            if row[acc_idx]:
                accessions.add(row[acc_idx])
    uncompressed = path.stat().st_size  # placeholder replaced by caller if needed
    return rows, n_columns, uncompressed, sorted(accessions)


def gzip_atomic(src: Path, dest: Path) -> int:
    tmp = dest.with_suffix(dest.suffix + ".partial")
    if tmp.exists():
        tmp.unlink()
    raw_size = src.stat().st_size
    with src.open("rb") as inp, gzip.open(tmp, "wb") as out:
        while True:
            chunk = inp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    tmp.replace(dest)
    return raw_size


def append_manifest(row: dict[str, str]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    exists = MANIFEST.exists()
    with MANIFEST.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def already_good(dest: Path) -> bool:
    if not dest.exists() or dest.stat().st_size < 100:
        return False
    try:
        with gzip.open(dest, "rt", encoding="latin-1") as handle:
            header = handle.readline()
        return header.startswith("time,")
    except OSError:
        return False


def download_year(year: int) -> None:
    dest = RAW / f"noaa-rvc-florida-keys-{year}.csv.gz"
    partial = RAW / f"noaa-rvc-florida-keys-{year}.csv.partial"
    url = build_url(year)
    if already_good(dest):
        print(f"{year} already present {dest.name}", file=sys.stderr)
        return
    if partial.exists():
        partial.unlink()
    status, content_type = fetch(url, partial)
    raw_size = gzip_atomic(partial, dest)
    partial.unlink(missing_ok=True)
    digest = sha256_file(dest)
    rows, n_columns, _, accessions = summarize_csv_gz(dest)
    append_manifest(
        {
            "year": str(year),
            "query_url": url,
            "retrieval_timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "http_status": str(status),
            "content_type": content_type,
            "compressed_bytes": str(dest.stat().st_size),
            "uncompressed_bytes": str(raw_size),
            "sha256": digest,
            "data_rows": str(rows),
            "n_columns": str(n_columns),
            "accession_urls": "|".join(accessions),
            "download_status": "COMPLETE",
            "validation_status": "DOWNLOADED_UNVALIDATED",
            "path": str(dest.relative_to(ROOT)),
        }
    )
    print(
        json.dumps(
            {
                "year": year,
                "compressed_bytes": dest.stat().st_size,
                "uncompressed_bytes": raw_size,
                "sha256": digest,
                "data_rows": rows,
                "accession_urls": accessions,
            }
        )
    )


def main() -> None:
    years = [int(arg) for arg in sys.argv[1:]] or list(YEARS)
    for year in years:
        if year not in YEARS:
            raise SystemExit(f"unsupported year {year}")
        download_year(year)


if __name__ == "__main__":
    main()
