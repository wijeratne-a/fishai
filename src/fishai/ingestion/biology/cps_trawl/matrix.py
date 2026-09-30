"""Haul × species matrix expansion with evidence-backed zero-catch gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from fishai.ingestion.biology.cps_trawl.constants import (
    HAUL_META_MISSING_REASON,
    UNPARSEABLE_CATCH_ROW_REASON,
    UNRESOLVED_HIGHER_TAXON_REASON,
    ZERO_FRAME_UNVERIFIED_REASON,
)
from fishai.ingestion.biology.cps_trawl.taxonomy import (
    catch_row_establishes_target_presence,
    unresolved_taxon_blocks_target,
)
from fishai.ingestion.biology.cps_trawl.zero_frame import (
    DEFAULT_EVIDENCE_PATH,
    haul_zero_frame_status,
    load_zero_frame_evidence,
)

class ZeroFrameUnverifiedError(RuntimeError):
    """Raised when implied zero-catch cells are requested while the haul frame is unverified."""


def _haul_level_block_reason(meta: Mapping[str, Any] | None) -> str | None:
    if meta is None:
        return HAUL_META_MISSING_REASON
    if int(meta.get("unparseable_catch_rows") or 0) > 0:
        return UNPARSEABLE_CATCH_ROW_REASON
    return None


def expand_haul_species_matrix(
    catch_rows: Sequence[Mapping[str, Any]],
    haul_ids: Sequence[str],
    species_list: Sequence[str],
    *,
    species_itis_tsn: Mapping[str, int],
    haul_meta: Sequence[Mapping[str, Any]] | None = None,
    evidence_path: Path | None = None,
    on_unverified: Literal["raise", "na"] = "raise",
) -> list[dict[str, Any]]:
    """
    Expand catch rows to a haul-by-species matrix for ``species_list``.

    Implied zeros require per-cruise evidence (``config/cps_trawl_zero_frame_evidence.yaml``),
    explicit ``haul_meta`` per haul, and ITIS TSN matching (not scientific-name text alone).
    """
    evidence = load_zero_frame_evidence(evidence_path or DEFAULT_EVIDENCE_PATH)
    meta_by_id: dict[str, Mapping[str, Any]] | None
    if haul_meta is None:
        meta_by_id = None
    else:
        meta_by_id = {str(row["haul_id"]): row for row in haul_meta}

    catch_by_haul: dict[str, list[Mapping[str, Any]]] = {}
    for row in catch_rows:
        haul_id = str(row["haul_id"])
        catch_by_haul.setdefault(haul_id, []).append(row)

    out: list[dict[str, Any]] = []
    for haul_id in haul_ids:
        haul_meta_row: Mapping[str, Any] | None
        if meta_by_id is None:
            haul_meta_row = None
        else:
            haul_meta_row = meta_by_id.get(haul_id)
            if haul_meta_row is None:
                haul_meta_row = None

        haul_block = _haul_level_block_reason(haul_meta_row)
        if haul_meta_row is None and meta_by_id is not None:
            haul_block = HAUL_META_MISSING_REASON

        animalia_only = False
        if haul_meta_row is not None:
            animalia_only = bool(haul_meta_row.get("animalia_only_haul"))

        may_zero, frame_block_reason = haul_zero_frame_status(
            haul_id,
            animalia_only_haul=animalia_only,
            evidence=evidence,
        )

        haul_catch = catch_by_haul.get(haul_id, [])

        for species in species_list:
            target_tsn = species_itis_tsn.get(species)
            if target_tsn is None:
                raise ValueError(f"species_itis_tsn missing entry for target species: {species}")

            row: Mapping[str, Any] | None = None
            for catch_row in haul_catch:
                catch_species = str(catch_row.get("species", ""))
                catch_tsn = _parse_catch_tsn(catch_row)
                if catch_row_establishes_target_presence(
                    catch_species, catch_tsn, species, target_tsn
                ):
                    row = catch_row
                    break

            if row is not None:
                out.append(
                    {
                        "haul_id": haul_id,
                        "species": species,
                        "subsample_count": row.get("subsample_count"),
                        "count_raised_est": row.get("count_raised_est"),
                        "weight_kg": row.get("weight_kg"),
                        "presence_only": bool(row.get("presence_only")),
                        "is_implied_zero": False,
                        "fill_reason": None,
                    }
                )
                continue

            per_target_block: str | None = None
            if haul_block is None and may_zero:
                for catch_row in haul_catch:
                    catch_species = str(catch_row.get("species", ""))
                    catch_tsn = _parse_catch_tsn(catch_row)
                    if unresolved_taxon_blocks_target(
                        catch_species, catch_tsn, species, target_tsn
                    ):
                        per_target_block = UNRESOLVED_HIGHER_TAXON_REASON
                        break

            if haul_block is not None:
                reason = haul_block
            elif not may_zero:
                reason = frame_block_reason or ZERO_FRAME_UNVERIFIED_REASON
            elif per_target_block is not None:
                reason = per_target_block
            elif may_zero:
                out.append(
                    {
                        "haul_id": haul_id,
                        "species": species,
                        "subsample_count": 0,
                        "count_raised_est": 0,
                        "weight_kg": 0.0,
                        "presence_only": False,
                        "is_implied_zero": True,
                        "fill_reason": "verified_zero_frame",
                    }
                )
                continue
            else:
                reason = frame_block_reason or ZERO_FRAME_UNVERIFIED_REASON

            if on_unverified == "raise":
                raise ZeroFrameUnverifiedError(
                    f"cannot imply zero for haul_id={haul_id} species={species}: {reason}"
                )
            out.append(
                {
                    "haul_id": haul_id,
                    "species": species,
                    "subsample_count": None,
                    "count_raised_est": None,
                    "weight_kg": None,
                    "presence_only": False,
                    "is_implied_zero": False,
                    "fill_reason": reason,
                }
            )
    return out


def _parse_catch_tsn(row: Mapping[str, Any]) -> int | None:
    raw = row.get("itis_tsn")
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None
