"""Frozen WCOFS Zarr / pull-log contract from bot2 PR #11 (read-only git ref).

Pinned to PR #11 head ``42261b4`` — do **not** merge PR #11 into ``feature/sdmtmb-core``.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.ingestion.physics.wcofs_daily import (
    build_lead_plan,
    evidence_from_forecast_age,
    forecast_age_hours,
    requested_cycle_time,
    unknown_slot_record,
)
from fishai.models.wcofs_prediction_lead import prediction_output_from_forecast_age

PR11_COMMIT = "42261b4d3b07522ff6cb30dec4f70225eaa715cb"
PR11_COMMIT_SHORT = "42261b4"
PR11_PULL = "https://github.com/wijeratne-a/fishai/pull/11"

PR11_VALID_OFFSETS_H = wcofs_src.TARGET_VALID_OFFSETS_H

# ``step_provenance_record`` @ 42261b4 (successful pulls only).
PR11_STEP_PROVENANCE_KEYS = frozenset(
    {
        "valid_offset_h",
        "requested_cycle_time",
        "source_cycle_time",
        "source_run_time",
        "valid_time",
        "forecast_age_hours",
        "fallback_used",
        "evidence_state_hint",
        "primary_cycle_available",
        "lead_tag",
    }
)

PR11_UNKNOWN_PULL_REASONS = frozenset(
    {
        "missing_operational_cycle",
        "download_failed",
        "valid_time_mismatch",
    }
)

# Per-step coordinates on packaged Zarr @ 42261b4.
PR11_ZARR_STEP_COORDS = frozenset(
    {
        "valid_offset_h",
        "time",
        "valid_time",
        "forecast_age_hours",
        "source_cycle_time",
        "source_run_time",
        "evidence_state_hint",
        "lead_days",
    }
)

REPO_ROOT = Path(__file__).resolve().parents[3]
PR11_FIXTURE_PATH = REPO_ROOT / "tests" / "models" / "fixtures" / "wcofs_pr11_contract.json"


@dataclass(frozen=True)
class SchemaMismatch:
    area: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"area": self.area, "detail": self.detail}


def _git_show(ref: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def compare_feature_branch_to_pr11(
    *, pr11_ref: str = PR11_COMMIT
) -> list[SchemaMismatch]:
    """Document remaining deltas between #5 branch and PR #11 ``pr11_ref`` (no silent merge)."""
    mismatches: list[SchemaMismatch] = []
    feat_store = (REPO_ROOT / "src/fishai/ingestion/physics/wcofs_store.py").read_text(
        encoding="utf-8"
    )
    feat_daily = (REPO_ROOT / "src/fishai/ingestion/physics/wcofs_daily.py").read_text(
        encoding="utf-8"
    )
    pr11_store = _git_show(pr11_ref, "src/fishai/ingestion/physics/wcofs_store.py")
    pr11_daily = _git_show(pr11_ref, "src/fishai/ingestion/physics/wcofs_daily.py")

    if "build_day_success_record" in feat_daily and "build_day_success_record" not in pr11_daily:
        mismatches.append(
            SchemaMismatch(
                "pull_log_record_types",
                "#5 adds day success/tombstone pull-log record types; "
                f"PR #11 {PR11_COMMIT_SHORT} pull log is step-centric only",
            )
        )

    if "source_cycle_time" in PR11_ZARR_STEP_COORDS and "source_cycle_time" not in {
        "source_run_time",
        "valid_time",
        "forecast_age_hours",
    }:
        mismatches.append(
            SchemaMismatch(
                "zarr_field_names",
                "PR #11 Zarr carries both source_cycle_time and source_run_time per step; "
                "#5 prediction viewer contract exposes source_run_time only (not source_cycle_time)",
            )
        )

    if "fallback_used" in PR11_STEP_PROVENANCE_KEYS and 'out["fallback_used"]' not in pr11_store:
        mismatches.append(
            SchemaMismatch(
                "zarr_vs_prediction_viewer",
                "fallback_used is on PR #11 step_provenance rows but not a per-step Zarr coordinate; "
                "#5 prediction output includes fallback_used on every viewer row",
            )
        )

    mismatches.append(
        SchemaMismatch(
            "dtype_lead_days",
            "PR #11 Zarr lead_days is float64 with NaN for nowcast steps; "
            "#5 prediction output lead_days is integer 0–3 (never NaN)",
        )
    )

    pr11_reasons = set(PR11_UNKNOWN_PULL_REASONS)
    if "valid_time_mismatch" in feat_daily and "valid_time_mismatch" not in pr11_reasons:
        mismatches.append(
            SchemaMismatch(
                "unknown_reason_codes",
                "#5 ingestion lists valid_time_mismatch but PR #11 ref missing that reason",
            )
        )

    if pr11_store and "source_run_time" not in pr11_store:
        mismatches.append(
            SchemaMismatch(
                "source_run_time",
                f"PR #11 {PR11_COMMIT_SHORT} wcofs_store.py missing source_run_time coord (expected on all steps)",
            )
        )

    return mismatches


def compare_feature_branch_to_pr11_a469ebf() -> list[SchemaMismatch]:
    """Backward-compatible alias — compares against PR #11 head ``42261b4``."""
    return compare_feature_branch_to_pr11()


def pr11_step_provenance_row(
    lp: Any,
    *,
    target: dt.date,
    primary_available: bool,
) -> dict[str, Any]:
    """Mirror ``step_provenance_record`` @ PR #11 ``42261b4``."""
    valid = wcofs_src.valid_time_for_lead_tag(lp.cycle_date, lp.lead_tag)
    source = wcofs_src.cycle_run_time(lp.cycle_date)
    requested = requested_cycle_time(target)
    age = forecast_age_hours(valid, lp.cycle_date)
    fallback_used = lp.cycle_date != target or lp.fallback is not None
    hint, lead_days = evidence_from_forecast_age(age, fallback_used=fallback_used)
    rec: dict[str, Any] = {
        "valid_offset_h": lp.valid_offset_h,
        "requested_cycle_time": requested.isoformat(),
        "source_cycle_time": source.isoformat(),
        "source_run_time": source.isoformat(),
        "valid_time": valid.isoformat(),
        "forecast_age_hours": age,
        "fallback_used": fallback_used,
        "evidence_state_hint": hint,
        "primary_cycle_available": primary_available,
        "lead_tag": lp.lead_tag,
    }
    if lead_days is not None:
        rec["lead_days"] = lead_days
    if lp.fallback:
        rec["fallback"] = lp.fallback
    return rec


def pr11_zarr_step_view(step: dict[str, Any]) -> dict[str, Any]:
    """Zarr per-step fields as written by ``package_wcofs_cycle`` @ ``42261b4``."""
    lead_days = float("nan")
    if "lead_days" in step:
        lead_days = float(step["lead_days"])
    return {
        "valid_offset_h": int(step["valid_offset_h"]),
        "time": step["valid_time"],
        "valid_time": step["valid_time"],
        "forecast_age_hours": float(step["forecast_age_hours"]),
        "source_cycle_time": step["source_cycle_time"],
        "source_run_time": step["source_run_time"],
        "evidence_state_hint": step["evidence_state_hint"],
        "lead_days": lead_days,
    }


def pr5_prediction_from_pr11_zarr_step(step: dict[str, Any]) -> dict[str, Any]:
    """Map one PR #11 Zarr step to PR #5 prediction output fields."""
    zarr = pr11_zarr_step_view(step)
    lead_in = zarr["lead_days"]
    if math.isnan(lead_in):
        lead_in = None
    out = prediction_output_from_forecast_age(
        zarr["forecast_age_hours"],
        fallback_used=bool(step["fallback_used"]),
        lead_days_input=lead_in,
    )
    return {
        "evidence_state": _pr5_evidence_state_label(out),
        "lead_days": int(out["lead_days"]),
        "unknown_reason": out["unknown_reason"],
        "source_run_time": step["source_run_time"],
        "forecast_age_hours": float(step["forecast_age_hours"]),
        "fallback_used": bool(step["fallback_used"]),
        "valid_time": step["valid_time"],
    }


def pr5_prediction_from_pr11_unknown_slot(slot: dict[str, Any]) -> dict[str, Any]:
    reason = str(slot["reason"])
    if reason not in PR11_UNKNOWN_PULL_REASONS:
        raise ValueError(
            f"unexpected UNKNOWN reason {reason!r}; PR11 documents {PR11_UNKNOWN_PULL_REASONS}"
        )
    out = prediction_output_from_forecast_age(
        None,
        fallback_used=False,
        unknown_reason=reason,
    )
    return {
        "evidence_state": "UNKNOWN",
        "lead_days": int(out["lead_days"]),
        "unknown_reason": reason,
        "source_run_time": None,
        "forecast_age_hours": None,
        "fallback_used": False,
        "valid_time": slot.get("valid_time"),
    }


def _pr5_evidence_state_label(resolved: dict[str, Any]) -> str:
    tier = resolved["evidence_state"]
    if tier == "NOWCAST":
        return "NOWCAST_UNVALIDATED"
    if tier == "FORECAST":
        return "FORECAST"
    if tier == "UNKNOWN":
        return "UNKNOWN"
    raise ValueError(f"unexpected tier {tier!r}")


def _plan_for_scenario(
    name: str,
    target: dt.date,
    *,
    primary_available: bool,
    cycle_exists_fn: Callable[[dt.date], bool],
) -> Any:
    return build_lead_plan(
        target,
        primary_available=primary_available,
        max_missed_cycles=2,
        cycle_exists_fn=cycle_exists_fn,
    )


def build_pr11_scenario(name: str, target: dt.date) -> dict[str, Any]:
    """Synthetic PR #11-shaped tables for contract tests."""
    if name == "normal_primary_cycle":
        plan = _plan_for_scenario(
            name, target, primary_available=True, cycle_exists_fn=lambda _d: True
        )
        sample_offsets = (-21, -3, 0, 3, 24, 72)
    elif name == "r1_fallback_previous_cycle":
        prev = target - dt.timedelta(days=1)

        def exists(d: dt.date) -> bool:
            return d == prev

        plan = _plan_for_scenario(
            name, target, primary_available=False, cycle_exists_fn=exists
        )
        sample_offsets = (-21, -3, 0, 3, 24)
    elif name == "r2_fallback_offsets_beyond_24_unknown":
        r2 = target - dt.timedelta(days=2)

        def exists(d: dt.date) -> bool:
            return d == r2

        plan = _plan_for_scenario(
            name, target, primary_available=False, cycle_exists_fn=exists
        )
        sample_offsets = tuple(range(-21, 25, 3)) + (27, 72)
    elif name == "download_failed_absent_from_zarr":
        plan = _plan_for_scenario(
            name, target, primary_available=True, cycle_exists_fn=lambda _d: True
        )
        sample_offsets = (0, 3)
    elif name == "valid_time_mismatch_absent_from_zarr":
        plan = _plan_for_scenario(
            name, target, primary_available=True, cycle_exists_fn=lambda _d: True
        )
        sample_offsets = (0, 3)
    else:
        raise ValueError(name)

    steps = {
        lp.valid_offset_h: pr11_step_provenance_row(
            lp, target=target, primary_available=plan.primary_available
        )
        for lp in plan.leads
    }
    unknown = {int(u["valid_offset_h"]): u for u in plan.unknown_slots}

    if name == "download_failed_absent_from_zarr":
        failed_offset = 3
        if failed_offset in steps:
            del steps[failed_offset]
        unknown[failed_offset] = unknown_slot_record(
            target, failed_offset, reason="download_failed"
        )
    if name == "valid_time_mismatch_absent_from_zarr":
        bad = 3
        if bad in steps:
            del steps[bad]
        unknown[bad] = unknown_slot_record(target, bad, reason="valid_time_mismatch")

    zarr_steps = [steps[o] for o in sample_offsets if o in steps]
    absent = [o for o in sample_offsets if o not in steps]
    unknown_rows = [unknown[o] for o in sample_offsets if o in unknown]

    expected: dict[str, dict[str, Any]] = {}
    for row in zarr_steps:
        off = str(row["valid_offset_h"])
        expected[off] = pr5_prediction_from_pr11_zarr_step(row)
    for row in unknown_rows:
        off = str(row["valid_offset_h"])
        expected[off] = pr5_prediction_from_pr11_unknown_slot(row)

    return {
        "name": name,
        "target_date": target.isoformat(),
        "pr11_commit": PR11_COMMIT,
        "pr11_commit_short": PR11_COMMIT_SHORT,
        "pr11_pull": PR11_PULL,
        "zarr_steps": zarr_steps,
        "zarr_absent_offsets": absent,
        "pull_log_unknown": unknown_rows,
        "expected_pr5_predictions": expected,
    }


def load_pr11_fixture() -> dict[str, Any]:
    return json.loads(PR11_FIXTURE_PATH.read_text(encoding="utf-8"))


def assert_pr11_step_schema(step: dict[str, Any]) -> None:
    missing = PR11_STEP_PROVENANCE_KEYS - set(step.keys())
    if missing:
        raise AssertionError(f"PR11 step missing keys: {sorted(missing)}")
    if not step.get("source_run_time"):
        raise AssertionError("PR11 42261b4 requires source_run_time on every successful step")


def assert_pr11_zarr_view(step: dict[str, Any]) -> None:
    view = pr11_zarr_step_view(step)
    missing = PR11_ZARR_STEP_COORDS - set(view.keys())
    if missing:
        raise AssertionError(f"PR11 Zarr view missing coords: {sorted(missing)}")
    if not view.get("source_run_time"):
        raise AssertionError("PR11 Zarr view missing source_run_time")


def assert_source_run_time_for_fallback_tier(
    scenario_name: str,
    target: dt.date,
    *,
    expected_source: dt.datetime,
) -> None:
    scenario = build_pr11_scenario(scenario_name, target)
    iso = expected_source.isoformat()
    for row in scenario["zarr_steps"]:
        assert row["source_run_time"] == iso
        view = pr11_zarr_step_view(row)
        assert view["source_run_time"] == row["source_run_time"]
