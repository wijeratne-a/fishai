# Predicting fish distribution from sparse data — executive summary

**Date:** 2026-09-27  
**Scope:** Research and methodology only. No application code, no model fits, no globe edits, no fishing recommendations.

**CORE PROBLEM:** "Where are the fish?" is nine different questions (distribution, survey detection, abundance, individual movement, population redistribution, larval connectivity, nowcast, forecast, climate). Sparse, biased observations can support some of them. They cannot support a live map of untagged fish.

**WHAT FISHAI CAN REALISTICALLY PREDICT:** The chance that a completed, documented survey records a named common species in a named region, method, and season. That is question 2. One internal example exists: Florida Keys bicolor damselfish, trained 2014/2016/2018, scored once on 2022, Brier 0.095 versus prevalence 0.125. It ranks dives well and ran about 5 points high overall. Not published. Not a location.

**WHAT FISHAI CANNOT PREDICT:** Where an untagged fish is now; abundance from presence-only records; movement without tags; larval connectivity from one CalCOFI cruise; a nowcast or forecast that beats climatology (no contemporaneous labels, no archived fish-relevant forecasts used in a locked test); most species even on good surveys (14 of 16 older models failed; both Santa Barbara bass models failed 2022).

**BEST NEAR-TERM METHOD:** Locked survey-detection models (L2 logistic or simple GAM) on zero-bearing RVC and similar frames; habitat, depth, visibility; no year dummies; Brier and log loss versus prevalence; one unused later year.

**BEST LONG-TERM METHOD:** The same observation-process discipline, plus spatial GLMMs on dense survey frames, habitat rasters, optional environmental terms that survive locked later-year tests, and only then analysis-driven nowcast research if contemporaneous observations exist. Telemetry and larval models stay separate questions.

**MOST IMPORTANT NEW DATA:** (1) more unused survey years and more species on existing zero-bearing frames; (2) bathymetry and benthic habitat rasters; (3) archived ocean analyses and forecasts with issue times; (4) contemporaneous sentinel observations; (5) telemetry only for movement research.

**MOST IMPORTANT ENVIRONMENTAL VARIABLES:** Survey habitat, depth, and visibility first. Structure and bathymetry next for reef fish. Depth-resolved temperature is a hypothesis, not a default (it failed as a kept feature for Keys damselfish and SBC kelp bass). Surface SST is not a bottom proxy unless mixed-layer depth is verified at occupied depth. Chlorophyll is often unusable over shallow reef.

**BEST VALIDATION DESIGN:** Freeze and hash before opening test labels; score once; cluster bootstrap by site; proper scores versus a named baseline; refuse missing covariates and out-of-range inputs; never use future-day fields.

**COMMERCIAL TOOL INSIGHTS WORTH ADAPTING:** Name the layer (SST, depth, AIS, backscatter are not fish); store issue time and valid time; put uncertainty on the map (WhaleWatch); bathymetry and fronts as covariate hypotheses; EcoCast-style one-question validation (S74, P832). Independent vessel evidence: Paolo et al. 2024, 72–76% of industrial fishing missing from public AIS (P819).

**COMMERCIAL TOOL PRACTICES TO AVOID:** Catch pins, BiteScores, hotspot maps, fishing-forecast copy, sonar or FAD targeting, AIS as fish, CPUE-on-a-front as occurrence (INCOIS PFZ), unvalidated probability claims. MaxSea is a retired product name (2016); TIMEZERO continues. Maxar Intelligence is Vantor (Oct 2025).

**TELEMETRY ROLE:** Answers question 4 for tagged animals. Does not locate the untagged population. Requires a partnership and stays internal (S02, S84, S85). None of 25 movement methods is `DO_NOW`. Closest movement-adjacent step is Keys survey center-of-gravity after habitat joins.

**NOWCAST REQUIREMENTS:** A covariate that already beat survey-only on a locked later year; analyzed fields at issue time; independent observations after the freeze; skill versus climatology. FishAI meets none of the last three and not yet the first.

**FORECAST REQUIREMENTS:** Nowcast requirements plus archived forecasts and skill by lead versus climatology and persistence. Start the archive now: ESPC-D-V02 keeps only the last 8 forecast runs then scrubs them (P501); RTOFS is still on NOMADS HTTPS (observed 2026-09-26/27, P507) after OpenDAP retired 2026-02-23 (P506); CoastWatch ERDDAP RTOFS search returned HTTP 404 (P508). Do not issue forecasts.

**TOP FIVE RESEARCH PRIORITIES:**
1. More locked RVC detection models (`DO_NOW`).
2. Habitat rasters and spatial models on Keys (`DO_AFTER_ENVIRONMENTAL_JOINS`).
3. Archive ocean analyses and forecasts (`DO_AFTER_ENVIRONMENTAL_JOINS`).
4. Multi-year structured surveys with a fresh test year (`DO_AFTER_MORE_STRUCTURED_DATA`).
5. Sentinel observations and, later, internal telemetry (`REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA` / `REQUIRES_TELEMETRY`).

**FINAL RECOMMENDATION:** `FOCUS_ON_STRUCTURED_SURVEY_EXPANSION_FIRST`

A nowcast program is not supported by available evidence until an environmental term and contemporaneous labels exist. Telemetry and larval work are separate tracks, not the next product. Expanding honest survey-detection models on data FishAI already holds is the only path that can be accurate and later crowd-fed with complete checklists rather than pins.

## Files in this folder

See the companion matrices and protocols. This summary is the decision layer; the matrices are the evidence layer.
