#!/usr/bin/env python3
"""Score one new environmental variable once on locked 2023 after freezing on 2016–2021.

Does not rerun the MUR SST comparison. Does not write a globe layer.
OISST is scored only as a robustness check of a second SST product.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "modeling"))
sys.path.insert(0, str(ROOT / "scripts" / "acquisition"))

from run_puerto_rico_prediction_test import (  # noqa: E402
    HOLDOUT_YEAR,
    PUBLICATION_STATUS,
    RANDOM_SEED,
    SST_CALIBRATION_TOL,
    SST_TRAIN_MISSING_MAX,
    SPECIES,
    TRAIN_YEARS,
    accept_sst_model,
    build_labeled_rows,
    load_puerto_rico_events,
    required_paths,
    score_holdout,
)
from write_run_manifest import build_manifest, write_manifest  # noqa: E402

OISST_META = ROOT / "data" / "restricted" / "environmental" / "ncdcOisst21Agg_LonPM180" / "JOIN_META.json"
DEPTH_SEARCH = ROOT / "audit" / "predictors" / "DEPTH_TEMPERATURE_SEARCH.json"
OUT = ROOT / "audit" / "prediction-test" / "ENVIRONMENTAL_DECISION.md"
JSON_OUT = ROOT / "audit" / "prediction-test" / "ENVIRONMENTAL_DECISION.json"
MANIFEST_OUT = ROOT / "audit" / "prediction-test" / "OISST_ROBUSTNESS_RUN_MANIFEST.json"


def load_oisst_by_date() -> dict[str, float]:
    cache = ROOT / "data" / "restricted" / "environmental" / "ncdcOisst21Agg_LonPM180" / "by-date"
    values: dict[str, float] = {}
    if not cache.is_dir():
        return values
    for path in cache.glob("*.json"):
        info = json.loads(path.read_text(encoding="utf-8"))
        if info.get("status") == "ok" and info.get("mean_sst") is not None:
            values[info["date"]] = float(info["mean_sst"])
    return values


def freeze_on_train(events: dict, oisst: dict[str, float]) -> dict:
    """Freeze missingness and offset policy on 2016–2021 only. Do not look at 2023."""
    train = [rec for rec in events.values() if rec.get("year") in TRAIN_YEARS]
    n = 0
    missing = 0
    for rec in train:
        n += 1
        day = rec.get("date")
        if not day or day not in oisst:
            missing += 1
    missing_fraction = missing / n if n else 1.0
    frozen = {
        "variable": "ncdcOisst21Agg_LonPM180.sst",
        "frozen_on_years": list(TRAIN_YEARS),
        "holdout_year_not_used_to_choose": HOLDOUT_YEAR,
        "offset_days": 2,
        "allowed_offsets": [0, -1, -2],
        "future_day_offsets_forbidden": True,
        "units": "degree_celsius",
        "train_missing_fraction": round(missing_fraction, 6),
        "eligible": missing_fraction < SST_TRAIN_MISSING_MAX,
        "frozen_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return frozen


def attach_oisst(events: dict, oisst: dict[str, float]) -> None:
    for rec in events.values():
        rec["sst"] = oisst.get(rec.get("date") or "")


def decide() -> dict:
    depth = {}
    if DEPTH_SEARCH.is_file():
        depth = json.loads(DEPTH_SEARCH.read_text(encoding="utf-8"))
    join = {}
    if OISST_META.is_file():
        join = json.loads(OISST_META.read_text(encoding="utf-8"))

    events, universe = load_puerto_rico_events(required_paths())
    oisst = load_oisst_by_date()
    frozen = freeze_on_train(events, oisst)

    decision = "SST_ADDS_NO_VALUE"
    species_rows = []
    scored = False
    reason = "new_variable_not_frozen_or_not_eligible"

    depth_status = depth.get("coverage_status", "HISTORICAL_COVERAGE_FAILED")
    if depth_status != "DATASET_ID_VERIFIED_NOT_JOINED" or not depth.get("chosen"):
        depth_note = "HISTORICAL_COVERAGE_FAILED or ID only; not joined; not scored as bottom temperature."
    else:
        depth_note = f"dataset_id={(depth.get('chosen') or {}).get('dataset_id')}; not joined; SST was not used as bottom temperature."

    if frozen["eligible"] and oisst:
        attach_oisst(events, oisst)
        scored = True
        any_accept = True
        for code, name in SPECIES:
            rows = build_labeled_rows(events, universe, code, require_sst=True)
            train = [r for r in rows if r["year"] in TRAIN_YEARS]
            test = [r for r in rows if r["year"] == HOLDOUT_YEAR]
            survey_rows = build_labeled_rows(events, universe, code, require_sst=False)
            survey_train = [r for r in survey_rows if r["year"] in TRAIN_YEARS]
            survey_test = [r for r in survey_rows if r["year"] == HOLDOUT_YEAR]
            counts: dict[str, int] = {}
            for rec in train:
                counts[rec["habitat"]] = counts.get(rec["habitat"], 0) + 1
            habitats = [h for h, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:6]]
            years = sorted({r["year"] for r in train})
            survey = score_holdout(survey_train, survey_test, habitats, years, include_sst=False)
            env = score_holdout(train, test, habitats, years, include_sst=True)
            accepted = accept_sst_model(
                survey["holdout_brier_model"],
                survey["holdout_logloss_model"],
                env["holdout_brier_model"],
                env["holdout_logloss_model"],
                env["mean_predicted_probability"],
                env["holdout_prevalence"],
            )
            any_accept = any_accept and accepted
            species_rows.append(
                {
                    "species_code": code,
                    "scientific_name": name,
                    "survey_brier": round(survey["holdout_brier_model"], 6),
                    "env_brier": round(env["holdout_brier_model"], 6),
                    "survey_logloss": round(survey["holdout_logloss_model"], 6),
                    "env_logloss": round(env["holdout_logloss_model"], 6),
                    "calibration_gap": round(env["calibration_gap"], 6),
                    "accepted": accepted,
                }
            )
        decision = "OISST_ACCEPTED" if any_accept else "SST_ADDS_NO_VALUE"
        reason = "oisst_robustness_scored_once_after_freeze"
    elif not oisst:
        reason = "oisst_not_matched"
        decision = "SST_ADDS_NO_VALUE"

    payload = {
        "label": "INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED",
        "decision": decision,
        "reason": reason,
        "frozen": frozen,
        "mur_rescored": False,
        "scored": scored,
        "species": species_rows,
        "depth_temperature": depth_note,
        "oisst_join_missing_fraction": join.get("missing_fraction"),
        "publication": PUBLICATION_STATUS,
        "on_the_globe": False,
        "nowcast_milestone": "CLOSED",
        "nowcast_status": "NEEDS_MORE_ENVIRONMENTAL_COVERAGE"
        if decision != "OISST_ACCEPTED"
        else "OPEN_FOR_INTERNAL_NOWCAST_RESEARCH",
        "random_seed": RANDOM_SEED,
    }
    return payload


def write_report(payload: dict) -> None:
    lock = ROOT / "audit" / "prediction-test" / "RESULTS_LOCKED"
    if lock.is_file():
        raise RuntimeError(
            "RESULTS_LOCKED: refuse to overwrite inspected-holdout environmental decision"
        )
    lines = [
        "ENVIRONMENTAL DECISION:",
        f"DECISION: {payload['decision']}",
        f"MUR RESCORED: NO",
        f"SCORED NEW VARIABLE: {'YES' if payload['scored'] else 'NO'}",
        f"VARIABLE: ncdcOisst21Agg_LonPM180.sst (robustness only)",
        f"FROZEN ON: {', '.join(str(y) for y in TRAIN_YEARS)}",
        f"HOLDOUT SCORED ONCE: {HOLDOUT_YEAR}",
        f"DEPTH TEMPERATURE: {payload['depth_temperature']}",
        f"PUBLICATION: {payload['publication']}",
        "ON THE GLOBE: NO",
        f"NOWCAST MILESTONE: {payload['nowcast_milestone']}",
        f"NOWCAST STATUS: {payload['nowcast_status']}",
        "",
        "# Environmental decision",
        "",
        "**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**",
        "",
        f"Decision: `{payload['decision']}`. MUR SST was not rescored. "
        "OISST was eligible only after the join rule was frozen on 2016–2021.",
        "",
    ]
    if payload["species"]:
        lines += [
            "| Species | Survey Brier | OISST Brier | Survey log loss | OISST log loss | Calibration gap | Accepted |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
        for row in payload["species"]:
            lines.append(
                f"| {row['species_code']} | {row['survey_brier']:.6f} | {row['env_brier']:.6f} | "
                f"{row['survey_logloss']:.6f} | {row['env_logloss']:.6f} | {row['calibration_gap']:.6f} | "
                f"{'yes' if row['accepted'] else 'no'} |"
            )
        lines.append("")
    lines.append("No public globe layer was written.")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    JSON_OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    payload = decide()
    write_report(payload)
    manifest = build_manifest(
        experiment_id="pr_oisst_robustness_once",
        random_seed=RANDOM_SEED,
        train_years=list(TRAIN_YEARS),
        holdout_year=HOLDOUT_YEAR,
        input_paths=[p for p in required_paths() if p.is_file()],
        notes="OISST robustness score after freeze on 2016-2021. Not a MUR rescore. NOT_PUBLISHED.",
    )
    write_manifest(MANIFEST_OUT, manifest)
    print(f"decision={payload['decision']}")
    print(f"scored={payload['scored']}")
    print("on_the_globe=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
