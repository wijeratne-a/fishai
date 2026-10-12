"""Market squid CPS encounter rows (all sizes; no length gate — not an adult model)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from fishai.ingestion.adult.constants import (
    EVIDENCE_IMPLIED_ZERO,
    OBSERVATION_SOURCE_NEARSHORE,
    OBSERVATION_SOURCE_TRAWL,
)
from fishai.ingestion.adult.observations import (
    _encounter_from_measurements,
    _enumerated_events_and_species,
    _nearshore_catch_row_species,
    _nearshore_row_has_species_catch,
    _nearshore_row_is_enumerated,
    _trawl_catch_row_species,
    _trawl_row_has_species_catch,
    _trawl_row_is_enumerated,
)
from fishai.ingestion.biology.cps_trawl.catch import is_presence_only

MARKET_SQUID_CANONICAL: str = "Doryteuthis opalescens"
MARKET_SQUID_ALIASES: frozenset[str] = frozenset(
    {MARKET_SQUID_CANONICAL, "Loligo opalescens"},
)

ENCOUNTER_LABEL: str = (
    "squid encounter (all sizes; maturity unfiltered — no length data)"
)


def _match_squid(name: str) -> bool:
    return str(name or "").strip() in MARKET_SQUID_ALIASES


def build_trawl_squid_encounters(catch: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    stats = {
        "input_rows": 0,
        "presence_only_excluded": 0,
        "non_target_species_skipped": 0,
        "rows_kept": 0,
    }
    rows: list[dict[str, Any]] = []
    if catch.empty:
        return pd.DataFrame(), stats
    for _, row in catch.iterrows():
        stats["input_rows"] += 1
        if is_presence_only(row.get("presence_only")):
            stats["presence_only_excluded"] += 1
            continue
        species = str(row.get("species") or row.get("scientific_name") or "").strip()
        if not _match_squid(species):
            stats["non_target_species_skipped"] += 1
            continue
        weight = row.get("weight_kg")
        weight_f = float(weight) if weight is not None and pd.notna(weight) else None
        count_raw = row.get("count_raised_est")
        if count_raw is None or pd.isna(count_raw):
            count_raw = row.get("subsample_count")
        count = int(count_raw) if count_raw is not None and pd.notna(count_raw) else None
        rows.append(
            {
                "event_id": str(row["haul_id"]),
                "species": MARKET_SQUID_CANONICAL,
                "observation_source": OBSERVATION_SOURCE_TRAWL,
                "encounter": _encounter_from_measurements(weight_kg=weight_f, count=count),
                "weight_kg": weight_f,
                "count_observed": count,
                "adult_median_length_mm": None,
                "biology_excluded": False,
                "biology_excluded_reason": "",
                "encounter_semantics": ENCOUNTER_LABEL,
            }
        )
        stats["rows_kept"] += 1
    return pd.DataFrame(rows), stats


def build_nearshore_squid_encounters(catch: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    stats = {
        "input_rows": 0,
        "non_target_species_skipped": 0,
        "rows_kept": 0,
    }
    rows: list[dict[str, Any]] = []
    if catch.empty:
        return pd.DataFrame(), stats
    for _, row in catch.iterrows():
        stats["input_rows"] += 1
        species = str(row.get("scientific_name") or row.get("species") or "").strip()
        if not _match_squid(species):
            stats["non_target_species_skipped"] += 1
            continue
        weight = row.get("total_weight_kg")
        weight_f = float(weight) if weight is not None and pd.notna(weight) else None
        count_raw = row.get("total_number")
        count = int(count_raw) if count_raw is not None and pd.notna(count_raw) else None
        rows.append(
            {
                "event_id": str(row["set_id"]),
                "species": MARKET_SQUID_CANONICAL,
                "observation_source": OBSERVATION_SOURCE_NEARSHORE,
                "encounter": _encounter_from_measurements(weight_kg=weight_f, count=count),
                "weight_kg": weight_f,
                "count_observed": count,
                "adult_median_length_mm": None,
                "biology_excluded": False,
                "biology_excluded_reason": "",
                "encounter_semantics": ENCOUNTER_LABEL,
            }
        )
        stats["rows_kept"] += 1
    return pd.DataFrame(rows), stats


def append_squid_implied_absences(
    observations: pd.DataFrame,
    *,
    trawl_catch: pd.DataFrame,
    nearshore_catch: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    stats = {"implied_absences_trawl": 0, "implied_absences_nearshore": 0}
    extra_rows: list[dict[str, Any]] = []
    existing: set[tuple[str, str, str]] = set()
    if not observations.empty:
        for _, row in observations.iterrows():
            existing.add(
                (
                    str(row["event_id"]),
                    str(row["species"]),
                    str(row["observation_source"]),
                )
            )

    trawl_enum, trawl_species = _enumerated_events_and_species(
        trawl_catch,
        event_id_col="haul_id",
        species_fn=_trawl_catch_row_species,
        enumerated_fn=_trawl_row_is_enumerated,
        species_catch_fn=_trawl_row_has_species_catch,
    )
    for event_id in trawl_enum:
        present = {s for s in trawl_species.get(event_id, set()) if _match_squid(s)}
        if present:
            continue
        key = (event_id, MARKET_SQUID_CANONICAL, OBSERVATION_SOURCE_TRAWL)
        if key in existing:
            continue
        extra_rows.append(
            {
                "event_id": event_id,
                "species": MARKET_SQUID_CANONICAL,
                "observation_source": OBSERVATION_SOURCE_TRAWL,
                "encounter": 0,
                "weight_kg": None,
                "count_observed": None,
                "adult_median_length_mm": None,
                "biology_excluded": False,
                "biology_excluded_reason": "",
                "absence_evidence": EVIDENCE_IMPLIED_ZERO,
                "encounter_semantics": ENCOUNTER_LABEL,
            }
        )
        stats["implied_absences_trawl"] += 1
        existing.add(key)

    near_enum, near_species = _enumerated_events_and_species(
        nearshore_catch,
        event_id_col="set_id",
        species_fn=_nearshore_catch_row_species,
        enumerated_fn=_nearshore_row_is_enumerated,
        species_catch_fn=_nearshore_row_has_species_catch,
    )
    for event_id in near_enum:
        present = {s for s in near_species.get(event_id, set()) if _match_squid(s)}
        if present:
            continue
        key = (event_id, MARKET_SQUID_CANONICAL, OBSERVATION_SOURCE_NEARSHORE)
        if key in existing:
            continue
        extra_rows.append(
            {
                "event_id": event_id,
                "species": MARKET_SQUID_CANONICAL,
                "observation_source": OBSERVATION_SOURCE_NEARSHORE,
                "encounter": 0,
                "weight_kg": None,
                "count_observed": None,
                "adult_median_length_mm": None,
                "biology_excluded": False,
                "biology_excluded_reason": "",
                "absence_evidence": EVIDENCE_IMPLIED_ZERO,
                "encounter_semantics": ENCOUNTER_LABEL,
            }
        )
        stats["implied_absences_nearshore"] += 1
        existing.add(key)

    if not extra_rows:
        return observations, stats
    extra = pd.DataFrame(extra_rows)
    if observations.empty:
        return extra, stats
    if "absence_evidence" not in observations.columns:
        observations = observations.copy()
        observations["absence_evidence"] = ""
    if "encounter_semantics" not in observations.columns:
        observations = observations.copy()
        observations["encounter_semantics"] = ENCOUNTER_LABEL
    return pd.concat([observations, extra], ignore_index=True), stats


def assemble_market_squid_encounter_observations(
    *,
    trawl_catch: pd.DataFrame,
    nearshore_catch: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    trawl_obs, trawl_stats = build_trawl_squid_encounters(trawl_catch)
    near_obs, near_stats = build_nearshore_squid_encounters(nearshore_catch)
    obs = pd.concat([trawl_obs, near_obs], ignore_index=True)
    obs, implied = append_squid_implied_absences(
        obs,
        trawl_catch=trawl_catch,
        nearshore_catch=nearshore_catch,
    )
    summary = {
        "encounter_semantics": ENCOUNTER_LABEL,
        "not_adult_model": True,
        "length_gate": "none",
        "trawl_catch": trawl_stats,
        "nearshore_catch": near_stats,
        "implied_absences": implied,
        "observation_rows_total": int(len(obs)),
        "encounter_presences": int((obs["encounter"] == 1).sum()) if not obs.empty else 0,
    }
    return obs, summary
