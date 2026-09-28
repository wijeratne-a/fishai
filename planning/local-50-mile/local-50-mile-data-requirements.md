# Local 50-mile data requirements

**Date:** 2026-09-23  
**Status:** Planning only  
**Scope:** What a training or evaluation row must contain before any 50-mile nowcast is fitted.

No survey or ocean file is downloaded by this note. No model is fitted. Public download remains distinct from training permission (`RVC_RIGHTS_RECORD.md`).

---

## Unit of analysis

One row is one **protocol-matched event** inside a stated spatial support (sample unit, tow, transect segment, or sampler event), not a compiled occurrence pin and not a 50-mile circle.

A 50-mile user window is a **query and display** radius. It is not the likelihood unit unless the survey design itself is defined at that scale (it usually is not).

---

## Required fields on every biological training row

| Field | Requirement |
|---|---|
| **Event id** | Stable sample-unit / tow / transect / sampler identifier from the provider frame |
| **Date** (and time if published) | Event time used for environmental match; survey-season label only if day is incomplete and the card says so |
| **Depth** | Recorded sample or gear depth; do not substitute a species maximum-depth encyclopedia value |
| **Method** | Named protocol (e.g. RVC two-stage visual; CUFES; bottom trawl). Version or stage changes across years are fields, not footnotes |
| **Effort** | Protocol unit of search or catch: completed diver survey, tow duration/distance, sampler volume/time, recorder duty cycle—as actually present on the approved extract |
| **Detection / non-detection** | Species (or egg / taxon) present under the protocol code, or a **verified** zero from the complete sample frame. A missing species row is not a zero until that rule is proven on the opened table |
| **Habitat / stratum** | Survey habitat code or stratum used in the design |
| **Environmental match keys** | Time, location support, and depth band used to join covariates without claiming finer resolution than the source |
| **Rights** | Written training permission, storage path outside the public repo if required, attribution string, and display class for any derived aggregate |
| **Sensitivity** | Flag for coordinate withholding, coarsening rules, and reviewer hold. Native coordinates stay out of git, the app, fixtures, logs, and diffs |

Rows that fail rights, zeros, or method consistency are not training rows. They may still support a **Historical pattern** or **Unknown** display state (`local-50-mile-coverage-framework.md`).

---

## Biological requirements

- Species or taxon identity must match the estimand (adult reef fish ≠ pelagic eggs ≠ eDNA MOTU without an explicit bridge study).
- Positive-only extracts fail the training gate (`TRAINING_DATA_HURDLE.md`, `FIRST_MODEL_FEASIBILITY.md`).
- Multi-year pools need a protocol-match field. Example already on record: NCEI 0282183 landing page describes two-stage design; 0306184 landing page describes single-stage—those seasons are not the same likelihood without an explicit model for the change (`RVC_MULTIYEAR_READINESS.csv`).
- OBIS/GBIF compiled rows may inform historical context only. They do not supply effort-aware non-detections.

### Gear metrics are not interchangeable

Do not pretend one effort currency.

| Example | Effort meaning |
|---|---|
| RVC second-stage plot | Completed visual search of a ~15 m diameter / 7.5 m radius cylinder (Smith et al. 2011; NCEI method text) |
| Bottom trawl tow | Gear, speed, duration, distance, and selectivity of that net |
| CUFES / ichthyoplankton | Sampler volume, underway track, and lab identification protocol |
| eDNA | Water volume, filtration, assay, and contamination controls |
| PAM | Duty cycle, detection range assumptions, and call classification rules |

A trawl tow is not a 15 m visual plot. A CUFES egg density is not a wreck-fish detection. Mixing gears without method-specific detection models invents skill.

---

## Environmental requirements

- Covariates must match the biological event’s time and spatial support (`FIRST_MODEL_FEASIBILITY.md` Gate C).
- Ocean model or satellite fields are **environment**, not observations of the animal.
- Forecast products may support a later forecast layer only after a nowcast is stable and the card reports skill by lead time.
- Operational numbers quoted in external strategy briefs (grid spacing, vertical levels, forecast length, API rate limits) stay labeled as brief claims until confirmed from a page actually read in a rights or ingest pass.
- No local environmental lake is assumed present in this repo today.

---

## Habitat requirements

- Prefer habitat or stratum fields already on the survey sample.
- External habitat maps, if used, must be aggregated to the sample unit and must not be published as site pins.
- Habitat suitability alone is a baseline story, not a sighting.

---

## Rights and storage (minimum)

Before any row enters a training table:

1. Written yes/no for acquisition, storage outside the public repository, training, and coarsened aggregate display.
2. Frozen file identity (URL, retrieval time, file name, byte size, SHA-256) after approval—not before.
3. Citation and subset phrase completed for the extract actually used.
4. Coordinate policy: withhold native coordinates; no wreck, spawning-site, nursery, telemetry-track, or fishing-guidance geometry in the product.
5. Observer, VMS, and similar confidential streams stay out of the public product unless a written confidentiality review allows a named aggregate output.

Until those exist, readiness stays below HIGH and the correct issued state remains historical atlas behavior or **Unknown**—consistent with goliath `NOT_PUBLISHED` and no nowcast issued.
