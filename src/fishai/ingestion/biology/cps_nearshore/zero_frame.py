"""Per-cruise set-frame evidence (committed YAML; human audit).

Implied zero catch for a target species may only be emitted for a set when
the set belongs to a VERIFIED cruise frame: a human-audited entry in
``config/cps_nearshore_zero_frame_evidence.yaml`` whose ``expected_sets``
equals ``report_set_log`` minus ``aborted_sets``. Anything else fails closed
(implied zeros recorded as not-available, never as silent zeros).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from fishai.ingestion.biology.cps_nearshore.constants import (
    ZERO_FRAME_UNVERIFIED_REASON,
)
from fishai.ingestion.sources import REPO_ROOT

DEFAULT_EVIDENCE_PATH = REPO_ROOT / "config" / "cps_nearshore_zero_frame_evidence.yaml"

SET_NOT_IN_VERIFIED_FRAME_REASON = "set_not_in_verified_frame"
CRUISE_FRAME_UNVERIFIED_REASON = "cruise_frame_unverified"
EVIDENCE_ENTRY_INVALID_REASON = "cruise_evidence_invalid"


@dataclass(frozen=True)
class CruiseSetFrameEvidence:
    cruise: str
    ship: str
    source_report_citation: str
    report_set_log: frozenset[int]
    aborted_sets: frozenset[int]
    expected_sets: frozenset[int]
    valid: bool
    invalid_reason: str | None


def _parse_set_list(raw: Any) -> list[int]:
    if raw is None:
        return []
    out: list[int] = []
    for item in raw:
        if isinstance(item, bool):
            raise ValueError("set list entries must be integers")
        out.append(int(item))
    return out


def _validate_entry(entry: Mapping[str, Any]) -> CruiseSetFrameEvidence:
    cruise = str(entry.get("cruise", "")).strip()
    ship = str(entry.get("ship", "")).strip()
    citation = str(entry.get("source_report_citation", "")).strip()
    report_log = frozenset(_parse_set_list(entry.get("report_set_log")))
    aborted = frozenset(_parse_set_list(entry.get("aborted_sets")))
    listed_expected = entry.get("expected_sets")
    computed_expected = frozenset(report_log - aborted)

    invalid_reason: str | None = None
    if not cruise or not ship:
        invalid_reason = "missing_cruise_or_ship"
    elif not citation:
        invalid_reason = "missing_source_report_citation"
    elif not report_log:
        invalid_reason = "empty_report_set_log"
    elif listed_expected is None:
        invalid_reason = "missing_expected_sets"
    else:
        expected_from_file = frozenset(_parse_set_list(listed_expected))
        if expected_from_file != computed_expected:
            invalid_reason = "expected_sets_mismatch_report_minus_aborted"

    expected_sets = computed_expected if invalid_reason is None else frozenset()
    return CruiseSetFrameEvidence(
        cruise=cruise,
        ship=ship,
        source_report_citation=citation,
        report_set_log=report_log,
        aborted_sets=aborted,
        expected_sets=expected_sets,
        valid=invalid_reason is None,
        invalid_reason=invalid_reason,
    )


def load_zero_frame_evidence(path: Path | None = None) -> dict[tuple[str, str], CruiseSetFrameEvidence]:
    """Load evidence file; invalid entries are kept but marked ``valid=False``."""
    evidence_path = path or DEFAULT_EVIDENCE_PATH
    data = yaml.safe_load(evidence_path.read_text(encoding="utf-8")) or {}
    frames = data.get("cruise_frames") or []
    index: dict[tuple[str, str], CruiseSetFrameEvidence] = {}
    for entry in frames:
        if not isinstance(entry, dict):
            continue
        parsed = _validate_entry(entry)
        key = (parsed.cruise, parsed.ship)
        index[key] = parsed
    return index


def parse_set_id(set_id: str) -> tuple[str, str, int]:
    """Return (cruise, ship, set_number) from ``CPSNearshore:{cruise}:{ship}:{set}``."""
    prefix = "CPSNearshore:"
    if not set_id.startswith(prefix):
        raise ValueError(f"unexpected set_id format: {set_id}")
    parts = set_id[len(prefix):].split(":")
    if len(parts) != 3:
        raise ValueError(f"unexpected set_id format: {set_id}")
    cruise, ship, set_s = parts
    return cruise, ship, int(set_s)


def set_zero_frame_status(
    set_id: str,
    evidence: Mapping[tuple[str, str], CruiseSetFrameEvidence],
) -> tuple[bool, str | None]:
    """Return (may_emit_implied_zeros, fill_reason_when_blocked).

    ``may_emit_implied_zeros`` is True only for sets in a verified cruise frame.
    """
    try:
        cruise, ship, set_no = parse_set_id(set_id)
    except ValueError:
        return False, EVIDENCE_ENTRY_INVALID_REASON
    frame = evidence.get((cruise, ship))
    if frame is None or not frame.valid:
        return False, CRUISE_FRAME_UNVERIFIED_REASON
    if set_no not in frame.expected_sets:
        return False, SET_NOT_IN_VERIFIED_FRAME_REASON
    return True, None
