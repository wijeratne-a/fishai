"""ERDDAP CSV row helpers (units/metadata row detection)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

UNITS_ROW_TIME_MARKER = "UTC"


def is_first_data_row(data_row_index: int) -> bool:
    """True for the first data line after the CSV header in each ERDDAP file."""
    return data_row_index == 0


def assert_erddap_units_row(row: Mapping[str, Any], *, path: Path | str) -> None:
    """
    Fail closed: the first data row in each source file must be the ERDDAP units row.

    Validated by ``time`` equal to ``UTC`` (after strip). Otherwise raise ``ValueError``
    naming the file; never treat a non-units row as skippable metadata.
    """
    time_cell = str(row.get("time", "")).strip()
    if time_cell != UNITS_ROW_TIME_MARKER:
        raise ValueError(
            f"expected ERDDAP units row (time={UNITS_ROW_TIME_MARKER!r}) as first data line "
            f"in {path}, got time={time_cell!r}"
        )


def is_erddap_units_row(row: Mapping[str, Any], *, data_row_index: int, path: Path | str) -> bool:
    """
    True when this row is the skippable units line for its file (first data row only).

    Call ``assert_erddap_units_row`` before skipping when ``data_row_index == 0``.
    """
    if not is_first_data_row(data_row_index):
        return False
    assert_erddap_units_row(row, path=path)
    return True
