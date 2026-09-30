#!/usr/bin/env python3
"""Join per-cycle WCOFS ocean_time reads to GLORYS daily time coordinates.

Inputs are JSONL produced by inspect_overlap_ocean_times.py and a GLORYS
time-coordinate JSONL (one object per calendar day). Writes the pairing table.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fishai.ingestion.physics.wcofs_glorys_overlap import (  # noqa: E402
    load_overlap_config,
    overlap_dates,
    wcofs_cycle_date_for_glorys_day,
)


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _parse(stamp: str) -> dt.datetime:
    text = stamp.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _hours(left: dt.datetime, right: dt.datetime) -> float:
    return (left - right).total_seconds() / 3600.0


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "usage: build_overlap_cycle_pairing_table.py WCOFS.jsonl GLORYS.jsonl OUT.jsonl",
            file=sys.stderr,
        )
        return 2
    wcofs_rows = _load_jsonl(Path(sys.argv[1]))
    glorys_rows = _load_jsonl(Path(sys.argv[2]))
    out_path = Path(sys.argv[3])
    by_cycle = {row["cycle_date"]: row for row in wcofs_rows}
    by_glorys = {row["glorys_day"]: row for row in glorys_rows}
    cfg = load_overlap_config()
    days = overlap_dates(cfg)
    table: list[dict] = []
    for day in days:
        cycle = wcofs_cycle_date_for_glorys_day(day, cfg)
        same = by_cycle[day.isoformat()]
        nxt = by_cycle[cycle.isoformat()]
        glorys = by_glorys[day.isoformat()]
        glorys_time = _parse(glorys["glorys_time_utc"])
        same_time = _parse(same["ocean_time_utc"])
        next_time = _parse(nxt["ocean_time_utc"])
        noon = dt.datetime.combine(day, dt.time(12, 0), tzinfo=dt.timezone.utc)
        table.append(
            {
                "glorys_day": day.isoformat(),
                "glorys_dataset_id": glorys["dataset_id"],
                "glorys_dataset_version": glorys["dataset_version"],
                "glorys_time_utc": glorys_time.isoformat(),
                "glorys_time_hours_since_1950_01_01": glorys["hours_since_1950_01_01"],
                "glorys_time_units": glorys["units"],
                "glorys_calendar": glorys["calendar"],
                "wcofs_cycle_date": cycle.isoformat(),
                "wcofs_s3_key": nxt["s3_key"],
                "wcofs_content_length": nxt["content_length"],
                "wcofs_ocean_time_utc": next_time.isoformat(),
                "wcofs_ocean_time_seconds": nxt["ocean_time_seconds"],
                "wcofs_ocean_time_units": nxt["ocean_time_units"],
                "same_day_cycle_date": day.isoformat(),
                "same_day_s3_key": same["s3_key"],
                "same_day_ocean_time_utc": same_time.isoformat(),
                "same_day_ocean_time_seconds": same["ocean_time_seconds"],
                "hours_same_day_minus_glorys_time": _hours(same_time, glorys_time),
                "hours_next_cycle_minus_glorys_time": _hours(next_time, glorys_time),
                "hours_same_day_minus_calendar_noon": _hours(same_time, noon),
                "hours_next_cycle_minus_calendar_noon": _hours(next_time, noon),
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in table),
        encoding="utf-8",
    )
    summary = {
        "n_glorys_days": len(table),
        "n_wcofs_cycles_read": len(by_cycle),
        "same_day_minus_glorys_time_hours": dict(
            Counter(row["hours_same_day_minus_glorys_time"] for row in table)
        ),
        "next_cycle_minus_glorys_time_hours": dict(
            Counter(row["hours_next_cycle_minus_glorys_time"] for row in table)
        ),
        "same_day_minus_noon_hours": dict(
            Counter(row["hours_same_day_minus_calendar_noon"] for row in table)
        ),
        "next_cycle_minus_noon_hours": dict(
            Counter(row["hours_next_cycle_minus_calendar_noon"] for row in table)
        ),
        "wcofs_clocks": dict(Counter(row["wcofs_ocean_time_utc"][11:19] for row in table)),
        "same_day_clocks": dict(
            Counter(row["same_day_ocean_time_utc"][11:19] for row in table)
        ),
        "glorys_clocks": dict(Counter(row["glorys_time_utc"][11:19] for row in table)),
    }
    summary_path = out_path.with_name(out_path.stem + "_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"wrote {out_path} rows={len(table)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
