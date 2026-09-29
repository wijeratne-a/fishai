"""CUFES covariate ``source_product`` checks against ``glorys_product_for_date``."""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable, Mapping, Sequence

from fishai.ingestion.physics.sources.glorys import glorys_product_for_date


def expected_glorys_source_product(event_day: dt.date) -> str:
    """Copernicus dataset id for ``event_day`` (delegates to PR #7 helper)."""
    return glorys_product_for_date(event_day)


def parse_event_utc_date(time_value: object) -> dt.date:
    if isinstance(time_value, dt.datetime):
        return time_value.date()
    text = str(time_value).strip()
    if not text:
        raise ValueError("empty event time")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(text)
    return parsed.date()


def find_source_product_mismatches(
    event_id: Sequence[str],
    event_time: Sequence[object],
    source_product: Sequence[str],
    *,
    config: Mapping[str, object] | None = None,
) -> list[str]:
    """Return human-readable mismatch lines (empty if all rows match)."""
    errors: list[str] = []
    for eid, tval, got in zip(event_id, event_time, source_product, strict=True):
        day = parse_event_utc_date(tval)
        expected = glorys_product_for_date(day, config=config)
        got_s = str(got).strip()
        if got_s != expected:
            errors.append(
                f"event_id={eid} date={day.isoformat()} source_product={got_s!r} "
                f"expected={expected!r} (glorys_product_for_date)"
            )
    return errors


def assert_source_products_match_glorys(
    event_id: Sequence[str],
    event_time: Sequence[object],
    source_product: Sequence[str],
    *,
    config: Mapping[str, object] | None = None,
) -> None:
    errors = find_source_product_mismatches(
        event_id, event_time, source_product, config=config
    )
    if errors:
        raise ValueError("; ".join(errors[:5]) + (f"; +{len(errors) - 5} more" if len(errors) > 5 else ""))
