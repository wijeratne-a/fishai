# Observation semantics (WS41)

**Status:** Binding label semantics for biological records.  
**Schema:** `labels/BIOLOGICAL_LABEL_SCHEMA.json`  
**Rules:** `labels/LABEL_VALIDATION_RULES.yaml`

## Observation outcomes

| Outcome | Meaning | Ecological absence? |
|---|---|---|
| `DETECTED` | Protocol recorded the taxon (any positive length bin or count under the source rule) | No claim about surrounding habitat |
| `EXPLICIT_SURVEY_NONDETECTION` | Publisher recorded a completed protocol zero for the target | **No** — protocol miss only |
| `CONSTRUCTED_SURVEY_NONDETECTION` | Derived after collapsing to species level under a documented complete frame | **No** — protocol miss only |
| `REPORTED_ABSENT` | Source explicitly reports absence language; still not proof of ecological absence without a completed frame | **No** by default (`is_ecological_absence_claim` stays false) |
| `PRESENCE_ONLY` | Positive record; gaps elsewhere are not zeros | No |
| `NOT_EVALUATED` | Taxon not in the published search universe, or no protocol for that target | Unknown, not absent |
| `UNKNOWN` | Insufficient evidence to label | Unknown |
| `INVALID_EVENT` | Event failed QC or is incomplete; do not mint detections or zeros | Unknown |

## Hard prohibitions

Do **not** equate any of the following with ecological absence or validated non-detection:

1. **Missing rows** — no row for a species means `NOT_EVALUATED` until a complete event frame proves otherwise.
2. **Zero counts alone** — a single `NUM == 0` length-bin row is not the species result on Atlantic RVC extracts.
3. **Habitat suitability** — suitable habitat is not an observation.
4. **SST / environmental fields** — covariates only (`evidence_tier=ENVIRONMENTAL_COVARIATE`).
5. **Telemetry positions** — individual tracks, not population non-detections.
6. **Citizen-science observations** — not standardized survey effort zeros.
7. **Acoustic classifier outputs** — not validated species presence without review.
8. **eDNA read absence** — assay non-detection is not a visual or occupancy zero without an assay-level protocol.

## Atlantic RVC / NCRMP (Florida Keys, Puerto Rico, USVI, Flower Garden Banks)

- `NUM` is a real-valued average, not an integer fish count.
- Multiple rows per species exist because of **length bins**.
- **Detection:** any row for the species code on the event has `NUM > 0`.
- **Species-level constructed non-detection:** the code is on that year’s fixed species list **and** every length-bin row for the code has `NUM == 0`, after length-bin collapse.
- A single `NUM == 0` row is **not** itself the species result (`zero_provenance=LENGTH_BIN_ROW_ONLY`).
- Outcome for valid constructed zeros: `CONSTRUCTED_SURVEY_NONDETECTION`.
- Requires: `event_completed=true`, `event_frame_complete=true`, non-empty `target_taxonomic_group`, valid `protocol_version`, `zero_semantics_documented=true`.

## Pacific NCRMP COUNT tables

- Positive counts only; downloaded extracts contained **no zeros**.
- Label positives as `DETECTED` or `PRESENCE_ONLY` with `count_type` as published.
- Do **not** invent non-detections from missing taxa (`PRESENCE_ONLY` / presence-only gap).

## OBIS Keys extract

- Compiler occurrences → `PRESENCE_ONLY`.
- Not equivalent to RVC zeros. Missing species are `NOT_EVALUATED`, never constructed zeros.

## CalCOFI CUFES sample

- Egg counts from a continuous underway fish egg sampler.
- `life_stage=egg`; `count_type=EGG_COUNT`.
- **Not** adult occurrence and **not** a reef-fish detection model label.

## Non-detection minting checklist

A non-detection label (`EXPLICIT_SURVEY_NONDETECTION` or `CONSTRUCTED_SURVEY_NONDETECTION`) is valid only when all hold:

1. Completed event (`event_completed`)
2. Defined target taxonomic group
3. Valid observation protocol (`protocol_version`)
4. Complete event frame (`event_frame_complete`)
5. Documented zero semantics (`zero_semantics_documented`)
6. `is_ecological_absence_claim` remains `false`
