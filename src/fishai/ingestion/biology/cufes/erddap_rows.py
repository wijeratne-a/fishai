"""ERDDAP CSV row helpers (units/metadata row detection)."""

from __future__ import annotations

from typing import Any, Mapping


def is_erddap_units_row(_row: Mapping[str, Any], *, data_row_index: int) -> bool:
    """
    True for the ERDDAP units/attributes row: always the first data line after the CSV header.

    Detection is structural only (``data_row_index == 0`` per yearly cached file), never by cell
    values such as blank keys or unit strings.
    """
    return data_row_index == 0
