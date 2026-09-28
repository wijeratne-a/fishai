# Multi-species nowcast infrastructure framework (proposal)

**Date:** 2026-09-23  
**Status:** PROPOSAL ONLY  
**Issued product:** None

This note is a **proposed infrastructure map** drawn from an external briefing on multi-species marine nowcasting. **Nothing in it is ingested or operational in this repository.** It does not download data, fit a model, clear rights, change the globe UI, or publish a species card. Existing FishAI gates stay in force: no nowcast or forecast is issued; California Current sardine/anchovy MVP remains PROPOSAL ONLY (`planning/local-50-mile/local-50-mile-prediction-mvp.md`); Florida Keys goliath grouper stays card `NOT_PUBLISHED`, feasibility `CONDITIONAL GO`, RVC rights `CONDITIONAL_REVIEW_REQUIRED`, zeros and `EPIITAJ` unverified, accession 0208321 set aside (`species/goliath-grouper/TRAINING_DATA_HURDLE.md`, `RVC_RIGHTS_RECORD.md`).

Public landing pages are not training permission. A missing species row is not a zero unless the full sample frame proves the survey event happened.

---

## Biological standards

Structured biological exchange should follow OBIS/GBIF practice and Darwin Core (DwC):

| Concept | Planning use |
|---|---|
| **Event Core vs Occurrence Core** | Prefer Event Core when effort and sample events matter; Occurrence Core alone is presence-oriented and weak for zeros |
| **occurrenceStatus=absent** and **individualCount=0** | Usable as non-detections **only when the publisher recorded a completed protocol** for that event—not when a species simply lacks a row in a presence-only dump |
| **parentEventID** | Links nested samples (station → tow → subsample) so effort is not double-counted |
| **eMoF** (extended Measurement or Fact) | Holds depth, gear, effort metrics, and assay covariates without inventing new core terms |
| **ISO 8601 dates** | Event time for joins to environmental fields |
| **EPSG:4326** | Default geographic CRS for planning; native high-resolution coordinates stay out of the public product |

DwC absence flags are **not** automatic training zeros. They are usable only when the publisher actually recorded a completed protocol and the project has written rights to store and use that event.

---

## Trait and taxonomy context

**FishBase** and **WoRMS** are taxonomy and trait lookup services (names, AphiaIDs, life-history attributes). They are **not** sightings, survey effort, or non-detection frames. They do not clear a nowcast and do not replace a protocol-matched biological extract.

---

## eDNA (candidate method family)

Darwin Core **DNA Derived Data** extension fields (sample material, assay, target taxon, and related lab metadata) are the intended exchange pattern if eDNA is ever considered. Planning caveats from the briefing:

- **False positives:** transport, wastewater, and other non-local DNA can produce detections that are not current animal presence at the sample site.
- **False negatives:** assay sensitivity, inhibition, and sparse sampling miss animals that were present.
- **Multi-level occupancy:** site → capture → PCR (or equivalent) hierarchy is the honest likelihood structure—not a single “detected here” pin.

eDNA is **not** a current-location product in FishAI planning. It does not authorize wreck, nursery, spawning, or telemetry coordinates, and it is not ingested here.

---

## Regional survey families (CANDIDATES)

Each family below is a **candidate** for a future rights-cleared, effort-aware extract. None is verified as ingested, zero-checked, or operational in this repo.

### NEFSC bottom trawl

Northeast Fisheries Science Center bottom-trawl and related shelf survey products are a structured tow-effort family for the Northeast US continental shelf. Gear and design are not interchangeable with reef visual census or egg samplers. **Not verified in this repo.**

### SEAMAP trawl and longline

Southeast Area Monitoring and Assessment Program trawl and longline products are fishery-independent candidates for US Southeast / Gulf / Mid-Atlantic footprints. Design-based zeros are possible only where a complete sample frame exists; that is unverified here. **Not verified in this repo.**

### G-FISHER S-BRUV

G-FISHER stereo baited remote underwater video (S-BRUV) style products are a candidate visual-video family. Native habitat maps stay **internal and coarsened** if ever approved; this note does not list wrecks, platforms, or geoform coordinates. **Not verified in this repo.**

### CalCOFI / CUFES

California Cooperative Oceanic Fisheries Investigations and Continuous Underway Fish Egg Sampler products are the proposed biological side of the California Current local-50-mile MVP (PROPOSAL ONLY). Egg or encounter protocols are not reef visual effort. **Not verified in this repo.**

### NCRMP / RVC

National Coral Reef Monitoring Program Reef Visual Census remains the strongest structured candidate on paper for Florida reef fish, including the Keys goliath path. Repo reconciliation: the Bohnsack/Bannerot stationary point count uses a **7.5 m radius** cylinder, matching Smith et al. 2011 as cited on NCEI pages; zeros and `EPIITAJ` are **unverified** (tables not opened); rights remain **`CONDITIONAL_REVIEW_REQUIRED`** with exit gate **`BLOCKED`**; accession **0208321** is set aside as too old for the first training extract (`RVC_RIGHTS_RECORD.md`, `TRAINING_DATA_HURDLE.md`). Public pages are not training permission. **Not verified as an approved extract in this repo.**

### IMOS / AODN

Integrated Marine Observing System and Australian Ocean Data Network products are candidate observing-system families for Australian footprints. Effort and non-detections depend on the specific product. **Not verified in this repo.**

### Reef Life Survey

Reef Life Survey diver visual products are a candidate structured-visual family. Non-detections apply only where the method defines search completion. **Not verified in this repo.**

### Passive acoustic monitoring (PAM)

Hydrophone networks can supply detections and duty-cycle effort, but sound propagation uncertainty means acoustic non-detection is not visual absence and does not produce animal tracks. **Not verified in this repo.**

---

## Environmental forcing

**WCOFS / ROMS**-class ocean models are a **candidate covariate source** for West Coast joins (surface and related fields), aligned with the California Current MVP proposal.

Figures from the briefing—any grid size, vertical level count, **24 h nowcast**, or **72 h forecast** horizon—are **stated in the briefing, not independently verified in this pass.** Biases mentioned in the briefing (for example salinity fronts and mixing) are **caveats**, not measured errors quantified in this repository. No environmental lake is stored or joined here.

---

## Access pattern

**ERDDAP** `griddap` (grids) and `tabledap` (tables) is the **intended retrieval pattern** if an approved ingest design is written later. Rate limits described in the briefing are **unverified here**. **No pipeline exists yet.**

---

## Rights and display constraints

- **MSA observer confidentiality** and the **rule of three** are **display constraints** for any future aggregate fishery product.
- This note does **not** describe how to obtain raw observer or VMS data.
- **Raw commercial locations stay out of the public product.**
- Native survey coordinates, wrecks, nurseries, spawning sites, and telemetry tracks are not added by this framework.
- No `APPROVED_*` rights are assigned here. Candidate families default to `CONDITIONAL_REVIEW_REQUIRED` until a human records written approval; raw observer coordinates for public display remain `BLOCKED`.

---

## Model family (PROPOSED, not fitted)

A candidate engine for later work—not a fit in this repo:

| Element | Planning note |
|---|---|
| **sdmTMB-class spatial GLMM** | Spatiotemporal generalized linear mixed model family as a proposed engine |
| **Barrier mesh** | Spatial correlation should not cross land |
| **Delta / hurdle** | Presence then positive count (or density), because marine surveys are zero-heavy |
| **Baselines** | Seasonal, effort-only, and simple spatial smoothers still have to be beaten before any predictive claim |
| **Evaluation options** | Boyce, TSS, and AUC are named options for a **later** holdout design—not results |

Do not treat this section as a fitted equation, skill score, or published model card. No model is fitted. The goliath card stays `NOT_PUBLISHED`. The California Current MVP stays PROPOSAL ONLY.

---

## What this does not unlock

- Training on any survey extract
- A 50-mile nowcast or forecast
- Any change to the Florida Keys goliath grouper card, rights record, or feasibility status
- Ingest of OBIS/GBIF as effort-aware zeros
- Public display of observer, VMS, or sensitive-site coordinates

Coverage vocabulary and readiness classes remain in `planning/local-50-mile/local-50-mile-coverage-framework.md`. Source family rows for this map are in `SOURCE_FAMILIES.csv` in this folder.

---

PROPOSAL ONLY — no multi-species nowcast or forecast is issued
