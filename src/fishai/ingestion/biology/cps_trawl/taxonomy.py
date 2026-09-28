"""ITIS TSN normalization and unresolved-taxa checks for zero-catch matching."""

from __future__ import annotations

import re
from typing import Final

# Subspecies (or infraspecific) ITIS TSN → accepted species TSN. No network lookups at runtime.
SUBSPECIES_TSN_TO_SPECIES_TSN: Final[dict[int, int]] = {
    623656: 161997,  # Sardinops sagax caerulea → Sardinops sagax
}

# Family names (ITIS-style) → genera that may appear as CPS trawl targets.
FAMILY_TO_GENERA: Final[dict[str, frozenset[str]]] = {
    "Clupeidae": frozenset({"Sardinops", "Engraulis", "Clupea", "Sardinella", "Opisthonema"}),
    "Engraulidae": frozenset({"Engraulis", "Anchoa"}),
}

_UNIDENTIFIED_FISH_RE = re.compile(r"unidentified\s+fish", re.IGNORECASE)
_FAMILY_RE = re.compile(r"^[A-Z][a-z]+idae$")


def canonical_species_tsn(itis_tsn: int | None) -> int | None:
    """Map infraspecific TSN to species-level TSN when known."""
    if itis_tsn is None:
        return None
    return SUBSPECIES_TSN_TO_SPECIES_TSN.get(itis_tsn, itis_tsn)


def target_genus(scientific_name: str) -> str | None:
    parts = scientific_name.strip().split()
    if not parts:
        return None
    return parts[0]


def is_unresolved_higher_taxon(scientific_name: str, itis_tsn: int | None) -> bool:
    """
    True when the row is a coarser taxon that could subsume species-level targets.

    Rows without a usable ``itis_tsn`` are treated as unresolved for zero-frame purposes.
    """
    name = scientific_name.strip()
    if not name:
        return True
    if itis_tsn is None:
        return True
    lower = name.lower()
    if lower in {"animalia", "pisces", "teleostei", "actinopterygii", "fish"}:
        return True
    if _UNIDENTIFIED_FISH_RE.search(name):
        return True
    if " sp." in name or name.endswith(" spp.") or name.endswith(" sp"):
        return True
    if _FAMILY_RE.match(name):
        return True
    return False


def unresolved_taxon_blocks_target(
    catch_species: str,
    catch_itis_tsn: int | None,
    target_species: str,
) -> bool:
    """True when an unresolved catch row could include ``target_species``."""
    if not is_unresolved_higher_taxon(catch_species, catch_itis_tsn):
        return False
    name = catch_species.strip()
    lower = name.lower()
    tgt_genus = target_genus(target_species)
    if tgt_genus is None:
        return False
    if lower in {"animalia", "pisces", "teleostei", "actinopterygii", "fish"}:
        return True
    if _UNIDENTIFIED_FISH_RE.search(name):
        return True
    if " sp." in name or name.endswith(" spp.") or name.endswith(" sp"):
        catch_genus = name.split()[0]
        return catch_genus == tgt_genus
    if _FAMILY_RE.match(name):
        genera = FAMILY_TO_GENERA.get(name)
        return genera is not None and tgt_genus in genera
    if catch_itis_tsn is None:
        return True
    return False
