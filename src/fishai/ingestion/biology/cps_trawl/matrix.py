"""Haul × species matrix expansion with evidence-backed zero-catch gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from fishai.ingestion.biology.cps_trawl.constants import ZERO_FRAME_UNVERIFIED_REASON
from fishai.ingestion.biology.cps_trawl.zero_frame import (
    DEFAULT_EVIDENCE_PATH,
    haul_zero_frame_status,
    load_zero_frame_evidence,
)


class ZeroFrameUnverifiedError(RuntimeError):
    """Raised when implied zero-catch cells are requested while the haul frame is unverified."""


def expand_haul_species_matrix(
    catch_rows: Sequence[Mapping[str, Any]],
    haul_ids: Sequence[str],
    species_list: Sequence[str],
    *,
    haul_meta: Sequence[Mapping[str, Any]] | None = None,
    evidence_path: Path | None = None,
    on_unverified: Literal["raise", "na"] = "raise",
) -> list[dict[str, Any]]:
    """
    Expand catch rows to a haul-by-species matrix for ``species_list``.

    Implied zeros require per-cruise evidence (``config/cps_trawl_zero_frame_evidence.yaml``)
    and exclude ``animalia_only_haul`` tows.
    """
    evidence = load_zero_frame_evidence(evidence_path or DEFAULT_EVIDENCE_PATH)
    meta_by_id: dict[str, Mapping[str, Any]] = {}
    if haul_meta is not None:
        for row in haul_meta:
            meta_by_id[str(row["haul_id"])] = row

    index: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in catch_rows:
        key = (str(row["haul_id"]), str(row["species"]))
        index[key] = row

    out: list[dict[str, Any]] = []
    for haul_id in haul_ids:
        meta = meta_by_id.get(haul_id, {})
        animalia_only = bool(meta.get("animalia_only_haul"))
        may_zero, block_reason = haul_zero_frame_status(
            haul_id,
            animalia_only_haul=animalia_only,
            evidence=evidence,
        )

        for species in species_list:
            row = index.get((haul_id, species))
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

            if may_zero:
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

            reason = block_reason or ZERO_FRAME_UNVERIFIED_REASON
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
