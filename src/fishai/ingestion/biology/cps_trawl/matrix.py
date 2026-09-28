"""Haul × species matrix expansion with zero-catch gate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping, Sequence

from fishai.ingestion.biology.cps_trawl.constants import (
    DEFAULT_ZERO_FRAME_STATUS,
    ZERO_FRAME_STATUS_UNVERIFIED,
    ZERO_FRAME_STATUS_VERIFIED,
    ZERO_FRAME_UNVERIFIED_REASON,
)


class ZeroFrameUnverifiedError(RuntimeError):
    """Raised when implied zero-catch cells are requested while the haul frame is unverified."""


@dataclass(frozen=True)
class MatrixCell:
    haul_id: str
    species: str
    count: int | None
    weight_kg: float | None
    presence_only: bool
    is_implied_zero: bool
    fill_reason: str | None


def expand_haul_species_matrix(
    catch_rows: Sequence[Mapping[str, Any]],
    haul_ids: Sequence[str],
    species_list: Sequence[str],
    *,
    zero_frame_status: str = DEFAULT_ZERO_FRAME_STATUS,
    on_unverified: Literal["raise", "na"] = "raise",
) -> list[dict[str, Any]]:
    """
    Expand catch rows to a haul-by-species matrix for ``species_list``.

    While ``zero_frame_status`` is ``UNVERIFIED``, absent species are never written as numeric
    zero; use ``on_unverified='raise'`` or ``'na'`` with ``fill_reason=zero_frame_unverified``.
    """
    if zero_frame_status not in (ZERO_FRAME_STATUS_UNVERIFIED, ZERO_FRAME_STATUS_VERIFIED):
        raise ValueError(f"unknown zero_frame_status: {zero_frame_status}")

    index: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in catch_rows:
        key = (str(row["haul_id"]), str(row["species"]))
        index[key] = row

    out: list[dict[str, Any]] = []
    for haul_id in haul_ids:
        for species in species_list:
            row = index.get((haul_id, species))
            if row is not None:
                out.append(
                    {
                        "haul_id": haul_id,
                        "species": species,
                        "count": row.get("count"),
                        "weight_kg": row.get("weight_kg"),
                        "presence_only": bool(row.get("presence_only")),
                        "is_implied_zero": False,
                        "fill_reason": None,
                    }
                )
                continue

            if zero_frame_status == ZERO_FRAME_STATUS_VERIFIED:
                out.append(
                    {
                        "haul_id": haul_id,
                        "species": species,
                        "count": 0,
                        "weight_kg": 0.0,
                        "presence_only": False,
                        "is_implied_zero": True,
                        "fill_reason": "verified_zero_frame",
                    }
                )
                continue

            if on_unverified == "raise":
                raise ZeroFrameUnverifiedError(
                    f"cannot imply zero for haul_id={haul_id} species={species}: "
                    f"{ZERO_FRAME_UNVERIFIED_REASON}"
                )
            out.append(
                {
                    "haul_id": haul_id,
                    "species": species,
                    "count": None,
                    "weight_kg": None,
                    "presence_only": False,
                    "is_implied_zero": False,
                    "fill_reason": ZERO_FRAME_UNVERIFIED_REASON,
                }
            )
    return out
