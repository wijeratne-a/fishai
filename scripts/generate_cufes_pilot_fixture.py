#!/usr/bin/env python3
"""One-off: fetch CalCOFI CUFES pilot rows and write tests/fixtures/cufes_pilot_distances.csv.

Uses PR #4's legacy haversine (EARTH_RADIUS_NM=3440.065) for distance_m before the PR #2 swap.
ERDDAP window matches PR #4: 1996-03-15 .. 2022-04-27, pilot bbox from data/SOURCES.yaml.
At most 2 concurrent HTTP requests.
"""

from __future__ import annotations

import csv
import io
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fishai.ingestion.biology.cufes.constants import ERDDAP_FIELDS
from fishai.ingestion.biology.cufes.fetch import (
    DEFAULT_BACKOFF_SEC,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT_SEC,
    _http_get,
    build_erddap_csv_url,
    iter_yearly_windows,
    read_cufes_csv,
)
from fishai.ingestion.biology.cufes.pipeline import pilot_bbox_from_manifest
from fishai.ingestion.biology.cufes.transform import make_event_id, transform_rows

_LEGACY_EARTH_RADIUS_NM = 3440.065
_PILOT_START = date(1996, 3, 15)
_PILOT_END = date(2022, 4, 27)
_OUT = REPO / "tests" / "fixtures" / "cufes_pilot_distances.csv"
_EXPECTED_READ = 15969


def _legacy_haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """PR #4 temporary helper (deleted on branch) — nautical miles × 1852."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return _LEGACY_EARTH_RADIUS_NM * c * 1852.0


def _fetch_year(window: tuple) -> tuple[int, bytes]:
    win_start, win_end = window
    bbox = pilot_bbox_from_manifest()
    url = build_erddap_csv_url(win_start, win_end, bbox, fields=ERDDAP_FIELDS)
    body = _http_get(
        url,
        timeout=DEFAULT_TIMEOUT_SEC,
        max_retries=DEFAULT_MAX_RETRIES,
        backoff=DEFAULT_BACKOFF_SEC,
    )
    return win_start.year, body


def main() -> int:
    windows = iter_yearly_windows(_PILOT_START, _PILOT_END)
    bodies: dict[int, bytes] = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(_fetch_year, w): w for w in windows}
        for fut in as_completed(futures):
            year, body = fut.result()
            bodies[year] = body

    rows: list[dict[str, str]] = []
    units_skipped = 0
    for year in sorted(bodies):
        tmp = REPO / "data" / "raw" / "calcofi_cufes" / f"_gen_{year}.csv"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(bodies[year])
        chunk, skipped = read_cufes_csv(tmp)
        rows.extend(chunk)
        units_skipped += skipped
        tmp.unlink(missing_ok=True)

    if len(rows) != _EXPECTED_READ:
        print(
            f"ERROR: expected {_EXPECTED_READ} data rows, got {len(rows)} "
            f"(units_rows_skipped={units_skipped})",
            file=sys.stderr,
        )
        return 1

    transformed = transform_rows(rows, units_rows_skipped=units_skipped)
    report = transformed.qc_report
    print(
        "QC snapshot:",
        f"events_read={report['events_read']}",
        f"kept={report['events_kept']}",
        f"dropped={report['dropped_unique_total']}",
        f"speed_review={report['implied_speed_knots_quantiles']['speed_review_flag_count']}",
    )
    q = report["implied_speed_knots_quantiles"]
    p50_short = q["duration_under_10_min"]["p50"]
    p50_long = q["duration_10_min_or_more"]["p50"]
    print(f"median implied_speed_kn <10min={p50_short:.4f} >=10min={p50_long:.4f}")

    fieldnames = list(ERDDAP_FIELDS) + ["event_id", "distance_m"]
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    with _OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            cruise = str(row.get("cruise", "")).strip()
            ship_code = str(row.get("ship_code", "")).strip()
            sample_number = str(row.get("sample_number", "")).strip()
            event_id = make_event_id(cruise, ship_code, sample_number)
            out = dict(row)
            out["event_id"] = event_id
            try:
                lat1 = float(row["latitude"])
                lon1 = float(row["longitude"])
                lat2 = float(row["stop_latitude"])
                lon2 = float(row["stop_longitude"])
                if not all(math.isfinite(v) for v in (lat1, lon1, lat2, lon2)):
                    out["distance_m"] = "nan"
                else:
                    out["distance_m"] = f"{_legacy_haversine_distance_m(lat1, lon1, lat2, lon2):.6f}"
            except ValueError:
                out["distance_m"] = "nan"
            writer.writerow(out)

    print(f"Wrote {_OUT} ({_OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
