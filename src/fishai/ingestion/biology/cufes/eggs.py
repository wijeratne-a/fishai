"""Egg-count cell semantics for ERDDAP CUFES wide columns."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

from fishai.ingestion.biology.cufes.constants import EGG_CATEGORIES

# ERDDAP tabledap missing values in CSV appear as an empty field or the literal ``NaN``.
# A whitespace-only cell strips to empty and is treated the same as ERDDAP missing.
# Any other non-empty text (e.g. ``abc``, ``-1``, ``2.5``) is a hard QC failure for the event.


def egg_cell_not_sampled(raw: Any) -> bool:
    """True when ERDDAP marks the taxon as not sampled for this event."""
    if raw is None:
        return True
    text = str(raw).strip()
    if text == "":
        return True
    if text.lower() == "nan":
        return True
    return False


def egg_cell_invalid(raw: Any) -> bool:
    """True when the cell is present but not a valid non-negative integer count."""
    if egg_cell_not_sampled(raw):
        return False
    text = str(raw).strip()
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
