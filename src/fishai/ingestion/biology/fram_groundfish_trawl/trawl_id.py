"""Parse survey year from FRAM ``trawl_id`` (API catch rows lack per-row dates)."""

from __future__ import annotations


def survey_year_from_trawl_id(trawl_id: object) -> int | None:
    """Return the four-digit survey year encoded in ``trawl_id``, or ``None`` if invalid."""
    if trawl_id is None:
        return None
    text = str(trawl_id).strip()
    if len(text) < 4 or not text[:4].isdigit():
        return None
    year = int(text[:4])
    if year < 1977 or year > 2100:
        return None
    return year
