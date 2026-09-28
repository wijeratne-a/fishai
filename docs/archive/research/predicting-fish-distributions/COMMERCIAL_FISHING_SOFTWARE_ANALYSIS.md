# Commercial fishing software analysis

**Checked:** 2026-09-27 from public documentation, peer-reviewed DOM/acoustic papers, and prior FishAI sources. Vendor pages are claims (`evidence_class=WEAK`), not ecological skill. No fishing recommendations. Matrix: `COMMERCIAL_TOOL_CAPABILITY_MATRIX.csv` (40 tools). Sources: `SOURCE_INDEX.csv` P700–P899.

## What commercial tools actually know

They know bathymetry, navigation hazards, sea-surface temperature and colour, vessel positions, and what users chose to log as catches. They do not know where untagged fish are. Sonar is backscatter under one hull. A catch pin is a presence without effort. A front on an SST chart is a gradient, not a school.

## Why fishing success is not ecological validation

Fleets and anglers sample where they already expect fish (preferential sampling; S67, S80). Catchability changes with gear, skipper, and price. Five-star app reviews do not beat a locked later-year Brier score against a survey. Confidential logbooks cannot be a public FishAI layer (MSA 402(b)). INCOIS PFZ paired-boat tests raise CPUE on SST–chlorophyll features; that is catchability, not occurrence (P789–P791).

---

## Adaptable insights

1. **Name the layer.** SST, depth, AIS, and acoustic backscatter are not fish. EcoCast, GFW, and the better ocean-condition sites already separate environment or vessels from biology.
2. **Timestamps are the product.** Welch et al. 2019 (acquisition → prediction → dissemination → automation; P837) and SBT POAMA tests only make sense if issue time and valid time are stored. Cloud-free SST composites without a window are not nowcasts.
3. **Uncertainty belongs on the map.** WhaleWatch published occurrence, density, and error. Crowd bathymetry and satellite colour have coverage holes; hiding them manufactures false precision.
4. **Acoustics need an observation model.** Lopez et al. 2016 and RFMO buoy-abundance papers show manufacturer “tonnes” are not Sv. A relative, standardised index can inform question 3 internally. A FAD position or a 3D fish-finder target must not become a public layer.
5. **Independent later data, then incentives.** TurtleWatch still marked a loggerhead SST band years later, but Siders et al. (P846) found fishers did not avoid it. Skill and behaviour change are different tests.

## Practices to avoid

- Catch pins, BiteScores, “spot predictions,” and analyst X-marks as occurrence or nowcast.
- AIS speed-banding or GFW apparent fishing as animal location. Paolo et al. 2024: 72–76% of industrial fishing vessels are missing from public AIS (P819).
- FAD buoy maps, vendor biomass, and consumer sonar species/size modes as truth.
- Equating CPUE on a front (INCOIS PFZ, vendor fishing forecasts) with ecological abundance.
- Publishing wreck-scale bathymetry or real-time habitat for targeted taxa.

---

## Navigational tools

**Garmin ActiveCaptain, TIMEZERO TZ Professional, ECDIS/ENC.** Inputs: charts, GPS, radar, AIS, optional weather/SST overlays. Output: safe navigation. Uncertainty: none ecological. Useful: timestamps on overlays (issue time). Do not adopt: fishing modules or AIS fishing-mode colours as biomass (P722).

**MaxSea:** product name retired in 2016; the company continues as TIMEZERO (P718, P721, P723). Do not treat MaxSea as a vanished vendor or as a live product name.

## Bathymetric chart tools

**Navionics SonarChart, C-MAP Genesis / Genesis Live, Garmin Quickdraw, GEBCO.** Inputs: official charts plus crowd sonar depths, or compiled public grids. Output: finer contours. Evidence: depths are measurements; fish are not. Crowd bathy cannot enter an ENC (P702, P703). **BioBase/Lowrance (P743):** independent river test for depth and vegetation, not fish. Useful: bathymetry as a habitat covariate with quality flags (`data/raw/habitat/` is empty today). Do not adopt: “fishing contour” marketing or wreck-scale public layers.

## Onboard sonar

**Simrad imaging, Furuno DFF3D/WASSP, FAD echosounder buoys (Satlink, Marine Instruments, Zunibal).** Inputs: active acoustics. Output: water-column backscatter, sometimes a vendor “biomass” or species label. Independent evidence exists for using FAD acoustics as a *research* relative-abundance index after converting vendor scales to Sv (P802–P809), not as a public targeting grid. **Kato:** present in 2016–2018 WCPFC datasets (P811); no current consumer page confirmed 2026-09-27. Do not adopt: real-time species targeting or FAD-level public maps.

## Crowd-sourced catch-report tools

**Fishbrain and similar.** Inputs: user catches and locations. Output: social hotspots and BiteGuide activity scores (P751). Zeros and effort are missing (P754–P756, P891). Do not adopt: pins, bite layers, site rankings. The eBird analogue is a *complete checklist*, not this (S80).

## Satellite ocean-condition tools

**SatFish, Terrafin, Hilton, FishTrack.** Inputs: SST, chlorophyll, sometimes altimetry. Output: ocean maps sold as fishing intelligence. No independent Brier versus Reef Visual Census was found this pass. Useful: the same fields as covariate *hypotheses* (Keys already showed SST/depth-T often fail). Do not adopt: “where the fish are” labels. Cloud-free composites without a stated window are not nowcasts.

**Forecast Ocean Plus (Japan):** JAMSTEC-linked ocean forecast consulting (P775–P777). Ocean state, not species. **OceanPlus Ltd (UK):** weather routing, not a fishing map (P778). Do not conflate the names.

## Dynamic habitat / fishing-forecast products

**ROFFS and paid forecast services.** Inputs: ocean analyses plus expert or proprietary rules. Output: client charts and analyst dots. NASA Spinoff and testimonials are not locked tests (P786). Do not adopt: paid hotspot forecasts.

**INCOIS PFZ.** Independent CPUE tests exist. They measure catchability on fronts, not occurrence.

**CLS CATSAT.** Ocean + micronekton + AIS for tuna fleets. Vendor fishing-intelligence claims; not a survey likelihood.

## Vessel intelligence

**Global Fishing Watch** (Kroodsma et al. 2018; Paolo et al. 2024). AIS/SAR show vessels and inferred fishing hours. That is effort, a bias covariate, never fish location. Licence is CC BY-NC (P823, P898). **Vantor Maritime Sentry** (Maxar Intelligence rebranded October 2025; P829): ships, not fish. Do not adopt: hunting boats or using AIS as animals.

## Scientific conservation decision-support

**EcoCast (S74, P832):** observer + tag models + daily satellite ocean; dynamic closures 2–10× smaller than a static box in the paper. Still served on CoastWatch 2026-09-27. California drift-gillnet context is changing (Seary 2024; P840). **WhaleWatch (P847) and WhaleWatch 2.0 (P849):** habitat/density with uncertainty. **TurtleWatch:** SST band still associated with interactions; unused by fishers (P846). **CSIRO/AFMA SBT habitat (P854–P858):** nowcast and seasonal skill versus ocean analyses, for a named management question. Useful: separate species models, daily ocean, validation, not claiming pins. Do not invert conservation maps into harvest maps.

---

## Independent evidence for fishing forecasts

Peer-reviewed **skill** exists for scientific DOM habitat products, not for recreational fishing-forecast vendors.

- **Found, independent:** EcoCast; WhaleWatch; SBT nowcasts/forecasts; TurtleWatch SST association (avoidance failed); INCOIS PFZ CPUE; FAD echosounder BAI after scientific reprocessing; BioBase depth/vegetation; Kroodsma 2018 and Paolo 2024 for **vessels**.
- **Vendor-only or none found:** ROFFS, SatFish, Terrafin, Hilton, FishTrack, Fishbrain BiteGuide/spot AI, CATSAT fishing-intelligence claims, plotter fish-ID modes, FAD manufacturer tonnage.

## Components FishAI can adapt

- Bathymetry and (offshore) SST/fronts as *testable* covariates, locked later-year tests.
- Issue time and valid time on every ocean field (weather-forecast discipline).
- EcoCast-style: one question, one observation process, forward validation, coarsened public grids.
- GFW-style effort as a sampling-bias layer if citizen checklists ever exist — never as abundance.
- Acoustic-index discipline (Sv, not vendor tonnes) for an internal question-3 research track only.

## Practices FishAI must not adopt

- Catch pins, bite heatmaps, “fishing forecast” copy.
- Fine grids of aggregations, wrecks, FADs.
- Sonar or AIS as fish.
- Unvalidated probability language.
- Anything that answers “where should I fish?”
