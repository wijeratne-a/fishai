#!/usr/bin/env python3
"""
FishAI #7 overlap timestamp-verdict evidence run (661-day window).

Compares legacy same-day ``avg.nowcast`` pairing to UTC hourly fields pairing
(D+1 cycle for hours 04–23Z) and checks ``ocean_time`` on every scheduled lead.
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

from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates
from fishai.ingestion.physics.wcofs_ocean_time_probe import (
    HttpRequestBudget,
    probe_avg_nowcast_ocean_time,
    probe_fields_ocean_time,
    wrap_list_keys,
)
from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix
from fishai.ingestion.physics.wcofs_utc_daily_pairing import (
    hourly_fields_slots_for_utc_day,
    intended_glorys_day_valid_time_utc,
)
from fishai.physics.store import CycleNotAvailable


@dataclass(frozen=True)
class FileRef:
    cycle: dt.date
    lead: str | None  # None => avg.nowcast

    def cache_key(self) -> str:
        if self.lead is None:
            return f"avg:{self.cycle.isoformat()}"
        return f"fields:{self.cycle.isoformat()}:{self.lead}"


def _utc_naive(ts: dt.datetime) -> dt.datetime:
    if ts.tzinfo is not None:
        return ts.astimezone(dt.timezone.utc).replace(tzinfo=None)
    return ts


def _offset_hours(got: dt.datetime, want: dt.datetime) -> float:
    return abs((_utc_naive(got) - _utc_naive(want)).total_seconds()) / 3600.0


def _build_slot_index(days: list[dt.date]) -> dict[FileRef, list[tuple[dt.date, dt.datetime]]]:
    index: dict[FileRef, list[tuple[dt.date, dt.datetime]]] = defaultdict(list)
    for day in days:
        for slot in hourly_fields_slots_for_utc_day(day):
            ref = FileRef(cycle=slot.cycle, lead=slot.lead)
            index[ref].append((day, slot.expected_valid_time_utc))
    return index


def _probe_one(
    ref: FileRef,
    list_keys,
    budget: HttpRequestBudget,
) -> tuple[FileRef, dt.datetime | None, str | None, str | None]:
    try:
        if ref.lead is None:
            when, key = probe_avg_nowcast_ocean_time(ref.cycle, list_keys, budget=budget)
        else:
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

    slot_index = _build_slot_index(days)
    fields_refs = sorted(
        (ref for ref in slot_index if ref.lead is not None),
        key=lambda r: (r.cycle, r.lead or ""),
    )

    # Legacy avg.nowcast: one file per target day D from cycle D (same-day).
    legacy_avg_refs = [FileRef(cycle=day, lead=None) for day in days]
    # Correct avg.nowcast anchor: cycle D+1 for GLORYS calendar day D.
    new_avg_refs = [FileRef(cycle=day + dt.timedelta(days=1), lead=None) for day in days]

    ocean_times: dict[str, tuple[dt.datetime | None, str | None, str | None]] = {}

    def maybe_stop() -> bool:
        return max_http_requests is not None and budget.total >= max_http_requests

    all_refs = fields_refs + legacy_avg_refs + new_avg_refs
    seen: set[str] = set()
    unique_refs: list[FileRef] = []
    for ref in all_refs:
        key = ref.cache_key()
        if key in seen:
            continue
        seen.add(key)
        unique_refs.append(ref)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(_probe_one, ref, list_keys, budget): ref for ref in unique_refs
        }
        for fut in as_completed(futures):
            ref, when, s3_key, err = fut.result()
            ocean_times[ref.cache_key()] = (when, s3_key, err)
            if maybe_stop():
                for pending in futures:
                    pending.cancel()
                break

    # --- hourly UTC rebuild (fields) ---
    day_hourly_ok = 0
    day_hourly_partial = 0
    day_hourly_missing = 0
    slot_exact = 0
    slot_mismatch = 0
    slot_missing = 0
    max_slot_offset_h = 0.0
    mismatch_examples: list[dict[str, Any]] = []
    missing_examples: list[dict[str, Any]] = []
    dplus1_cycle_days = 0

    for day in days:
        slots = hourly_fields_slots_for_utc_day(day)
        dplus1 = day + dt.timedelta(days=1)
        dplus1_present = all(
            ocean_times.get(FileRef(cycle=dplus1, lead=f"n{h - 3:03d}").cache_key(), (None, None, None))[0]
            is not None
            for h in range(4, 24)
        )
        if dplus1_present:
            dplus1_cycle_days += 1

        day_ok = True
        day_has_missing = False
        for slot in slots:
            ref = FileRef(cycle=slot.cycle, lead=slot.lead)
            when, _key, err = ocean_times.get(ref.cache_key(), (None, None, "not_probed"))
            if when is None:
                slot_missing += 1
                day_has_missing = True
                day_ok = False
                if len(missing_examples) < 8:
                    missing_examples.append(
                        {
                            "day": day.isoformat(),
                            "cycle": slot.cycle.isoformat(),
                            "lead": slot.lead,
                            "reason": err or "missing_on_server",
                        }
                    )
                continue
            want = slot.expected_valid_time_utc
            if _utc_naive(when) == _utc_naive(want):
                slot_exact += 1
            else:
                slot_mismatch += 1
                day_ok = False
                off = _offset_hours(when, want)
                max_slot_offset_h = max(max_slot_offset_h, off)
                if len(mismatch_examples) < 8:
                    mismatch_examples.append(
                        {
                            "day": day.isoformat(),
                            "cycle": slot.cycle.isoformat(),
                            "lead": slot.lead,
                            "expected": want.isoformat(sep="T"),
                            "ocean_time": when.isoformat(),
                            "offset_hours": off,
                        }
                    )

        if day_ok:
            day_hourly_ok += 1
        elif day_has_missing:
            day_hourly_missing += 1
        else:
            day_hourly_partial += 1

    # --- legacy same-day avg.nowcast (old overlap table) ---
    legacy_cycle_present = 0
    legacy_intended_exact = 0
    legacy_wrong_day = 0
    legacy_missing = 0
    legacy_mismatch_examples: list[dict[str, Any]] = []

    for day in days:
        ref = FileRef(cycle=day, lead=None)
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
            if len(legacy_mismatch_examples) < 5:
                legacy_mismatch_examples.append(
                    {
                        "day": day.isoformat(),
                        "cycle": day.isoformat(),
                        "ocean_time": when.isoformat(),
                        "intended_for_glorys_day": intended.isoformat(),
                        "offset_hours": _offset_hours(when, intended),
                    }
                )

    # --- new D+1 avg.nowcast metadata guard ---
    new_avg_present = 0
    new_avg_exact = 0
    new_avg_mismatch = 0
    new_avg_missing = 0

    for day in days:
        ref = FileRef(cycle=day + dt.timedelta(days=1), lead=None)
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

    incomplete_probe = maybe_stop() or len(ocean_times) < len(unique_refs)

    return {
        "git_sha": "678b853500cee8308975fcbebcb10b1b09695d34",
        "overlap_days_attempted": len(days),
        "http_requests": {
            "list": budget.list_requests,
            "get_range": budget.get_requests,
            "total": budget.total,
            "max_configured_per_day": int(
                (config.get("rate_limits") or {}).get("max_requests_per_day", 200)
            ),
            "probe_incomplete": incomplete_probe,
            "unique_files_targeted": len(unique_refs),
            "unique_files_probed": len(ocean_times),
        },
        "hourly_utc_fields_rebuild": {
            "days_all_24_ocean_time_exact": day_hourly_ok,
            "days_with_any_missing_lead": day_hourly_missing,
            "days_with_mismatch_only": day_hourly_partial,
            "days_with_dplus1_cycle_hours_04_23_present": dplus1_cycle_days,
            "slots_exact": slot_exact,
            "slots_mismatch": slot_mismatch,
            "slots_missing": slot_missing,
            "max_slot_offset_hours": max_slot_offset_h,
            "mismatch_examples": mismatch_examples,
            "missing_examples": missing_examples,
        },
        "legacy_same_day_avg_nowcast_table": {
            "days_cycle_file_on_server": legacy_cycle_present,
            "days_ocean_time_matches_intended_glorys_day": legacy_intended_exact,
            "days_ocean_time_mismatch_vs_glorys_day": legacy_wrong_day,
            "days_missing_avg_nowcast": legacy_missing,
            "mismatch_examples": legacy_mismatch_examples,
            "note": (
                "Legacy overlap opened avg.nowcast for cycle D when pairing GLORYS day D; "
                "intended valid time is 15:00 UTC on calendar day D (cycle D+1 product)."
            ),
        },
        "dplus1_avg_nowcast_metadata": {
            "days_cycle_d_plus_1_on_server": new_avg_present,
            "days_ocean_time_exact_at_15z_on_d": new_avg_exact,
            "days_mismatch": new_avg_mismatch,
            "days_missing_cycle": new_avg_missing,
        },
        "before_after_summary": {
            "old_table_would_pair_days_with_same_day_cycle": legacy_cycle_present,
            "old_table_timestamp_valid_for_glorys_day": legacy_intended_exact,
            "new_hourly_table_fully_valid_days": day_hourly_ok,
            "new_dplus1_avg_metadata_valid_days": new_avg_exact,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-http-requests",
        type=int,
        default=None,
        help="Optional cap on LIST+GET requests (default: no cap; full 661-day evidence)",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write JSON report to this path (not committed)",
    )
    args = parser.parse_args(argv)
    report = run_evidence(max_http_requests=args.max_http_requests)
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
