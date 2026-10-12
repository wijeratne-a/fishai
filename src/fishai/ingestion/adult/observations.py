"""Adult observation rows from trawl and nearshore catch (presence-only excluded)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from fishai.ingestion.adult.constants import (
    ADULT_MIN_LENGTH_MM,
    ENCOUNTER_ALL_SIZES_SPECIES,
    EVIDENCE_IMPLIED_ZERO,
    EXCLUDE_REASON_JUVENILE,
    EXCLUDE_REASON_NO_SPECIMEN,
    EXCLUDE_REASON_PRESENCE_ONLY,
    OBSERVATION_SOURCE_NEARSHORE,
    OBSERVATION_SOURCE_TRAWL,
    PILOT_SPECIES,
)
from fishai.ingestion.adult.specimens import median_length_by_event_species
from fishai.ingestion.biology.cps_trawl.catch import is_presence_only


def _encounter_from_measurements(
    *,
    weight_kg: float | None,
    count: int | None,
) -> int:
    if weight_kg is not None and weight_kg > 0:
        return 1
    if count is not None and count > 0:
        return 1
    return 0


def _encounter_length_gate(
    event_id: str,
    species: str,
    medians: pd.Series,
) -> tuple[bool, str | None, float | None]:
    if species in ENCOUNTER_ALL_SIZES_SPECIES:
        key = (event_id, species)
        median_len = float(medians.loc[key]) if key in medians.index else None
        return True, None, median_len
    return _adult_length_gate(event_id, species, medians)


def _adult_length_gate(
    event_id: str,
    species: str,
    medians: pd.Series,
) -> tuple[bool, str | None, float | None]:
    key = (event_id, species)
    if key not in medians.index:
        return False, EXCLUDE_REASON_NO_SPECIMEN, None
    median_len = float(medians.loc[key])
    cutoff = ADULT_MIN_LENGTH_MM.get(species)
    if cutoff is None:
        return False, EXCLUDE_REASON_NO_SPECIMEN, median_len
    if median_len < cutoff:
        return False, EXCLUDE_REASON_JUVENILE, median_len
    return True, None, median_len


def build_trawl_observations(
    catch: pd.DataFrame,
    *,
    medians: pd.Series,
) -> tuple[pd.DataFrame, dict[str, int]]:
    stats = {
        "input_rows": 0,
        "presence_only_excluded": 0,
        "non_pilot_species_skipped": 0,
        "juvenile_excluded": 0,
        "no_specimen_excluded": 0,
        "rows_kept": 0,
    }
    rows: list[dict[str, Any]] = []
    if catch.empty:
        return pd.DataFrame(), stats
    for _, row in catch.iterrows():
        stats["input_rows"] += 1
        if bool(row.get("presence_only")):
            stats["presence_only_excluded"] += 1
            continue
        species = str(row.get("species") or "").strip()
        if species not in PILOT_SPECIES:
            stats["non_pilot_species_skipped"] += 1
            continue
        event_id = str(row["haul_id"])
        ok, reason, median_len = _encounter_length_gate(event_id, species, medians)
        if not ok:
            if reason == EXCLUDE_REASON_JUVENILE:
                stats["juvenile_excluded"] += 1
            else:
                stats["no_specimen_excluded"] += 1
            continue
        weight = row.get("weight_kg")
        weight_f = float(weight) if weight is not None and pd.notna(weight) else None
        count_raw = row.get("count_raised_est")
        if count_raw is None or pd.isna(count_raw):
            count_raw = row.get("subsample_count")
        count = int(count_raw) if count_raw is not None and pd.notna(count_raw) else None
        rows.append(
            {
                "event_id": event_id,
                "species": species,
                "observation_source": OBSERVATION_SOURCE_TRAWL,
                "encounter": _encounter_from_measurements(weight_kg=weight_f, count=count),
                "weight_kg": weight_f,
                "count_observed": count,
                "adult_median_length_mm": median_len,
                "biology_excluded": False,
                "biology_excluded_reason": "",
            }
        )
        stats["rows_kept"] += 1
    return pd.DataFrame(rows), stats


def build_nearshore_observations(
    catch: pd.DataFrame,
    *,
    medians: pd.Series,
) -> tuple[pd.DataFrame, dict[str, int]]:
    stats = {
        "input_rows": 0,
        "presence_only_excluded": 0,
        "non_pilot_species_skipped": 0,
        "juvenile_excluded": 0,
        "no_specimen_excluded": 0,
        "rows_kept": 0,
    }
    rows: list[dict[str, Any]] = []
    if catch.empty:
        return pd.DataFrame(), stats
    for _, row in catch.iterrows():
        stats["input_rows"] += 1
        species = str(row.get("scientific_name") or row.get("species") or "").strip()
        if species not in PILOT_SPECIES:
            stats["non_pilot_species_skipped"] += 1
            continue
        event_id = str(row["set_id"])
        ok, reason, median_len = _encounter_length_gate(event_id, species, medians)
        if not ok:
            if reason == EXCLUDE_REASON_JUVENILE:
                stats["juvenile_excluded"] += 1
            else:
                stats["no_specimen_excluded"] += 1
            continue
        weight = row.get("total_weight_kg")
        weight_f = float(weight) if weight is not None and pd.notna(weight) else None
        count_raw = row.get("total_number")
        count = int(count_raw) if count_raw is not None and pd.notna(count_raw) else None
        rows.append(
            {
                "event_id": event_id,
                "species": species,
                "observation_source": OBSERVATION_SOURCE_NEARSHORE,
                "encounter": _encounter_from_measurements(weight_kg=weight_f, count=count),
                "weight_kg": weight_f,
                "count_observed": count,
                "adult_median_length_mm": median_len,
                "biology_excluded": False,
                "biology_excluded_reason": "",
            }
        )
        stats["rows_kept"] += 1
    return pd.DataFrame(rows), stats


def observations_for_training_events(
    observations: pd.DataFrame,
    event_ids: set[str],
) -> pd.DataFrame:
    if observations.empty:
        return observations
    return observations[observations["event_id"].astype(str).isin(event_ids)].reset_index(drop=True)


def _trawl_catch_row_species(row: pd.Series) -> str:
    return str(row.get("species") or "").strip()


def _nearshore_catch_row_species(row: pd.Series) -> str:
    return str(row.get("scientific_name") or row.get("species") or "").strip()


def _trawl_row_is_enumerated(row: pd.Series) -> bool:
    if is_presence_only(row.get("presence_only")):
        return False
    count_raw = row.get("subsample_count")
    return count_raw is not None and pd.notna(count_raw)


def _nearshore_row_is_enumerated(row: pd.Series) -> bool:
    count_raw = row.get("total_number")
    return count_raw is not None and pd.notna(count_raw)


def _trawl_row_has_species_catch(row: pd.Series) -> bool:
    return not is_presence_only(row.get("presence_only"))


def _nearshore_row_has_species_catch(_row: pd.Series) -> bool:
    return True


def _enumerated_events_and_species(
    catch: pd.DataFrame,
    *,
    event_id_col: str,
    species_fn,
    enumerated_fn,
    species_catch_fn,
) -> tuple[set[str], dict[str, set[str]]]:
    enumerated_events: set[str] = set()
    species_by_event: dict[str, set[str]] = {}
    if catch.empty:
        return enumerated_events, species_by_event
    for _, row in catch.iterrows():
        event_id = str(row[event_id_col])
        if enumerated_fn(row):
            enumerated_events.add(event_id)
        species = species_fn(row)
        if not species:
            continue
        if species_catch_fn(row):
            species_by_event.setdefault(event_id, set()).add(species)
    return enumerated_events, species_by_event


def append_implied_absence_observations(
    observations: pd.DataFrame,
    *,
    trawl_catch: pd.DataFrame,
    nearshore_catch: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    For fully-enumerated hauls/sets, emit encounter=0 rows for pilot species with no catch row.

    Enumeration evidence: at least one catch row with presence_only != Y (trawl) and a
    non-null subsample_count (trawl) or total_number (nearshore).
    """
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
        present = trawl_species.get(event_id, set())
        for species in PILOT_SPECIES:
            if species in present:
                continue
            key = (event_id, species, OBSERVATION_SOURCE_TRAWL)
            if key in existing:
                continue
            extra_rows.append(
                {
                    "event_id": event_id,
                    "species": species,
                    "observation_source": OBSERVATION_SOURCE_TRAWL,
                    "encounter": 0,
                    "weight_kg": None,
                    "count_observed": None,
                    "adult_median_length_mm": None,
                    "biology_excluded": False,
                    "biology_excluded_reason": "",
                    "absence_evidence": EVIDENCE_IMPLIED_ZERO,
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
        present = near_species.get(event_id, set())
        for species in PILOT_SPECIES:
            if species in present:
                continue
            key = (event_id, species, OBSERVATION_SOURCE_NEARSHORE)
            if key in existing:
                continue
            extra_rows.append(
                {
                    "event_id": event_id,
                    "species": species,
                    "observation_source": OBSERVATION_SOURCE_NEARSHORE,
                    "encounter": 0,
                    "weight_kg": None,
                    "count_observed": None,
                    "adult_median_length_mm": None,
                    "biology_excluded": False,
                    "biology_excluded_reason": "",
                    "absence_evidence": EVIDENCE_IMPLIED_ZERO,
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
    combined = pd.concat([observations, extra], ignore_index=True)
    return combined, stats
