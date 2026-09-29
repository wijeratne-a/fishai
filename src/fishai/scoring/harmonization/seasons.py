"""Season labels for harmonization holdout strata."""

from __future__ import annotations

import datetime as dt


def season_label(day: dt.date, *, test_start: dt.date, test_end: dt.date) -> str:
    """
    Return DJF/MAM/JJA/SON for calendar seasons.

    Test-split JJA is only 1–23 June (partial); labelled distinctly per prereg.
    """
    if test_start <= day <= test_end and day.month == 6 and day.day <= 23:
        return "June only (1–23)"
    month = day.month
    if month in (12, 1, 2):
        return "DJF"
    if month in (3, 4, 5):
        return "MAM"
    if month in (6, 7, 8):
        return "JJA"
    return "SON"
