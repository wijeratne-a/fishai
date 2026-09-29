#!/usr/bin/env python3
"""
FishAI #7 overlap timestamp-verdict evidence run (661-day window).

Validates legacy same-day ``avg.nowcast`` pairing vs D+1-cycle pairing and checks
``ocean_time`` on every scheduled 3-hourly nowcast lead plus avg.nowcast metadata.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates
from fishai.ingestion.physics.wcofs_ocean_time_probe import (
    HttpRequestBudget,
    probe_avg_nowcast_ocean_time,
    probe_fields_ocean_time,
    wrap_list_keys,
)
from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix
from fishai.ingestion.physics.wcofs_utc_daily_pairing import intended_glorys_day_valid_time_utc
from fishai.physics.store import CycleNotAvailable


@dataclass(frozen=True)
class FileRef:
    kind: str  # fields | avg
    cycle: dt.date
    lead: str | None = None

    def cache_key(self) -> str:
        if self.kind == "avg":
            return f"avg:{self.cycle.isoformat()}"
        return f"fields:{self.cycle.isoformat()}:{self.lead}"


def _utc_naive(ts: dt.datetime) -> dt.datetime:
    if ts.tzinfo is not None:
        return ts.astimezone(dt.timezone.utc).replace(tzinfo=None)
    return ts


def _offset_hours(got: dt.datetime, want: dt.datetime) -> float:
    return abs((_utc_naive(got) - _utc_naive(want)).total_seconds()) / 3600.0


def nowcast_slots_for_glorys_day(day: dt.date) -> list[tuple[dt.date, str, dt.datetime]]:
    """Three-hourly nowcast fields whose valid time falls on UTC calendar ``day``."""
    slots: list[tuple[dt.date, str, dt.datetime]] = []
    for lead in wcofs_src.NOWCAST_LEADS:
        for cycle in (day, day + dt.timedelta(days=1)):
            expected = wcofs_src.valid_time_for_lead_tag(cycle, lead)
            if expected.date() == day:
                slots.append((cycle, lead, expected))
    return slots


def _probe_one(
    ref: FileRef,
    list_keys,
    budget: HttpRequestBudget,
) -> tuple[FileRef, dt.datetime | None, str | None, str | None]:
    try:
        if ref.kind == "avg":
            when, key = probe_avg_nowcast_ocean_time(ref.cycle, list_keys, budget=budget)
        else:
            assert ref.lead is not None
            when, key = probe_fields_ocean_time(ref.cycle, ref.lead, list_keys, budget=budget)
        return ref, when, key, None
    except CycleNotAvailable as exc:
        return ref, None, None, str(exc)
    except Exception as exc:  # noqa: BLE001
        return ref, None, None, f"{type(exc).__name__}: {exc}"


def run_evidence(*, max_http_requests: int | None) -> dict[str, Any]:
    config = load_overlap_config()
    days = overlap_dates(config)
    budget = HttpRequestBudget()
    list_keys = wrap_list_keys(list_keys_under_prefix, budget)

    field_slot_index: dict[tuple[dt.date, str], list[tuple[dt.date, dt.datetime]]] = defaultdict(
        list
    )
    field_refs: list[FileRef] = []
    for day in days:
        for cycle, lead, expected in nowcast_slots_for_glorys_day(day):
            field_slot_index[(cycle, lead)].append((day, expected))
            field_refs.append(FileRef(kind="fields", cycle=cycle, lead=lead))

    legacy_avg_refs = [FileRef(kind="avg", cycle=day) for day in days]
    new_avg_refs = [FileRef(kind="avg", cycle=day + dt.timedelta(days=1)) for day in days]

    seen: set[str] = set()
    unique_refs: list[FileRef] = []
    for ref in field_refs + legacy_avg_refs + new_avg_refs:
        key = ref.cache_key()
        if key in seen:
            continue
        seen.add(key)
        unique_refs.append(ref)

    ocean_times: dict[str, tuple[dt.datetime | None, str | None, str | None]] = {}

    def maybe_stop() -> bool:
        return max_http_requests is not None and budget.total >= max_http_requests

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(_probe_one, ref, list_keys, budget) for ref in unique_refs]
        for fut in as_completed(futures):
            ref, when, s3_key, err = fut.result()
            ocean_times[ref.cache_key()] = (when, s3_key, err)
            if maybe_stop():
                break

    # --- 3-hourly nowcast fields (rebuilt overlap physics path) ---
    day_fields_ok = 0
    day_fields_missing = 0
    day_fields_mismatch = 0
    slot_exact = 0
    slot_mismatch = 0
    slot_missing = 0
    max_slot_offset_h = 0.0
    mismatch_examples: list[dict[str, Any]] = []
    missing_examples: list[dict[str, Any]] = []
    dplus1_cycle_days = 0

    for day in days:
        slots = nowcast_slots_for_glorys_day(day)
        dplus1 = day + dt.timedelta(days=1)
        if any(cycle == dplus1 for cycle, _lead, _exp in slots):
            has_dplus1_file = all(
                ocean_times.get(FileRef(kind="fields", cycle=cycle, lead=lead).cache_key(), (None, None, None))[
                    0
                ]
                is not None
                for cycle, lead, _exp in slots
                if cycle == dplus1
            )
            if has_dplus1_file:
                dplus1_cycle_days += 1

        day_ok = True
        day_missing = False
        for cycle, lead, expected in slots:
            ref = FileRef(kind="fields", cycle=cycle, lead=lead)
            when, _key, err = ocean_times.get(ref.cache_key(), (None, None, "not_probed"))
            if when is None:
                slot_missing += 1
                day_missing = True
                day_ok = False
                if len(missing_examples) < 10:
                    missing_examples.append(
                        {
                            "day": day.isoformat(),
                            "cycle": cycle.isoformat(),
                            "lead": lead,
                            "reason": err or "missing_on_server",
                        }
                    )
                continue
            if _utc_naive(when) == _utc_naive(expected):
                slot_exact += 1
            else:
                slot_mismatch += 1
                day_ok = False
                off = _offset_hours(when, expected)
                max_slot_offset_h = max(max_slot_offset_h, off)
                if len(mismatch_examples) < 10:
                    mismatch_examples.append(
                        {
                            "day": day.isoformat(),
                            "cycle": cycle.isoformat(),
                            "lead": lead,
                            "expected": expected.isoformat(),
                            "ocean_time": when.isoformat(),
                            "offset_hours": off,
                            "reason": "valid_time_mismatch",
                        }
                    )

        if day_ok:
            day_fields_ok += 1
        elif day_missing:
            day_fields_missing += 1
        else:
            day_fields_mismatch += 1

    # --- legacy same-day avg.nowcast (old overlap table) ---
    legacy_cycle_present = 0
    legacy_intended_exact = 0
    legacy_wrong_day = 0
    legacy_missing = 0
    legacy_mismatch_examples: list[dict[str, Any]] = []

    for day in days:
        ref = FileRef(kind="avg", cycle=day)
        when, _key, err = ocean_times.get(ref.cache_key(), (None, None, "not_probed"))
        if when is None:
            legacy_missing += 1
            continue
        legacy_cycle_present += 1
        intended = intended_glorys_day_valid_time_utc(day)
        if _utc_naive(when) == _utc_naive(intended):
            legacy_intended_exact += 1
        else:
            legacy_wrong_day += 1
            if len(legacy_mismatch_examples) < 6:
                legacy_mismatch_examples.append(
                    {
                        "day": day.isoformat(),
                        "cycle": day.isoformat(),
                        "ocean_time": when.isoformat(),
                        "intended_for_glorys_day": intended.isoformat(),
                        "offset_hours": _offset_hours(when, intended),
                        "reason": "valid_time_mismatch",
                    }
                )

    # --- D+1 avg.nowcast metadata (rebuilt overlap WCOFS source cycle) ---
    new_avg_present = 0
    new_avg_exact = 0
    new_avg_mismatch = 0
    new_avg_missing = 0
    new_avg_mismatch_examples: list[dict[str, Any]] = []

    for day in days:
        ref = FileRef(kind="avg", cycle=day + dt.timedelta(days=1))
        when, _key, err = ocean_times.get(ref.cache_key(), (None, None, "not_probed"))
        if when is None:
            new_avg_missing += 1
            continue
        new_avg_present += 1
        intended = intended_glorys_day_valid_time_utc(day)
        if _utc_naive(when) == _utc_naive(intended):
            new_avg_exact += 1
        else:
            new_avg_mismatch += 1
            if len(new_avg_mismatch_examples) < 6:
                new_avg_mismatch_examples.append(
                    {
                        "day": day.isoformat(),
                        "cycle": (day + dt.timedelta(days=1)).isoformat(),
                        "ocean_time": when.isoformat(),
                        "intended_for_glorys_day": intended.isoformat(),
                        "offset_hours": _offset_hours(when, intended),
                    }
                )

    return {
        "git_sha": "678b853500cee8308975fcbebcb10b1b09695d34",
        "evidence_branch_sha": "01583fb",
        "overlap_days_attempted": len(days),
        "http_requests": {
            "list": budget.list_requests,
            "get": budget.get_requests,
            "total": budget.total,
            "max_configured_per_day": int(
                (config.get("rate_limits") or {}).get("max_requests_per_day", 200)
            ),
            "unique_files_targeted": len(unique_refs),
            "unique_files_probed": len(ocean_times),
            "probe_incomplete": len(ocean_times) < len(unique_refs),
        },
        "rebuilt_nowcast_fields_pairing": {
            "slots_per_day": 8,
            "days_all_slots_ocean_time_exact": day_fields_ok,
            "days_with_any_missing_lead": day_fields_missing,
            "days_with_valid_time_mismatch": day_fields_mismatch,
            "days_with_dplus1_cycle_and_all_dplus1_leads_present": dplus1_cycle_days,
            "slots_exact": slot_exact,
            "slots_valid_time_mismatch": slot_mismatch,
            "slots_missing": slot_missing,
            "max_slot_offset_hours": max_slot_offset_h,
            "mismatch_examples": mismatch_examples,
            "missing_examples": missing_examples,
        },
        "legacy_same_day_avg_nowcast_table": {
            "days_avg_nowcast_on_server": legacy_cycle_present,
            "days_ocean_time_matches_intended_glorys_day": legacy_intended_exact,
            "days_valid_time_mismatch_vs_glorys_day": legacy_wrong_day,
            "days_missing_avg_nowcast": legacy_missing,
            "mismatch_examples": legacy_mismatch_examples,
        },
        "rebuilt_dplus1_avg_nowcast_table": {
            "days_cycle_d_plus_1_on_server": new_avg_present,
            "days_ocean_time_exact_at_15z_on_d": new_avg_exact,
            "days_valid_time_mismatch": new_avg_mismatch,
            "days_missing_cycle_d_plus_1": new_avg_missing,
            "mismatch_examples": new_avg_mismatch_examples,
        },
        "before_after_summary": {
            "old_table_days_with_same_day_avg_on_server": legacy_cycle_present,
            "old_table_days_timestamp_ok_for_glorys_day_d": legacy_intended_exact,
            "old_table_days_timestamp_mismatch": legacy_wrong_day,
            "new_avg_dplus1_days_timestamp_ok": new_avg_exact,
            "new_fields_days_all_eight_leads_ok": day_fields_ok,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-http-requests",
        type=int,
        default=None,
        help="Optional cap on LIST+GET requests",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write JSON report (not committed)",
    )
    args = parser.parse_args(argv)
    report = run_evidence(max_http_requests=args.max_http_requests)
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.json_out is not None:
        args.json_out.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
