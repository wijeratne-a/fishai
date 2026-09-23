# Observation coverage maps

**Date:** 2026-09-18  
**Owner (this file + CSV):** OBSERVATION_MODALITY cluster  
**Machine table:** `taxa_modality_feasibility.csv` (15 taxon classes × 13 modalities = **195** rows).  
**Regenerate:** `python3 _build_feasibility.py` (catalog-only; no ingest).

This is a **feasibility** map, not a measured coverage fraction of the ocean. Global percent-area observed is **UNKNOWN** for almost every biological target; do not invent completeness numbers.

Depth / uncertainty maps for the twin belong to other observatory agents. This folder answers: *if we point modality X at taxon class Y, what class of claim is honest today?*

---

## Codes in the CSV

| Column | Values |
| --- | --- |
| `primary_class` | `DIRECT` · `INFERRED` · `FORECAST` · `NEEDS_INFRA` · `UNPROVEN` · `SPECULATIVE` · `IMPOSSIBLE` · `MIXED` · `LIMITED` |
| `direct_today` etc. | `YES` · `CONDITIONAL` · `LIMITED` · `NO` |
| `what_*` | Plain-language claims; empty only if the flag is `NO` |
| `confidence` | `HIGH` · `MEDIUM` · `LOW` |
| `as_of_date` | 2026-09-18 |

`LIMITED` as primary_class = the modality works only in a narrow setting (clear water, vocal species, tagged subset, intertidal, etc.).

`MIXED` = both a real direct path and a hard impossible path (e.g. VHR whales vs VIIRS fish).

---

## Compact primary-class matrix

D=DIRECT · I=INFERRED · L=LIMITED · M=MIXED · N=NEEDS_INFRA · U=UNPROVEN · X=IMPOSSIBLE

| taxon | M01 sat | M02 air | M03 opt | M04 EK | M05 PAM | M06 eDNA | M07 tag | M08 auto | M09 fix | M10 vessel | M11 DAS | M12 proxy | M13 human |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| finfish | I | L | D | D | L | D | D | N | I | D | U | I | D |
| sharks_rays | M | D | D | L | X | D | D | N | I | D | X | I | D |
| shellfish | I | L | D | L | X | D | L | I | D | D | I | I | D |
| crustaceans | X | X | D | L | L | D | D | I | I | D | X | I | D |
| cephalopods | I | L | D | L | X | D | L | N | I | D | X | I | L |
| marine_mammals | M | D | L | L | D | D | D | M | D | D | D | I | D |
| turtles | I | D | L | X | X | D | D | I | I | D | X | I | D |
| seabirds | M | D | L | X | X | L | D | I | L | D | X | I | D |
| plankton | D | L | D | D | X | D | X | D | D | D | I | I | L |
| jellyfish | U | L | D | L | X | D | X | N | L | D | X | I | D |
| corals | M | D | D | L | L | D | X | D | I | L | I | I | D |
| benthos | L | L | D | L | L | D | L | D | L | D | X | I | L |
| plants_algae | D | D | D | L | X | D | X | L | L | L | X | I | D |
| microbes | D | L | D | X | X | D | X | D | D | D | X | D | L |
| larvae | I | X | D | L | X | D | X | N | L | D | X | I | L |

**How to use:** do not advertise a `D` as global operational tracking. Read the `what_directly_observed` cell. Example: finfish × M01 is **I** on purpose — satellites do not see fish; they see habitat that must be fused with acoustics/eDNA/tags/vessels.

---

## Highest-leverage cells for currently invisible life

| Gap | Best next modality | Why |
| --- | --- | --- |
| Mesopelagic fishes | M04 opportunistic EK + M03 AUV cameras + M06 | Light does not reach; EK sees scatterers; cameras/eDNA name them |
| Cryptic / rare taxa | M06 time series on SOOP/IOOS | Occupancy without capture |
| Vocal whales in dark/ice | M05 + M11 DAS | Demonstrated; light-independent |
| Benthic infauna | M06 sediment + M03 grabs/ROV | Satellites cannot |
| Lobster/crab “from space” | M09/M08 **bottom T** + M10 CPUE | M01 SST is the wrong variable (X) |
| Larvae as named organisms | M03 imagers + M06 (stage mixed) + M12 transport | M01 particle tracking is water, not larvae |
| Microbes in 3D / under cloud | M08 BGC-Argo + M01 PACE | Design array not filled |

---

## What this is not

- Not measured % of ocean volume surveyed.  
- Not TRLs (mostly **UNKNOWN**).  
- Not a licence to ingest OBIS/ATN/CMEMS.  
- Not precise maps of listed species.
