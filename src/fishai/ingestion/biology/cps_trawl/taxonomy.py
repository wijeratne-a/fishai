"""ITIS TSN normalization and unresolved-taxa checks for zero-catch matching."""

from __future__ import annotations

import re
from typing import Final

from fishai.ingestion.biology.cps_trawl.constants import ITIS_TSN_SARDINOPS_SAGAX

# Subspecies (or infraspecific) ITIS TSN → accepted species TSN. No network lookups at runtime.
SUBSPECIES_TSN_TO_SPECIES_TSN: Final[dict[int, int]] = {
    623656: ITIS_TSN_SARDINOPS_SAGAX,  # Sardinops sagax caerulea → Sardinops sagax
}

# Family names (ITIS-style) → genera that may appear as CPS trawl targets.
FAMILY_TO_GENERA: Final[dict[str, frozenset[str]]] = {
    "Clupeidae": frozenset({"Sardinops", "Engraulis", "Clupea", "Sardinella", "Opisthonema"}),
    "Engraulidae": frozenset({"Engraulis", "Anchoa"}),
}

# Order names → genera that may appear as CPS trawl targets in the pilot.
ORDER_TO_GENERA: Final[dict[str, frozenset[str]]] = {
    "Clupeiformes": frozenset(
        {"Sardinops", "Engraulis", "Clupea", "Sardinella", "Opisthonema", "Anchoa"}
    ),
}

_UNIDENTIFIED_FISH_RE = re.compile(r"unidentified\s+fish", re.IGNORECASE)
_FAMILY_RE = re.compile(r"^[A-Za-z]+idae$", re.IGNORECASE)
_ORDER_RE = re.compile(r"^[A-Za-z]+iformes$", re.IGNORECASE)
_AMBIGUOUS_NAME_TOKENS: Final = ("unid.", "unidentified", "larvae")


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


def _genera_for_family_or_order(name: str) -> frozenset[str] | None:
    if _FAMILY_RE.match(name):
        for key, genera in FAMILY_TO_GENERA.items():
            if key.lower() == name.lower():
                return genera
    if _ORDER_RE.match(name):
        for key, genera in ORDER_TO_GENERA.items():
            if key.lower() == name.lower():
                return genera
    return None


def _has_ambiguous_name_token(scientific_name: str) -> bool:
    lower = scientific_name.lower()
    return any(token in lower for token in _AMBIGUOUS_NAME_TOKENS)


def is_genus_only_taxon(scientific_name: str) -> bool:
    """True for a single-word genus name (e.g. ``Sardinops``), not family/order ranks."""
    name = scientific_name.strip()
    if not name:
        return False
    if _genera_for_family_or_order(name) is not None:
        return False
    parts = name.split()
    return len(parts) == 1


def species_name_matches_target(catch_species: str, target_species: str) -> bool:
    """True when ``catch_species`` is the target binomial or an infraspecific of it."""
    catch_parts = catch_species.strip().split()
    target_parts = target_species.strip().split()
    if len(target_parts) < 2 or len(catch_parts) < 2:
        return False
    return catch_parts[0] == target_parts[0] and catch_parts[1] == target_parts[1]


def taxon_identity_disagreement_blocks_target(
    catch_species: str,
    catch_itis_tsn: int | None,
    target_species: str,
    target_itis_tsn: int | None,
) -> bool:
    """Name and TSN disagree on whether this row is the target species."""
    name_matches = species_name_matches_target(catch_species, target_species)
    canon_catch = canonical_species_tsn(catch_itis_tsn)
    canon_target = canonical_species_tsn(target_itis_tsn)
    if name_matches and canon_catch != canon_target:
        return True
    if (
        canon_catch is not None
        and canon_target is not None
        and canon_catch == canon_target
        and not name_matches
    ):
        return True
    return False


def catch_row_establishes_target_presence(
    catch_species: str,
    catch_itis_tsn: int | None,
    target_species: str,
    target_itis_tsn: int | None,
) -> bool:
    """True only when name and TSN both agree on the target species (or subspecies)."""
    if is_unresolved_higher_taxon(catch_species, catch_itis_tsn):
        return False
    if taxon_identity_disagreement_blocks_target(
        catch_species, catch_itis_tsn, target_species, target_itis_tsn
    ):
        return False
    canon_catch = canonical_species_tsn(catch_itis_tsn)
    canon_target = canonical_species_tsn(target_itis_tsn)
    if canon_catch is None or canon_target is None or canon_catch != canon_target:
        return False
    return species_name_matches_target(catch_species, target_species)


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
    if _has_ambiguous_name_token(name):
        return True
    if " sp." in name or name.endswith(" spp.") or name.endswith(" sp"):
        return True
    if _genera_for_family_or_order(name) is not None:
        return True
    if is_genus_only_taxon(name):
        return True
    return False


def unresolved_taxon_blocks_target(
    catch_species: str,
    catch_itis_tsn: int | None,
    target_species: str,
    target_itis_tsn: int | None = None,
) -> bool:
    """True when an unresolved catch row could include ``target_species``."""
    if target_itis_tsn is not None and taxon_identity_disagreement_blocks_target(
        catch_species, catch_itis_tsn, target_species, target_itis_tsn
    ):
        return True
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
    if _has_ambiguous_name_token(name):
        return True
    if " sp." in name or name.endswith(" spp.") or name.endswith(" sp"):
        catch_genus = name.split()[0]
        return catch_genus == tgt_genus
    genera = _genera_for_family_or_order(name)
    if genera is not None:
        return tgt_genus in genera
    if is_genus_only_taxon(name):
        return name.split()[0] == tgt_genus
    if catch_itis_tsn is None:
        return True
    return False
