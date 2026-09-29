#!/usr/bin/env python3
"""Characterize 1998 CUFES QC exclusions against the locked time-forward split.

Reads tests/fixtures/cufes_pilot_distances.csv and applies transform_rows.
Does not change exclusion rules. Writes a JSON report.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fishai.ingestion.biology.cufes.constants import (  # noqa: E402
    ERDDAP_FIELDS,
    QC_RULE_LABELS,
)
from fishai.ingestion.biology.cufes.transform import (  # noqa: E402
    _parse_erddap_time,
    qc_flags_for_row,
    transform_rows,
)

FIXTURE = REPO / "tests" / "fixtures" / "cufes_pilot_distances.csv"
FIT_END = datetime(2017, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
TEST_START = datetime(2018, 1, 1, tzinfo=timezone.utc)


def _split_bucket(stamp: datetime | None) -> str:
    if stamp is None:
        return "unparsed"
    if stamp <= FIT_END:
        return "fit_through_2017-12-31"
    if stamp >= TEST_START:
        return "test_from_2018-01-01"
    return "gap"


def _flag_labels(flags: int) -> list[str]:
    return [label for label, bit in QC_RULE_LABELS if flags & bit]


def main() -> int:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    with FIXTURE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    year_rows = [row for row in rows if str(row["time"]).startswith("1998")]
    erddap = [{key: row[key] for key in ERDDAP_FIELDS} for row in year_rows]
    result = transform_rows(erddap, units_rows_skipped=0)
    report = result.qc_report

    by_rule = {key: int(value) for key, value in report["dropped_by_rule"].items() if value}
    months_kept: Counter[str] = Counter()
    months_dropped: Counter[str] = Counter()
    cruises_kept: Counter[str] = Counter()
    cruises_dropped: Counter[str] = Counter()
    split_kept: Counter[str] = Counter()
    split_dropped: Counter[str] = Counter()
    dropped_examples: list[dict[str, object]] = []
    for row in year_rows:
        flags = qc_flags_for_row(row)
        month = str(row["time"])[:7]
        cruise = str(row["cruise"])
        stamp = _parse_erddap_time(row.get("time"))
        bucket = _split_bucket(stamp)
        if flags:
            months_dropped[month] += 1
            cruises_dropped[cruise] += 1
            split_dropped[bucket] += 1
            if len(dropped_examples) < 12 or "coord_invalid" in _flag_labels(flags):
                dropped_examples.append(
                    {
                        "event_id": f"CUFES:{row['cruise']}:{row['ship_code']}:{row['sample_number']}",
                        "time": row["time"],
                        "cruise": cruise,
                        "reasons": _flag_labels(flags),
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "stop_latitude": row["stop_latitude"],
                        "stop_longitude": row["stop_longitude"],
                    }
                )
        else:
            months_kept[month] += 1
            cruises_kept[cruise] += 1
            split_kept[bucket] += 1

    # Whole-fixture split so 1998 can be compared to the locked boundary.
    all_split_kept: Counter[str] = Counter()
    all_split_dropped: Counter[str] = Counter()
    for row in rows:
        flags = qc_flags_for_row({key: row[key] for key in ERDDAP_FIELDS})
        bucket = _split_bucket(_parse_erddap_time(row.get("time")))
        if flags:
            all_split_dropped[bucket] += 1
        else:
            all_split_kept[bucket] += 1

    short_kept = sum(1 for event in result.events if event["short_event"])
    payload = {
        "fixture": "tests/fixtures/cufes_pilot_distances.csv",
        "fixture_rows": len(rows),
        "year": 1998,
        "rows_time_startswith_1998": len(year_rows),
        "qc_function": "fishai.ingestion.biology.cufes.transform.transform_rows",
        "events_read": int(report["events_read"]),
        "events_kept": int(report["events_kept"]),
        "dropped_rows": int(report["dropped_rows"]),
        "dropped_unique_total": int(report["dropped_unique_total"]),
        "dropped_by_rule": by_rule,
        "kept_short_event": short_kept,
        "kept_long_event": int(report["events_kept"]) - short_kept,
        "months_kept": dict(sorted(months_kept.items())),
        "months_dropped": dict(sorted(months_dropped.items())),
        "cruises_kept": dict(sorted(cruises_kept.items())),
        "cruises_dropped": dict(sorted(cruises_dropped.items())),
        "split_rule": {
            "source": "prereg/harmonization_wcofs_glorys.yaml upwelling_lags.selection",
            "fit_split_end": "2017-12-31",
            "frozen_before": "2018-01-01",
            "holdout_test_end": "2022-04-27",
        },
        "year_1998_split_kept": dict(split_kept),
        "year_1998_split_dropped": dict(split_dropped),
        "time_min": min(row["time"] for row in year_rows),
        "time_max": max(row["time"] for row in year_rows),
        "rows_with_time_on_or_after_2018": sum(
            1 for row in year_rows if str(row["time"]) >= "2018"
        ),
        "fixture_split_kept": dict(all_split_kept),
        "fixture_split_dropped": dict(all_split_dropped),
        "prompt_reference_excluded": 1171,
        "prompt_reference_retained": 1373,
        "prompt_reference_sum": 1171 + 1373,
        "dropped_examples": dropped_examples,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if out_path is None:
        sys.stdout.write(text)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"wrote {out_path} kept={payload['events_kept']} dropped={payload['dropped_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
