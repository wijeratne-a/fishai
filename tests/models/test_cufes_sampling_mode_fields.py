"""PR #4 cufes_events: fields available for planned vs adaptive discrimination."""

from __future__ import annotations

import inspect

from fishai.ingestion.biology.cufes.constants import ERDDAP_FIELDS
from fishai.ingestion.biology.cufes import transform


def test_erddap_fetch_has_no_line_or_station_column() -> None:
    lowered = {f.lower() for f in ERDDAP_FIELDS}
    assert "line" not in lowered
    assert "station" not in lowered
    assert "cruise" in lowered
    assert "sample_number" in lowered


def test_row_to_event_payload_has_no_sampling_mode_flag() -> None:
    src = inspect.getsource(transform.row_to_event)
    assert "planned_transect" not in src
    assert "adaptive_infill" not in src
    assert '"event_id"' in src


def test_erddap_includes_cruise_ship_sample_for_external_matching_only() -> None:
    assert "ship_code" in ERDDAP_FIELDS
    assert "cruise" in ERDDAP_FIELDS
