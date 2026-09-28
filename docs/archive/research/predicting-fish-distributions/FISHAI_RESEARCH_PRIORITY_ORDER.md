# FishAI research priority order

Ordered by expected scientific return given data already on disk, remaining clean test years, and harm if the output is misread as a fish finder.

## P0 — Do not spend effort here

| Item | Why |
|---|---|
| Rescoring Puerto Rico 2023, Keys 2022 damselfish, or SBC 2022 bass | Locks exist. Rescoring is not new evidence |
| A single macro "fish" or guild model | Species on the same dive do not share a detection rate |
| MaxEnt / GBIF as the product | No zeros, no effort (S67, S68) |
| N-mixture on RVC | Single visit, no closure (S43; later critiques) |
| Issuing a nowcast or fishing forecast | No contemporaneous labels; no archived fish-relevant forecasts |
| Public hotspot or catch maps | Safety boundary |

## P1 — `DO_NOW`

1. Inventory common RVC species with explicit zeros and enough detections; fit one locked survey-detection model at a time (Keys first: 2022 unused for species other than bicolor damselfish, with design-exposure disclosed).
2. Keep the Keys damselfish card as the template: freeze, hash, score once, Brier and log loss versus prevalence, calibration, `NOT_PUBLISHED`.
3. Start a WoRMS accepted-name map so codes do not split a species (audit TAX-001). No invented AphiaIDs.
4. Keep writing run manifests. Do not expand the globe.

## P2 — `DO_AFTER_ENVIRONMENTAL_JOINS`

1. Public bathymetry and benthic habitat for the Keys box; join to events; spatial GLMM or sdmTMB with a barrier or land mask (S72, S73).
2. Depth-resolved temperature as a hypothesis only, never as a required feature. Product shift from GOFS 3.1 to ESPC-D-V02 must be tested, not assumed.
3. Begin an analysis and forecast archive with issue and valid times. ESPC-D-V02 forecast folder keeps ~8 runs then scrubs them (P501). RTOFS: NOMADS HTTPS still live 2026-09-26/27 (P507); OpenDAP retired 2026-02-23 (P506); do not wait for CoastWatch ERDDAP (404, P508). The archive is for a future test, not a product launch.

## P3 — `DO_AFTER_MORE_STRUCTURED_DATA`

1. Multi-year trawl (complete DATRAS or a U.S. survey) for hurdle / VAST indices.
2. Another kelp-forest frame (Channel Islands, PISCO) with a test year that is not SBC 2022.
3. Pacific RVC only after a documented zero constructor.

## P4 — `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA`

1. Sentinel sites with structured checklists, PAM, or replicated eDNA timed to a nowcast freeze.
2. Larval connectivity only with PLD, vertical behavior, and genetic or recruitment validation (S62, S63; Bode et al. 2019 P312: wrong behaviour can lose to a passive model). CalCOFI cruise 202204 is not enough.

## P5 — `REQUIRES_TELEMETRY`

Movement research for tagged animals, internal, coarsened, no receiver maps (S02, S84, S85). After the survey-detection layer is routine, not instead of it.

## Stopping rules

- Stop adding covariates when they fail locked later-year tests.
- Stop modelling a species below the detection floors (50 train / 10 test).
- Stop any path that needs a public fine map of aggregations.
- Stop calling spatial CV a nowcast.

## Alignment with evidence tiers

This order is Level 1 expansion, then a Level 2 habitat gate, then archives for a possible Level 3. It is not a jump to a digital twin (`FISHAI_ROADMAP_BY_EVIDENCE_TIER.md`).
