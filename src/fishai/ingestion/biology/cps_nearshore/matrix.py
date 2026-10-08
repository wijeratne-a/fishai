"""Set × pilot-species encounter matrix with the zero-frame gate.

For each set and each pilot species (Pacific sardine, northern anchovy) emit
one row: presence when a catch row establishes the target, an implied zero
only when the set is in a verified cruise frame, otherwise an explicit
not-available marker. Never presence-only: every row carries the effort
context (the purse-seine set) and the evidence state.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from fishai.ingestion.biology.cps_nearshore.constants import (
    PILOT_MATRIX_SPECIES,
    PILOT_SPECIES_ITIS_TSN,
    SET_META_MISSING_REASON,
    UNRESOLVED_HIGHER_TAXON_REASON,
    ZERO_FRAME_UNVERIFIED_REASON,
)
from fishai.ingestion.biology.cps_nearshore.zero_frame import (
    CRUISE_FRAME_UNVERIFIED_REASON,
    SET_NOT_IN_VERIFIED_FRAME_REASON,
    load_zero_frame_evidence,
    set_zero_frame_status,
)
from fishai.ingestion.biology.cps_trawl.taxonomy import (
    catch_row_establishes_target_presence,
    is_unresolved_higher_taxon,
    unresolved_taxon_blocks_target,
)

try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    Path = None  # type: ignore[assignment]


class ZeroFrameUnverifiedError(RuntimeError):
    """Raised when implied zeros are requested without verified frame evidence."""


def _set_level_block_reason(meta: Mapping[str, Any] | None) -> str | None:
    if meta is None:
        return SET_META_MISSING_REASON
    return None


def expand_set_species_matrix(
    catch: Sequence[Mapping[str, Any]],
    set_ids: Sequence[str],
    species: Sequence[str],
    *,
    species_itis_tsn: Mapping[str, int] | None = None,
    set_meta: Sequence[Mapping[str, Any]] | None = None,
    evidence_path=None,
    on_unverified: str = "na",
) -> list[dict[str, Any]]:
    """Expand long catch into a set × species encounter matrix.

    ``on_unverified`` controls implied-zero behavior for sets outside a
    verified frame: ``"na"`` (default) emits an explicit not-available marker;
    ``"error"`` raises :class:`ZeroFrameUnverifiedError`.
    """
    tsn_lookup = dict(species_itis_tsn or PILOT_SPECIES_ITIS_TSN)
    evidence = load_zero_frame_evidence(evidence_path)
    meta_by_id = {str(m.get("set_id")): m for m in (set_meta or [])}

    by_set: dict[str, list[Mapping[str, Any]]] = {}
    for row in catch:
        by_set.setdefault(str(row.get("set_id")), []).append(row)

    out: list[dict[str, Any]] = []
    for set_id in set_ids:
        set_id = str(set_id)
        meta = meta_by_id.get(set_id)
        rows = by_set.get(set_id, [])
        may_zero, zero_reason = set_zero_frame_status(set_id, evidence)
        for target in species:
            target_tsn = tsn_lookup.get(target)
            presence = any(
                catch_row_establishes_target_presence(
                    r.get("scientific_name", ""),
                    r.get("itis_tsn"),
                    target,
                    target_tsn,
                )
                for r in rows
            )
            blocked_by_taxon = any(
                unresolved_taxon_blocks_target(
                    r.get("scientific_name", ""), r.get("itis_tsn"), target, target_tsn
                )
                or is_unresolved_higher_taxon(r.get("scientific_name", ""), r.get("itis_tsn"))
                for r in rows
            )
            record: dict[str, Any] = {
                "set_id": set_id,
                "scientific_name": target,
                "itis_tsn": target_tsn,
                "encounter": None,
                "evidence": "not_available",
                "reason": None,
            }
            level_block = _set_level_block_reason(meta)
            if level_block is not None:
                record["reason"] = level_block
            elif presence:
                record["encounter"] = 1
                record["evidence"] = "direct_observation"
            elif blocked_by_taxon:
                record["reason"] = UNRESOLVED_HIGHER_TAXON_REASON
            elif may_zero:
                record["encounter"] = 0
                record["evidence"] = "implied_zero_verified_frame"
            elif on_unverified == "error":
                raise ZeroFrameUnverifiedError(
                    f"implied zero requested for unverified set {set_id}"
                )
            else:
                record["reason"] = zero_reason or ZERO_FRAME_UNVERIFIED_REASON
            out.append(record)
    return out
