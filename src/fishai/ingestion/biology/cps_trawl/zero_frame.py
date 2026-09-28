"""Per-cruise zero-catch frame evidence (committed YAML; human audit)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from fishai.ingestion.biology.cps_trawl.constants import (
    ANIMALIA_ONLY_ZERO_FRAME_REASON,
    ZERO_FRAME_UNVERIFIED_REASON,
)
from fishai.ingestion.sources import REPO_ROOT

DEFAULT_EVIDENCE_PATH = REPO_ROOT / "config" / "cps_trawl_zero_frame_evidence.yaml"

HAUL_NOT_IN_VERIFIED_FRAME_REASON = "haul_not_in_verified_frame"
CRUISE_FRAME_UNVERIFIED_REASON = "cruise_frame_unverified"
EVIDENCE_ENTRY_INVALID_REASON = "cruise_evidence_invalid"


@dataclass(frozen=True)
class CruiseFrameEvidence:
    cruise: str
    ship: str
    source_report_citation: str
    report_haul_log: frozenset[int]
    aborted_tows: frozenset[int]
    expected_hauls: frozenset[int]
    valid: bool
    invalid_reason: str | None


def _parse_haul_list(raw: Any) -> list[int]:
    if raw is None:
        return []
    out: list[int] = []
    for item in raw:
        if isinstance(item, bool):
            raise ValueError("haul list entries must be integers")
        out.append(int(item))
    return out


def _validate_entry(entry: Mapping[str, Any]) -> CruiseFrameEvidence:
    cruise = str(entry.get("cruise", "")).strip()
    ship = str(entry.get("ship", "")).strip()
    citation = str(entry.get("source_report_citation", "")).strip()
    report_log = frozenset(_parse_haul_list(entry.get("report_haul_log")))
    aborted = frozenset(_parse_haul_list(entry.get("aborted_tows")))
    listed_expected = entry.get("expected_hauls")
    computed_expected = frozenset(report_log - aborted)

    invalid_reason: str | None = None
    if not cruise or not ship:
        invalid_reason = "missing_cruise_or_ship"
    elif not citation:
        invalid_reason = "missing_source_report_citation"
    elif not report_log:
        invalid_reason = "empty_report_haul_log"
    elif listed_expected is None:
        invalid_reason = "missing_expected_hauls"
    else:
        expected_from_file = frozenset(_parse_haul_list(listed_expected))
        if expected_from_file != computed_expected:
            invalid_reason = "expected_hauls_mismatch_report_minus_aborted"

    expected_hauls = computed_expected if invalid_reason is None else frozenset()
    return CruiseFrameEvidence(
        cruise=cruise,
        ship=ship,
        source_report_citation=citation,
        report_haul_log=report_log,
        aborted_tows=aborted,
        expected_hauls=expected_hauls,
        valid=invalid_reason is None,
        invalid_reason=invalid_reason,
    )


def load_zero_frame_evidence(path: Path | None = None) -> dict[tuple[str, str], CruiseFrameEvidence]:
    """Load evidence file; invalid entries are kept but marked ``valid=False``."""
    evidence_path = path or DEFAULT_EVIDENCE_PATH
    data = yaml.safe_load(evidence_path.read_text(encoding="utf-8")) or {}
    frames = data.get("cruise_frames") or []
    index: dict[tuple[str, str], CruiseFrameEvidence] = {}
    for entry in frames:
        if not isinstance(entry, dict):
            continue
        parsed = _validate_entry(entry)
        key = (parsed.cruise, parsed.ship)
        index[key] = parsed
    return index


def parse_haul_id(haul_id: str) -> tuple[str, str, int]:
    """Return (cruise, ship, haul_number) from ``CPSTrawl:{cruise}:{ship}:{haul}``."""
    prefix = "CPSTrawl:"
    if not haul_id.startswith(prefix):
        raise ValueError(f"unexpected haul_id format: {haul_id}")
    parts = haul_id[len(prefix) :].split(":")
    if len(parts) != 3:
        raise ValueError(f"unexpected haul_id format: {haul_id}")
    cruise, ship, haul_s = parts
    return cruise, ship, int(haul_s)


def haul_zero_frame_status(
    haul_id: str,
    *,
    animalia_only_haul: bool,
    evidence: Mapping[tuple[str, str], CruiseFrameEvidence],
) -> tuple[bool, str | None]:
    """
    Return (may_emit_implied_zeros, fill_reason_when_blocked).

    ``may_emit_implied_zeros`` is True only for hauls in a verified cruise frame.
    """
    if animalia_only_haul:
        return False, ANIMALIA_ONLY_ZERO_FRAME_REASON

    cruise, ship, haul_num = parse_haul_id(haul_id)
    entry = evidence.get((cruise, ship))
    if entry is None:
        return False, ZERO_FRAME_UNVERIFIED_REASON
    if not entry.valid:
        return False, EVIDENCE_ENTRY_INVALID_REASON
    if haul_num not in entry.expected_hauls:
        return False, HAUL_NOT_IN_VERIFIED_FRAME_REASON
    return True, None
