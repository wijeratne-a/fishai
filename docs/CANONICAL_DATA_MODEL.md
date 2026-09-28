# Canonical data model

**Status:** Binding contract for normalized FishAI records.  
**Schemas:** `schemas/*.schema.json` (JSON Schema draft-07).

## Entities

| Entity | Role |
|---|---|
| **Source** | Registry entry; owns rights, license, protocol, coordinate policy |
| **Event** | Protocol sample unit (dive, tow, transect, sampler event) |
| **Observation** | Taxon result on an event (presence, verified non-detection, or unknown) |
| **Effort** | Completed search/catch unit; required to mint survey non-detections |
| **Taxon** | WoRMS-backed identity |
| **Measurement** | Typed value; may be biological or environmental |
| **Provenance** | Raw bytes + transform + rights snapshot |
| **GlobeEvidence** / **GlobeModelOutput** | Public products — see `GLOBE_DATA_CONTRACT.md` |

## Hard rules

1. **Missing rows are not absences.** A species absent from a table is `NO_SURVEY` / `UNKNOWN` until a complete protocol frame proves a non-detection.
2. **Protocols stay separate.** Do not pool incompatible methods without an explicit bridge model.
3. **SST is not a fish observation.** Environmental measurements use `subject_kind=ENVIRONMENTAL` and evidence `ENVIRONMENTAL_CONDITION`.
4. **Presence-only is not absence.** Sources with `presence_only=true` cannot mint zeros.
5. **Internal models are not published nowcasts.** `INTERNAL_MODEL_OUTPUT` ≠ `PUBLISHED_NOWCAST`.
6. **No fishing guidance.** Public products set `fishing_guidance=false`.
7. **No raw coordinates on globe outputs.** Public geometry is `spatial_cell_id` (or official unit) only.
8. **Time precision is explicit:** `SECOND` \| `MINUTE` \| `HOUR` \| `DAY` \| `MONTH` \| `YEAR` \| `UNKNOWN`.
9. **Do not invent minimum sample sizes.** Use `THRESHOLD_REQUIRES_POWER_ANALYSIS`.

## Observation states

| State | Meaning |
|---|---|
| `CONFIRMED_PRESENCE` | Protocol recorded the taxon |
| `SURVEY_NONDETECTION` | Completed effort + taxon in frame + no detection |
| `PRESENCE_ONLY_NO_ABSENCE` | Positive-only extract; gaps are not zeros |
| `NO_SURVEY` | No protocol ran → unknown, not absent |
| `RESTRICTED` | Exists but withheld/coarsened |
| `UNKNOWN` | Insufficient evidence |

## Layers (summary)

`raw` → `normalized` (these schemas) → `feature` → `prediction` → `product`. Public/product layers drop native lat/lon.
