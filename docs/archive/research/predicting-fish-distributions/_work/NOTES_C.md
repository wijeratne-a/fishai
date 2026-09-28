# NOTES_C — fish behavior variables, nowcast and forecast methods

Checked 2026-09-27. Research only. Source ids: S-ids from `research/global-life-tracking/RESEARCH_SOURCES.csv` plus P500–P576 in `SOURCES_C.csv`. Also reuse existing P009 (Muhling) in `SOURCE_INDEX.csv`.

## Best-evidenced variables by guild

- **Reef fish:** habitat structure (hard-bottom/rugosity, coral vs abiotic), survey depth, and visibility as detectability (S41; H_REEF_VIS_HARD). FishAI Keys bicolor damselfish used habitat+depth+vis and beat prevalence on 2022 (Brier 0.09537 vs 0.12475) but failed calibration (P548). Temperature at dive depth did not earn a place on CV.
- **Demersal fish:** bottom temperature, oxygen/metabolic index, substrate, and depth (Nye 2009 P540; Deutsch 2015 P537; J-SCOPE bottom O2 P528). SST is not an accepted bottom proxy.
- **Coastal pelagic fish:** SST, fronts, chl/upwelling (CUTI/BEUTI on the CCS only, P521), currents/SSH, season. Adult sardine–SST relationships broke in the 2014–2018 heatwave (validation AUC near 0.5; P524).
- **Oceanic pelagic fish:** occupied-depth T, oxygen/OMZ (Prince and Goodyear 2006: ETP hypoxic boundary often ~25 m; P541), fronts/SSH/EKE, season/diel. Operational SBT habitat uses T (and chl in nowcasts) (P530/P531).
- **Estuarine fish:** salinity, tides, discharge, hypoxia, seagrass/mangroves. Hourly, not daily SST.
- **Deep-sea fish:** depth, bottom T, oxygen/OMZ, substrate/seamounts. Surface SST/chl excluded as occupancy predictors (H-BEH-015).
- **Polar fish:** ice, bottom T, light/season, zooplankton; borealization literature (P557). SST ice-contaminated; not a bottom proxy.
- **Sharks and rays:** split the guild. Benthic batoids follow demersal rules; pelagic sharks follow oceanic rules plus telemetry for occupied depth (S02/S09). Nursery habitat is stage-specific and sensitive.
- **Eggs and larvae:** currents at larval depth, spawning time, MLD/stability, prey match-mismatch (S62/S63; P565). Eggs are not adults (S119).
- **Juveniles:** nursery habitat (seagrass, mangroves, structure), salinity, tides. Do not copy adult reef coefficients. No precise pins.
- **Spawning adults:** lunar/season/site fidelity often dominate SST (P564). Aggregation coordinates stay withheld.

## SST limits (do not assume SST is sufficient)

- FishAI Keys: HYCOM water_temp at dive depth dropped (CV Brier 0.08145 with T vs 0.08115 without) (P548).
- FishAI SBC kelp bass: kept T on CV then failed 2022 — predicted 0.379 vs observed 0.605; 2022 cooler (15.8 C vs 17.3 C training) while detections stayed high (P549).
- FishAI Puerto Rico MUR/OISST: untrusted (future-day leakage; holdout reuse) (P550).
- Muhling et al. 2020: correlative SDMs trained 2003–2013 had AUCs > 0.7 in-sample years then lost skill in 2014–2018; adult sardine near AUC 0.5 (P524).
- Surface as bottom proxy: acceptable only when mixed-layer depth exceeds occupied depth and that is verified. Default is no (H_SST_PROXY_CAUTION; P540).

## Oxygen

- Metabolic index Phi at equatorward edges ~2–5; projected ~20% global and ~50% northern high-latitude decline this century (P537).
- Habitat compression of tropical pelagics by a shallow hypoxic layer, often ~25 m in the ETP, not in the WNA (P541: 19 billfish/801 d vs 13/429 d).
- J-SCOPE: bottom oxygen among the more predictable seasonal fields, biased low; fall transition poorly predicted (P528). Hypoxia on the product page is O2 < 2 mg/l (P570).
- FishAI has no oxygen product.

## Habitat

- `data/raw/habitat/` is empty. Binding gap for Q1 (FISHAI_DATA_GAP_ANALYSIS).
- GEBCO/bathymetry is envelope, not reef presence (transferability warnings).
- Same-day SBC kelp is a survey covariate, not a forecast (P560).
- VIIRS chl over Keys reef is mostly masked/bottom-contaminated (P551; optically shallow <30 m guidance P518/P519).

## Forecast skill decay (verified fragments only)

- Persistence is the reference. In the J-SCOPE domain, Jan-initialized July SST: forecast r~0.4–0.6 vs persistence r~0.0–0.4 (P528).
- SBT habitat boundaries: skill to 3–4 month leads vs nowcasts (P530). Related GAB SST skill described as useful to ~2 months in project text (P531) — do not merge the two.
- NMME multimodel SST generally beats individuals (P533/P534); LIM often comparable at the coast (P535).
- WCOFS physics: day-1 current MAE cut 1–2 cm/s (15–40%); T skill held across 3 days (P510).
- J-SCOPE 2026 oxygen page: stated uncertainty ~10% early season, up to ~50% later (P570) — operational language, not a paper table.
- CMIP thermal habitat: many species agree, 116–120 strongly disagree; some west-coast shifts >1000 km under RCP 8.5 (P539).
- Biological skill cannot exceed physics skill and can collapse under novel conditions (P524; P573).

## Nowcast minimums (Q7)

1. An environmental (or habitat) term that already beat survey-only on a locked later year.
2. Analyzed fields available at issue time, matched to occupied depth, no future days.
3. Contemporaneous independent observations after the freeze.
4. Skill versus climatology (and persistence if used).
5. Calibration check, not AUC alone (P548; P575).

FishAI meets none of 2–4 and has not met 1 for temperature.

## Forecast minimums (Q8)

Everything in Q7, plus archived forecasts with issue and valid times, and skill by lead versus climatology and persistence. Stop at leads that lose. FishAI has no forecast archive (P576).

## Archive status (2026-09-27)

- **GOFS 3.1 GLBy:** hycom.org archive 2014-07 to **2024-09-04** (P500). FishAI preregistration used **2024-09-05**. Do not collapse those dates. 7-day forecast historically.
- **ESPC-D-V02 expt_03.1:** public from **2024-08-10**, 8-day forecast, last 8 runs retained then scrubbed; page flag `[missing data]` (P501). Operational Aug 2024 (P503).
- **RTOFS:** still on NOMADS HTTPS (`rtofs.20260926`, `rtofs.20260927`) (P507). OpenDAP on NOMADS retired **2026-02-23** (P506). CoastWatch ERDDAP RTOFS search **HTTP 404** this pass (P508). Ops described as v2.5 in PNS 26-17 (2026-03-12); v3.0 was a comment period (P505).
- **WCOFS:** operational; 24 h nowcast / 72 h forecast; live 2026-09-22 log (P509–P511). West Coast only. Not in FishAI.
- **UCSC CCS ROMS:** public THREDDS nowcast/hindcast ~10 km (P512). Not NWS ops. Not in FishAI.
- **GLORYS12 / CMEMS PHY:** account exists; not ingested. GLORYS is reanalysis (1993–near present on the viewer this pass, P513), not a forecast. PHY_001_024 is the 10-day NRT/forecast family (P514).
- **FishAI:** HYCOM boxes for Keys/SBC; MUR/OISST PR (untrusted); VIIRS chl unusable on reef; no issue-time forecast archive; no habitat rasters.
