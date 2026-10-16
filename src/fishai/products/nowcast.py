"""Plan an operational egg-encounter nowcast from a local GLORYS day index.

The fitted surfaces themselves are produced by
``scripts/products/refresh_nowcast.R`` inside the CI R image.
"""

from __future__ import annotations

import json
from pathlib import Path


def latest_glorys_valid_day(index_path: Path) -> str:
    """Newest ISO day in a local GLORYS index. Empty or malformed input fails closed."""
    days = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(days, list) or not days:
        raise ValueError("GLORYS day index is empty")
    cleaned = []
    for day in days:
        text = str(day)
        if len(text) != 10 or text[4] != "-" or text[7] != "-":
            raise ValueError(f"GLORYS day is not ISO: {day}")
        cleaned.append(text)
    return max(cleaned)


def nowcast_plan(valid_day: str) -> dict[str, object]:
    return {
        "mode": "nowcast",
        "valid_day": valid_day,
        "lead_days": 0,
        "forecast_age_hours": 0,
        "evidence_state": "NOWCAST_UNVALIDATED",
        "source_run_time": f"{valid_day}T00:00:00Z",
        "life_stage": "egg",
    }
