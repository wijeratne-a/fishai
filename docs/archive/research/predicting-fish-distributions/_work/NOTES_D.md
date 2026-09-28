# NOTES_D — commercial fishing software and DOM tools

**Pass date:** 2026-09-27  
**Files:** `COMMERCIAL_FISHING_SOFTWARE_ANALYSIS.md`, `COMMERCIAL_TOOL_CAPABILITY_MATRIX.csv`, `SOURCES_D.csv` (P700–P899).  
**Vendor pages:** `evidence_class=WEAK` whenever they are used for performance.

## Adaptable insights (five)

1. **Name the layer.** SST, depth, AIS, and acoustic backscatter are not fish. EcoCast, GFW, and the better ocean-condition sites already separate environment or vessels from biology. FishAI’s nine questions collapse if those layers share a label.
2. **Timestamps are the product.** Welch et al. 2019 (acquisition → prediction → dissemination → automation) and SBT POAMA tests only make sense if issue time and valid time are stored. Cloud-free SST composites without a window are not nowcasts.
3. **Uncertainty belongs on the map.** WhaleWatch published occurrence, density, and error. Crowd bathymetry and satellite colour have coverage holes; hiding them manufactures false precision.
4. **Acoustics need an observation model.** Lopez et al. 2016 and RFMO buoy-abundance papers show manufacturer “tonnes” are not Sv. A relative, standardised index can inform question 3 internally. A FAD position or a 3D fish-finder target must not become a public layer.
5. **Independent later data, then incentives.** TurtleWatch still marked a loggerhead SST band years later, but Siders et al. found fishers did not avoid it. A habitat map can be scientifically useful and operationally unused. Skill and behaviour change are different tests.

## Practices to avoid

- Catch pins, BiteScores, “spot predictions,” and analyst X-marks as occurrence or nowcast.
- AIS speed-banding or GFW apparent fishing as animal location.
- FAD buoy maps, vendor biomass, and consumer sonar species/size modes as truth.
- Equating CPUE on a front (INCOIS PFZ, vendor fishing forecasts) with ecological abundance.
- Publishing wreck-scale bathymetry or real-time habitat for targeted taxa.

## Independent evidence for fishing forecasts

Peer-reviewed **skill** exists for scientific DOM habitat products, not for recreational fishing-forecast vendors.

- **Found, independent:** EcoCast (Hazen et al. 2018) habitat/bycatch surfaces and smaller dynamic closures versus a static leatherback closure; WhaleWatch (Hazen et al. 2017) telemetry habitat scaled to density, with uncertainty; SBT nowcasts/forecasts (Hobday and Hartmann 2006; Hobday et al. 2010, 2011; Eveson et al. 2015) with reported seasonal skill versus ocean analyses; TurtleWatch SST band still associated with loggerhead interactions (Siders et al.), even though avoidance failed; INCOIS PFZ paired-boat or landing-centre CPUE tests (higher catch rates in SST–chlorophyll features — catchability, not occurrence); FAD echosounder BAI papers (Lopez, Santiago, Uranga, IATTC/IOTC/WCPFC) after scientific reprocessing, not vendor apps; BioBase/Lowrance river test (Bruneel et al. 2019) for depth and vegetation, not fish; Kroodsma 2018 and Paolo 2024 for **vessels**.
- **Vendor-only or none found:** ROFFS, SatFish, Terrafin, Hilton, FishTrack, Fishbrain BiteGuide/spot AI, CATSAT fishing-intelligence claims, plotter “Accu-Fish,” FAD manufacturer tonnage. NASA Spinoff and customer quotes are not locked tests.
- **FAD brand status:** Satlink, Marine Instruments, and Zunibal product pages were live. Kato appears in WCPFC 2016–2018 acoustic datasets (P811); no current consumer page was confirmed on 2026-09-27.

## Bottom line

Commercial fishing software is a sensor stack for boats: charts, depth along tracks, beams of sound, satellite skin temperature and colour, and other vessels. A few government and CSIRO tools add habitat probability with papers and uncertainty. Almost none of the paid “where the fish are” products publish an independent, baseline-beating test of ecological state. FishAI can reuse layer separation, issue times, uncertainty, and acoustic-index discipline. It must not reuse pins, bite scores, AIS-as-fish, FAD maps, or catch success as validation.
