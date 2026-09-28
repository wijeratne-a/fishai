# Wireframes (text / ASCII)

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/wireframes.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Spec mocks. Fixture geography. **Not** a harvest map. **Not** a live forecast.

Commercial email/PDF wireframes stay in `../artifacts/product_and_monetization/wireframe_spec.md`. These frames are the **globe** chrome. Stack/prototype agents may implement a subset (M1+M8+M9).

---

## 1. Globe chrome (MVP desktop)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ FISHAI  ·  OCEAN LIFE GLOBE (RESEARCH / FIXTURE)                             │
│ NOT A LIVE ANIMAL MAP  ·  SYNTHETIC CELLS  ·  NO INGEST                      │
│ NOT FOOD-SAFETY  ·  NOT HARVEST AUTHORIZATION  ·  NOT NAVIGATION             │
├──────────────────────────────────────────────────────────────────────────────┤
│ AOI: Willapa Bay, WA (public water body)   Taxon context: M. gigas 836033    │
│ View: (•) Earth+bathy  ( ) Unknown map  ( ) Evidence focus                   │
│       [Subsurface] [Curtain] [Slice] [Seafloor] [Playback] [Compare]         │
│       [Food web] [Story]  ← all LATER, disabled                              │
│ Publish: COARSENED  ·  Depth: (•) Emersion  ( ) 0–10m  ( ) Unknown           │
├─────────────┬──────────────────────────────────────────────┬─────────────────┤
│ LAYERS      │                                              │ TIME READOUT    │
│ BASE        │           N                 land             │ Issued:         │
│ [x] Earth   │      ~~~~ bay ~~~~          [bathy]          │  2026-09-18     │
│ [x] Bathy*  │   ░░  ▒▒  ██  ▢▢                           │  23:00 UTC      │
│ [ ] DOH GA  │   ░░  ▒▒  ██  ▢▢     *not for navigation    │ Valid: 16:00 PDT │
│   context   │   W          E                               │  → +72h         │
│ DRIVERS     │                                              │ Inputs through: │
│ [x] Tide    │   ██  OSI Elevated (amber) fixture           │  NWS 21:00Z     │
│ [ ] Air Fcst│   ▒▒  MODEL/FORECAST env                     │ Last direct obs:│
│ [ ] Waves   │   ░░  REMOTE skin SST (not body T)           │  none on-lease  │
│ [ ] SST skin│   ▢▢  UNKNOWN / DATA_GAP hatch               │ Conf: LOW       │
│ ESTIMATE    │                                              │ Model: OSI72-   │
│ [x] OSI-72  │   click → evidence panel                     │  RULE-v0 fixture│
│     Cat D   │                                              │ Coverage: LOW   │
│ COVERAGE    │                                              │                 │
│ [x] Unknown │                                              │ [Export table]  │
│ [x] Obs dens│                                              │ [Print 1-pager] │
├─────────────┴──────────────────────────────────────────────┴─────────────────┤
│ Legend: solid=observed  dotted=inferred  dashed=forecast  hatch=unknown      │
│ OSI chips: Typical=gray  Elevated=amber  High=red-outline  Cannot=B/W        │
│ NEVER: red flood = oysters  ·  green = harvest OK  ·  AIS = animals          │
└──────────────────────────────────────────────────────────────────────────────┘
* Bathymetry: GEBCO-class context, not for navigation.
```

Mobile: stack layers under a drawer; **does-not-mean strip stays sticky**; map is 2D.

---

## 2. Evidence panel (Mode 8 / click)

```text
┌─ EVIDENCE EXPLORER  cell WILLAPA-PUBLIC-P  depth EMRSION+SFC ───────────────┐
│ THIS IS: FORECAST · Category D · ops-stress indicator (fixture ranks)       │
│ NOT: food-safety · harvest OK · % dead · abundance · live tracking          │
│ Evidence: FORECAST · Cat D · Tier 3 env only · Conf LOW · T2/T3 attempt     │
│ Publish: COARSENED public water · no lease corners                          │
│                                                                             │
│ WHY                                                                         │
│  Rule uses forecast air overlapping daytime emersion + wind/wave.           │
│  Inputs, not “caused by SST.” SST if shown = supporting skin T.             │
│                                                                             │
│ TRUST                                                                       │
│  Low: no on-lease sensors, no prospective skill, fixture comparison set.    │
│  Validation: none. NOT READY FOR OPERATIONAL USE.                           │
│                                                                             │
│ MISSING                                                                     │
│  On-lease T/DO · bag microclimate · ploidy · handling · HAB toxin (always)  │
│                                                                             │
│ OBSERVED / INFERRED / FORECAST                                              │
│  Tide: harmonic prediction (labeled)  Air/waves: FORECAST                   │
│  OSI rank: FORECAST (rule)  Oyster N: not estimated                         │
│                                                                             │
│  1 Current estimate     n/a abundance · OSI Elevated at issue (fixture)     │
│  2 Forecast estimate    upper tercile vs this zone, similar tides/season    │
│  3 Confidence           Low · FRESH:ok DENSITY:low LABEL:low                │
│  4 Last direct obs      none on-lease · station 3.2 km fixture              │
│  5 Obs count            0 mort protocol 14d · 1 regional tide source        │
│  6 Obs types            [ ]survey [ ]tag [ ]eDNA [ ]acoustic [ ]sonar       │
│                         [ ]camera [ ]catch [ ]citizen [x]sat/env proxy      │
│                         [x]tide [x]NWP forecast                             │
│  7 Env inputs           air T fcst · tide · wind/wave · water T UNKNOWN     │
│  8 Drivers              1 air×emersion×solar  2 wind/wave  3 water support  │
│  9 Comparable hist      yesterday Typical (fixture)                         │
│ 10 Model version        OSI72-RULE-2026-09-18-v0 · no ML                    │
│ 11 Validation           none prospective                                    │
│ 12 Limitations          not body T; not Vp; station offset; delayed mort.   │
│ 13 Sources / licenses   NWS · CO-OPS · WDOH context · licence UNKNOWN       │
│ 14 Freshness            NWS 21:00Z · tides as-of 18 Sep · DOH 22:10Z (B)    │
│ 15 Privacy              COARSENED · PRIVATE if partner KPI (none here)      │
│ 16 Reduce uncertainty   on-lease logger; emersion-timed air; 30s outcomes   │
│                                                                             │
│ OPTIONS (not commands)                                                      │
│  [ ] A shift labor off hottest emersion                                     │
│  [ ] B increase monitoring this daylight tide                               │
│  [ ] C inspect gear after wave/wind                                         │
│  [ ] D keep current plan                                                    │
│  Low conf + costly action: options shown as consider-only, not recommended. │
│                                                                             │
│ MODULE B (not this score)  WDOH growing-area / biotoxin viewer  [link]      │
│ Official status last-verified 22:10Z · if stale, do not harvest from this.  │
│                                                                             │
│ [Log outcome 30s]  [Report error]  [Open 14-field PDF]                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Unknown / data-gap map (Mode 9)

```text
┌─ UNKNOWN MAP  ·  observation support (not oyster counts) ───────────────────┐
│ Depth: [emersion] [0–1 m] [1–5 m] [>5 m] [bottom] [unassigned]              │
│ Time: last 72h hourly (fixture)                                             │
│                                                                             │
│     ▢▢▢▢▢▢▢▢▢▢▢  ▢ = no samples (DATA_GAP)                                 │
│     ▢▢░░▢▢▒▒▢▢▢  ░ = remote skin SST only                                  │
│     ▢▢░░██▒▒▢▢▢  ▒ = forecast env / OSI (not animals)                      │
│     ▢▢▢▢██▢▢▢▢▢  █ = named station (DIRECT/in situ)                        │
│                                                                             │
│ Station •  3.2 km from example zone (fixture distance)                      │
│ DOH outline: harvest geography, not biology                                 │
│                                                                             │
│ This prediction has LOW confidence because:                                 │
│  - no recent direct observations on-lease;                                  │
│  - no depth-specific bag temperature;                                       │
│  - no validated survey of mortality this window;                            │
│  - nearest in-situ 3.2 km.                                                  │
│                                                                             │
│ UNKNOWN is the result. Not a broken map. Not zero oysters.                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. W1 local oyster **stress** view (not a harvest map)

Purpose: later bind of M1+M8+M9 to the paused commercial wedge. **Same chrome**, different emphasis. Still fixture until rights + founder lock.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ FISHAI  ·  WILLAPA OPS-STRESS VIEW  ·  SAMPLE / FIXTURE / NO MODEL          │
│ Pacific oyster (M. gigas) · WA Willapa DOH growing areas (context only)     │
│ PRIVATE partner zone would appear only under ACL — this mock uses public    │
│ water-body cells.  NOT Totten.  NOT Vp Category 3 harvest-control demo.     │
│                                                                             │
│ ┌──────────┐ ┌──────────┐ ┌────────────────────┐                            │
│ │ ELEVATED │ │ CONF LOW │ │ NOT FOOD-SAFETY    │                            │
│ │ ops-str. │ │ no snsrs │ │ NOT HARVEST AUTH   │                            │
│ └──────────┘ └──────────┘ └────────────────────┘                            │
│                                                                             │
│ Map: coarsened cells of RELATIVE ops-stress tercile                         │
│      gray Typical · amber Elevated · red-outline High · hatch Cannot-issue  │
│      NO choropleth of farms. NO SST titled oysters. NO open/closed colors.  │
│                                                                             │
│ Tiny sketch (labeled):  tide/emersion vs forecast AIR                       │
│      “not oyster body temperature”                                          │
│                                                                             │
│ WHAT IT MEANS: upper tercile work-stress vs this zone, similar tides/season │
│ WHAT IT DOES NOT: legality, closures, toxins, % dead, weather-safety, nav   │
│ OPTIONS: labor timing · monitoring · gear inspect · no change               │
│ MODULE B: fortress.wa.gov/doh/oswpviewer  (wins if conflict)                │
│                                                                             │
│ If you came here to see whether you can harvest: STOP. Use WDOH, not this.  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Design-review fails for this frame:** green cells, merged OSI+DOH score, lease GPS, “safe to eat,” 19 °C SST kill law, Totten demo, mortality %.

---

## 5. Depth / emersion stub (panel, not Mode 3 globe)

```text
Hour →  0    6    12   18   24   48   72
Tide    ████░░░░████░░░░████     harmonic / observed
AirT    ·····FORECAST··········  dashed
WtrT    ░station░░UNKNOWN lease
OSI     ···FORECAST rank·······
Mort    □□□ no protocol count

Y: emersion (air) | water (station, not bed)
```

---

## 6. Out of wireframe scope (same as commercial + globe later)

- Global multi-taxon arcade  
- Species picker  
- Volumetric life cloud  
- Food-web mode  
- Story autoplay  
- Climate RCP slider  
- Public heatmaps of catch  
- Unconstrained chat  

If a designer asks where the pretty fish go: **they don’t.** NANOOS already has water maps. This chrome is **evidence + ignorance + a local ops-stress rank**.
