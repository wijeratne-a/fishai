"""Pilot ERDDAP regression: distances and speed QC from committed fixture (no network)."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from fishai.ingestion.biology.cufes.constants import ERDDAP_FIELDS
from fishai.ingestion.biology.cufes.transform import transform_rows
from fishai.ingestion.physics.geo_distance import haversine_km

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "cufes_pilot_distances.csv"
PILOT_EVENTS_READ = 15969
PILOT_UNITS_ROWS_SKIPPED = 27
PILOT_EVENTS_KEPT = 14592
PILOT_DROPPED_UNIQUE = 1377
PILOT_SPEED_REVIEW_COUNT = 25
PILOT_MEDIAN_SPEED_UNDER_10_MIN = 4.95
PILOT_MEDIAN_SPEED_10_MIN_OR_MORE = 9.51


def _load_pilot_rows() -> list[dict[str, str]]:
    with FIXTURE.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _erddap_only(row: dict[str, str]) -> dict[str, str]:
    return {k: row[k] for k in ERDDAP_FIELDS if k in row}


def test_pilot_fixture_distances_match_shared_great_circle() -> None:
    assert FIXTURE.is_file(), f"missing fixture: {FIXTURE}"
    rows = _load_pilot_rows()
    assert len(rows) == PILOT_EVENTS_READ
    max_delta_m = 0.0
    compared = 0
    for row in rows:
        recorded_text = str(row["distance_m"]).strip().lower()
        if recorded_text in {"", "nan"}:
            continue
        lat1 = float(row["latitude"])
        lon1 = float(row["longitude"])
        lat2 = float(row["stop_latitude"])
        lon2 = float(row["stop_longitude"])
        recorded_m = float(row["distance_m"])
        computed_m = haversine_km(lat1, lon1, lat2, lon2) * 1000.0
        assert math.isfinite(computed_m)
        max_delta_m = max(max_delta_m, abs(computed_m - recorded_m))
        assert abs(computed_m - recorded_m) <= 1.0
        compared += 1
    nan_dist = sum(
        1 for r in rows if str(r["distance_m"]).strip().lower() in {"", "nan"}
    )
    assert compared == len(rows) - nan_dist
    assert max_delta_m < 1.0


def test_pilot_qc_speed_report_matches_pr4_pilot() -> None:
    rows = [_erddap_only(r) for r in _load_pilot_rows()]
    result = transform_rows(rows, units_rows_skipped=PILOT_UNITS_ROWS_SKIPPED)
    report = result.qc_report
    assert report["events_read"] == PILOT_EVENTS_READ
    assert report["events_kept"] == PILOT_EVENTS_KEPT
    assert report["dropped_unique_total"] == PILOT_DROPPED_UNIQUE
    quantiles = report["implied_speed_knots_quantiles"]
    assert quantiles["speed_review_flag_count"] == PILOT_SPEED_REVIEW_COUNT
    p50_short = quantiles["duration_under_10_min"]["p50"]
    p50_long = quantiles["duration_10_min_or_more"]["p50"]
    assert p50_short is not None and p50_long is not None
    assert round(p50_short, 2) == PILOT_MEDIAN_SPEED_UNDER_10_MIN
    assert round(p50_long, 2) == PILOT_MEDIAN_SPEED_10_MIN_OR_MORE
