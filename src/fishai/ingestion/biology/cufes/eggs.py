"""Egg-count cell semantics for ERDDAP CUFES wide columns."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

from fishai.ingestion.biology.cufes.constants import EGG_CATEGORIES

# ERDDAP tabledap marks a taxon as not sampled only with a missing-value NaN (float NaN or
# the literal text ``NaN``, any case, after ASCII strip). Empty or whitespace-only cells are
# invalid and fail the whole event under QC_COUNT_INVALID.


def egg_cell_not_sampled(raw: Any) -> bool:
    """True only when ERDDAP marks the taxon as not sampled (NaN missing value)."""
    if isinstance(raw, float) and math.isnan(raw):
        return True
    if raw is None:
        return False
    text = str(raw).strip()
    if text.lower() == "nan":
        return True
    return False


def egg_cell_invalid(raw: Any) -> bool:
    """True when the cell is present but not a valid non-negative integer count."""
    if egg_cell_not_sampled(raw):
        return False
    if raw is None:
        return True
    text = str(raw).strip()
    if text == "":
        return True
    try:
        value = float(text)
    except ValueError:
        return True
    if math.isnan(value) or value < 0 or value != int(value):
        return True
    return False


def parse_sampled_egg_count(raw: Any) -> int:
    """Parse a sampled cell; caller must ensure ``not egg_cell_not_sampled(raw)``."""
    value = float(str(raw).strip())
    return int(value)


@dataclass
class EggRowState:
    invalid: bool
    all_not_sampled: bool
    sampled: dict[str, int]


def classify_egg_row(row: Mapping[str, Any]) -> EggRowState:
    sampled: dict[str, int] = {}
    any_invalid = False
    any_sampled = False
    for col, taxon in EGG_CATEGORIES:
        raw = row.get(col)
        if egg_cell_invalid(raw):
            any_invalid = True
            break
        if egg_cell_not_sampled(raw):
            continue
        any_sampled = True
        sampled[taxon] = parse_sampled_egg_count(raw)
    return EggRowState(
        invalid=any_invalid,
        all_not_sampled=not any_sampled and not any_invalid,
        sampled=sampled,
    )
