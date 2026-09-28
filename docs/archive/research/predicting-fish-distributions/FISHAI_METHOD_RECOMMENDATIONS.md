# FishAI method recommendations

Answers the ten required questions. Ranked with the program labels. Details and matrices in the rest of this folder. Source ids: `SOURCE_INDEX.csv`.

## 1. What FishAI can model now

**Survey detection probability (question 2)** for common species in zero-bearing frames: Keys RVC, Puerto Rico RVC, USVI RVC, Flower Garden Banks RVC, and SBC LTER kelp transects.

Method: L2 logistic or a simple GAM on habitat, depth, and visibility (and same-day kelp on SBC), no year dummies, scaler on training years, missing covariates refused, one locked later year, Brier and log loss versus prevalence.

**DO_NOW.** One species at a time. Most will lose. A loss is a result.

Do not cite Puerto Rico 2023. Do not treat Keys damselfish calibration failure as a pass.

## 2. After historical environmental joins

**DO_AFTER_ENVIRONMENTAL_JOINS**

- Join bathymetry and benthic habitat (not empty `data/raw/habitat/`) to Keys RVC events.
- Retry temperature at depth only as a pre-registered hypothesis, frozen on training-year spatial CV, scored on an unused year. It already failed as a kept feature for Keys damselfish and SBC kelp bass.
- Spatial GLMM / sdmTMB on Keys RVC (hundreds of sites per year), not on 11 SBC sites.
- Survey center-of-gravity on that Keys spatial model (`DO_AFTER_ENVIRONMENTAL_JOINS`): within-domain Q5, not individual tracks. Eleven SBC sites cannot support a regional COG (P316).
- Support masks from training habitat and depth.

This still answers questions 1–2, not a nowcast. An environmental term is kept only if it beats survey-only on a locked later year.

## 3. After more structured survey data

**DO_AFTER_MORE_STRUCTURED_DATA**

- Full multi-year trawl series (DATRAS, DFO, or a U.S. bottom-trawl program) for relative abundance (question 3) and seasonal redistribution (question 5).
- Pacific NCRMP only if zeros can be reconstructed from a published species list; otherwise presence-only.
- Channel Islands or PISCO kelp surveys if a new test year is available (SBC 2022 is burned).
- Repeat visits or a second method at sentinel sites if occupancy (true presence versus detection) is the target.

## 4. What needs telemetry

**REQUIRES_TELEMETRY**

- Individual movement (question 4).
- Utilization distributions and behavioral states for tagged animals only.
- Movement-informed population models, and only if tags are representative.

Minimum program: a published array or Argos/PSAT dataset, detection-range tests, and an agreement that tracks stay internal (S02, S11, S12, S84, S85). Do not infer tracks from survey pins (`MODEL_SELECTION_RULES.md`).

## 5. What needs eDNA, acoustics, or cameras

**REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA** or **DO_AFTER_MORE_STRUCTURED_DATA** depending on public archives.

- eDNA: occupancy with contamination and transport as the observation model, not presence pins (S37).
- PAM: local presence of sound-producing taxa, with propagation and noise (S31, S32).
- BRUV / stereo video: relative abundance with bait and field-of-view as effort.

These do not replace RVC. They get their own likelihoods (S69, S70).

## 6. What public occurrence records can never support

**NOT_RECOMMENDED** as a detection or abundance model.

OBIS, GBIF, iNaturalist, and catch apps cannot give non-detections, effort, abundance, current location, or nowcast validation (S67, S68, S80). They may sit as a separate relative-intensity stream with an explicit bias model.

## 7. Minimum viable regional nowcast

**UNSUPPORTED_BY_AVAILABLE_EVIDENCE** today.

Required, all of them:

1. A survey-detection or distribution model whose environmental term beat survey-only on a locked later year.
2. Current analyzed ocean fields at the relevant depth, available at issue time. GOFS 3.1: hycom.org archive ends **2024-09-04** (P500); FishAI preregistration used **2024-09-05** — do not collapse. ESPC-D-V02 is the active analysis from 2024-08-10 (P501).
3. Independent observations in the same window after the freeze.
4. Skill versus climatology of that window.
5. Coarsening, delay, and a non-location label.

FishAI fails (1) and (3). Archiving analyses now is the only nowcast work that is not pretend.

## 8. Minimum viable short-term forecast

**UNSUPPORTED_BY_AVAILABLE_EVIDENCE** today.

Everything in section 7, plus archived ocean forecasts with issue and valid times, and skill by lead versus climatology and persistence. RTOFS remains on NOMADS HTTPS (`rtofs.20260926/27`, P507) after OpenDAP retirement 2026-02-23 (P506); CoastWatch ERDDAP RTOFS search HTTP 404 (P508). ESPC-D-V02 forecast folder retains only the last 8 runs then scrubs them (P501). Start archiving; do not issue a fish forecast.

Seasonal habitat forecasts for tuna and dolphinfish exist in the literature (Hobday, Eveson, Brodie). They are management tools with their own validation, not a template to copy onto reef-fish RVC.

## 9. Claims to refuse

- Live location of untagged fish.
- Global or regional abundance from presence-only data.
- Survey zeros as ecological absence.
- SST or chlorophyll as a fish map. Surface SST is not a bottom proxy unless mixed-layer depth is verified at occupied depth.
- Particle tracks as adult movement. Wrong larval vertical behaviour can beat a passive model in the wrong direction (Bode et al. 2019, P312); Q6 stays `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA`.
- Spatial CV as a nowcast test.
- Accuracy percentages for rare or common species.
- Harvest, hotspot, or "where to fish" language.
- Any published layer without `PUBLISHED` and a support mask.

## 10. Highest expected improvement per unit of data and complexity

**DO_NOW:** more common species on existing zero-bearing RVC frames, same locked protocol as Keys damselfish.

**Next increment:** habitat and bathymetry joins for Keys spatial models (`DO_AFTER_ENVIRONMENTAL_JOINS`).

**Do not spend complexity on:** a generic fish model, MaxEnt on GBIF, N-mixture on single-visit RVC, nowcast dashboards, or commercial fishing-forecast clones.

| Rank | Action | Label |
|---|---|---|
| 1 | Locked survey-detection models for more Keys and other RVC species | `DO_NOW` |
| 2 | Habitat rasters + spatial GLMM on Keys | `DO_AFTER_ENVIRONMENTAL_JOINS` |
| 3 | Archive ocean analyses and forecasts with issue times | `DO_AFTER_ENVIRONMENTAL_JOINS` |
| 4 | Multi-year trawl or additional kelp-forest programs with a fresh test year | `DO_AFTER_MORE_STRUCTURED_DATA` |
| 5 | Sentinel contemporaneous observations for a future nowcast test | `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA` |
| 6 | Telemetry partnership, internal | `REQUIRES_TELEMETRY` |
| — | Presence-only occurrence models as the product | `NOT_RECOMMENDED` |
| — | Nowcast or forecast issuance | `UNSUPPORTED_BY_AVAILABLE_EVIDENCE` |
