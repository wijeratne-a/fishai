# Competitive Landscape

**Date:** 2026-09-18  
**Rule:** Do **not** claim uniqueness because our marketing words differ. Free government portals and $80/year fishing apps already occupy “ocean intelligence” in users’ heads.

**Legend for `relevance`:** A = oyster 72h ops-risk WA · B = Chinook 24–48h encounter CA/OR · C = lobster next-trip CPUE GOM  
**Pricing:** public list or reputable secondary source; **n/p** = not published (contact sales).  
**Prediction capability:** what they actually ship, not brochure verbs.

This is a **working register**, not a claim that every vendor was interviewed.

---

## How to read this

Customers do not buy categories; they buy a **10-minute ritual**. For WA oyster growers that ritual is approximately:

> NANOOS NVS + phone weather + tide app + WDOH closure page + SoundToxins/listserv + tribal/crew knowledge.

Any FishAI brief must beat **that bundle**, not “the absence of a Bloomberg Terminal for oysters.”

---

## A. Public marine portals and ocean observing

### NANOOS NVS — Shellfish Growers

| Field | Content |
|---|---|
| Customer | Commercial shellfish growers, NERR partners, public |
| Use case | Near-real-time water temp, salinity, turbidity, chlorophyll, DO, conductivity for mariculture decisions |
| Data | NERR, UW ORCA, Ecology, Pacific Shellfish Institute sites (WA listed on product page); IOOS-funded |
| Public/private | Public portal |
| Prediction | **Nowcast / observed time series**, not a 72h lease-level ops-risk brief |
| Geo | PNW; WA sites include Hood Canal, Willapa, Padilla, etc. |
| Business model | Public good (NOAA IOOS → NANOOS) |
| Pricing | Free |
| Strengths | Already in grower bookmarks; map + stations; trusted |
| Weaknesses | Not lease-specific decision contract; not 72h ranked options; not outcome loop; user must synthesize |
| Data moat | Sustained IOOS + agency stations — we will not out-observe them in v0 |
| Workflow moat | **This is the current workflow** |
| Gaps | Forward 72h, uncertainty language, farm-private labels |
| Legal | Public; attribution. Not a harvest authority |
| Relevance | **A: primary substitute.** B/C: low |

### NERACOOS + related GOM buoys

| Field | Content |
|---|---|
| Customer | Mariners, scientists, lobster industry (indirect) |
| Use case | Real-time Gulf of Maine ocean/weather |
| Data | Buoys, models |
| Public/private | Public |
| Prediction | Observing + some model products; **not** vessel CPUE |
| Geo | Gulf of Maine / Northeast |
| Business model | IOOS RA public good |
| Pricing | Free |
| Strengths | Physical environment backbone for C |
| Weaknesses | No trip-level CPUE product |
| Moats | Observing network |
| Gaps | Permissioned haul logs |
| Legal | Public |
| Relevance | **C: high (input).** A/B: low |

### Copernicus Marine (CMEMS) / Mercator Ocean / EU Digital Twin Ocean

| Field | Content |
|---|---|
| Customer | Researchers, agencies, industry, public |
| Use case | Global/regional ocean physics & BGC, reanalysis, forecast, digital-twin scenarios |
| Data | Satellite, in situ, models (e.g. GLORYS); AI models (e.g. GLONET) in DTO work |
| Public/private | Free with account (Toolbox); DTO evolving |
| Prediction | Ocean state forecasts (temp, currents, etc.), not species CPUE |
| Geo | Global + European emphasis |
| Business model | EU public service; Mercator operates |
| Pricing | Free data access (account); no volume quota per their public API docs |
| Strengths | Authoritative physics; 72h env drivers |
| Weaknesses | Coastal WA leases and GOM trap-scale not solved; not a farm brief |
| Moats | Institutional |
| Gaps | Customer decision UX; private outcomes |
| Legal | License/attribution; commercial use generally allowed under CMEMS terms — **confirm in rights register** |
| Relevance | A/B/C: **input vendor**, not competitor for the brief |

### NOAA NWS marine / CO-OPS tides / nowCOAST / NDBC / CDIP

| Field | Content |
|---|---|
| Customer | Public, mariners, industry |
| Use case | Weather, marine forecast, tides, waves, observations |
| Data | Federal operational |
| Public/private | Public |
| Prediction | Weather/wave/tide — **not** biological encounter or farm mortality |
| Geo | US |
| Business model | Public |
| Pricing | Free |
| Strengths | Trust, freshness, legal weather-safety source |
| Weaknesses | FishAI **must not** compete as weather-safety or navigation |
| Moats | Mandate |
| Gaps | Species/lease decision |
| Legal | Public domain / USGov; FishAI must **not** present as official NWS |
| Relevance | A/B/C: **input + substitute for “should I go out”** (we refuse that job) |

### IOOS regional portals (SECOORA, CeNCOOS, PACIOOS, etc.)

Same pattern as NANOOS/NERACOOS: public nowcasts, not paid decision briefs. Relevance = inputs if geography expands. Not v0 competitors except as the **habit** of “I already have a portal.”

---

## B. Government dashboards — harvest, closures, seasons

### WA DOH Commercial Shellfish Map Viewer + Growing Area Closures + Vibrio tools

| Field | Content |
|---|---|
| Customer | Commercial harvesters/dealers, agencies |
| Use case | Growing-area **classification**, emergency closures, biotoxin, **Vp control plan** (WAC 246-282-006), harvest-time temperature **planning** via NVS maps |
| Data | Sanitary surveys, water quality, biotoxin, harvest sites, temp loggers hosted with industry/tribes |
| Public/private | Public official |
| Prediction | Regulatory status; temp **planning aid** that **does not replace** harvest-time measurements |
| Geo | Washington growing areas |
| Business model | Public health mandate |
| Pricing | Free |
| Strengths | **The** harvest-legal source; growers must use it |
| Weaknesses | Not 72h ops-stress; not gear/workability |
| Moats | Law |
| Gaps | Ops-risk vs food-safety is our claimed job — **easy to confuse**; this is the #1 product-risk competitor |
| Legal | Official; FishAI must link, not mimic authority |
| Relevance | **A: critical adjacent / confusion risk.** B/C: none |

### ODFW / CDFW / NMFS / PFMC ocean salmon regulations and reports

| Field | Content |
|---|---|
| Customer | Recreational and commercial salmon fishers, charters |
| Use case | Seasons, in-season closures, bag limits, fishing reports |
| Data | Management + some catch monitoring |
| Public/private | Public |
| Prediction | Management measures, not 48h encounter rank |
| Geo | CA/OR/WA ocean salmon |
| Business model | Public |
| Pricing | Free |
| Strengths | **Must-check** before any charter product; 2026 measures still include area closures and Chinook retention bans in subareas |
| Weaknesses | Not a conditions forecast |
| Moats | Law |
| Gaps | Relative encounter given **open** |
| Legal | FishAI must not give license/season advice except “check official” |
| Relevance | **B: hard substitute + season kill-switch.** A/C: none |

### Maine DMR landings + lobster rules

| Field | Content |
|---|---|
| Customer | Industry, public, managers |
| Use case | Landings/value by species/zone/month; trap limits; licensing |
| Data | Dealer landings (mandatory since 2004); harvester survey (sampled, confidentiality constraints) |
| Public/private | Aggregates public; confidential microdata |
| Prediction | None operational for next trip |
| Geo | Maine |
| Business model | Public |
| Pricing | Free tables/PDFs |
| Strengths | Official economics (e.g. 2025 prelim. ~78.8M lb, ~$461M lobster) |
| Weaknesses | Too coarse/lagged for next-trip CPUE; confidentiality |
| Moats | Statute |
| Gaps | Vessel effort-normalized real-time |
| Legal | Confidentiality of harvester data |
| Relevance | **C: context, not product.** |

### ACCSP / GARFO VTR / NMFS stock assessments / ASMFC lobster

Scientific and compliance reporting. Not a captain-facing next-trip brief. Relevance C: possible licensed/aggregated inputs after rights review. **Not** a UX competitor.

---

## C. HAB and shellfish monitoring tools

### SoundToxins (Washington Sea Grant / NWFSC heritage)

| Field | Content |
|---|---|
| Customer | WDOH, growers, tribes, volunteers |
| Use case | Phytoplankton / HAB early warning for Puget Sound; listserv; database for managers |
| Data | Partner microscopy counts |
| Public/private | Partnership network; manager-facing |
| Prediction | Early warning of HAB **species presence** to prioritize testing / harvest timing for **health and economic loss** |
| Geo | Puget Sound |
| Business model | Grant/public program (funding historically fragile vs ORHAB’s legislative surcharge) |
| Pricing | Free to participants |
| Strengths | Trusted; grower-embedded |
| Weaknesses | HAB/food-safety, not 72h physical ops-stress |
| Moats | Human sampling network |
| Gaps | Wave/heat/DO workability |
| Legal | Public-health adjacent |
| Relevance | **A: adjacent; do not compete; link.** If growers only want HAB, our wedge is wrong. |

### ORHAB + PNW HAB Forecasting Bulletin (NANOOS / NOAA partners)

| Field | Content |
|---|---|
| Customer | Coastal managers, tribes, industry |
| Use case | PNW HAB nowcast/forecast of initiation/transport for **seafood safety and fisheries management** |
| Data | IOOS winds/currents/satellite + shore sampling |
| Public/private | Public bulletin |
| Prediction | HAB conditions / transport — **not** farm gear stress |
| Geo | Pacific Northwest coast |
| Business model | Public / research-ops |
| Pricing | Free |
| Strengths | Interpreted bulletin format (close cousin to our **format**, different **claim**) |
| Weaknesses | Food-safety purpose |
| Moats | Sampling + expert analysts |
| Gaps | Lease ops-stress |
| Legal | Not a harvest order by itself; managers use it |
| Relevance | **A: format analog, claims conflict if we blur.** |

### NOAA NCCOS HAB forecasts / Algal Bloom Monitoring System

Regional HAB forecasts (some NOAA, some partners). Public health and coastal management. Pricing free. Relevance A: HAB confusion. Innovasea markets **aquaBloom** HAB prediction in a **finfish** stack — different species/buyer.

---

## D. Fishing forecast tools (heavy on wedge B)

### Fishbrain (Pro)

| Field | Content |
|---|---|
| Customer | Recreational anglers; some guides |
| Use case | Social catches, BiteTime forecast, regs, Garmin depth, waypoints |
| Data | Crowdsourced catches (marketing: tens of millions), maps from Garmin/C-MAP/Navionics partners |
| Public/private | Social-public catches; private waypoints |
| Prediction | BiteTime ML **species catch probability by time**; “spot prediction” from map structure |
| Geo | Global emphasis US/Canada inland + some salt |
| Business model | Freemium SaaS |
| Pricing | **Pro $12.99/mo or $79.99/yr** (public 2026 pages) |
| Strengths | Distribution, habit, cheap, regs module |
| Weaknesses | Crowdsource bias; not effort-normalized charter CPUE; spot culture vs our privacy default; not CA/OR Chinook-ops specific |
| Data moat | Social graph |
| Workflow moat | Phone app everyone has |
| Gaps | Safe claims contract; charter fill-rate; coarsened cells |
| Legal | Must still follow seasons; social spots can harm fisheries/privacy |
| Relevance | **B: primary commercial competitor.** A/C: none |

### FishTrack

| Field | Content |
|---|---|
| Customer | Offshore anglers/charters |
| Use case | Cloud-free SST, chlorophyll, currents, tides, marine weather, waypoints |
| Data | Satellite SST/chl, models, weather |
| Public/private | Subscription maps; user waypoints private |
| Prediction | **Conditions layers**, user interprets “bite zones”; 5–7 day marine weather |
| Geo | Global emphasis offshore |
| Business model | Subscription |
| Pricing | App Store: **Premium ~$14.99/mo or ~$95.99/yr** |
| Strengths | Actual ocean layers captains already buy |
| Weaknesses | Not a Chinook encounter **rank with uncertainty contract** |
| Moats | Imagery pipeline + brand |
| Gaps | Effort-normalized labels |
| Legal | Standard ToS |
| Relevance | **B: high.** C: some SST. A: low |

### RipCharts

| Field | Content |
|---|---|
| Customer | Serious ocean anglers |
| Use case | SST, chl, altimetry, currents, bathymetry overlays |
| Data | Satellite / oceanographic products |
| Public/private | Paid maps; private waypoints |
| Prediction | Imagery + some SST forecast products on premium |
| Geo | US coasts + international packages |
| Business model | Subscription |
| Pricing | **~$99/yr standard, ~$169/yr premium** (register page 2026) |
| Strengths | Dense overlays; offline |
| Weaknesses | Expert-interpreter UX; not species-effort model |
| Moats | Product catalog |
| Gaps | Claims contract; partner catch |
| Legal | ToS |
| Relevance | **B: high.** C: moderate. A: none |

### Hilton’s Realtime Navigator

| Field | Content |
|---|---|
| Customer | Offshore anglers |
| Use case | SST, chlorophyll, currents, altimetry, navigation app |
| Data | Satellite / ocean |
| Public/private | Paid |
| Prediction | Condition maps |
| Geo | Regional US + international |
| Business model | Subscription |
| Pricing | **$49.99/week, $74.99/month, $200/year** per region; +$30 extra region (public terms) |
| Strengths | Seasonal purchase; captains know it |
| Weaknesses | Same as RipCharts |
| Moats | Brand in sportfishing |
| Gaps | Safe relative-encounter product |
| Legal | ToS |
| Relevance | **B: high** |

### Terrafin

| Field | Content |
|---|---|
| Customer | Saltwater anglers |
| Use case | SST/chlorophyll charts |
| Data | Satellite |
| Public/private | Paid |
| Prediction | Charts, not CPUE |
| Geo | Includes Pacific |
| Business model | Subscription |
| Pricing | Often cited **~$120/yr** (secondary; confirm at purchase) |
| Strengths | Simple, known |
| Weaknesses | Layers not a brief |
| Relevance | **B: medium-high** |

### FishRadar and similar “AI fishing forecast” apps

| Field | Content |
|---|---|
| Customer | Recreational |
| Use case | Condition scoring from env data; alerts |
| Data | SST, bathymetry, currents, wind, waves, pressure (vendor claims) |
| Public/private | App |
| Prediction | Bite windows / scores |
| Geo | Broad |
| Business model | Freemium |
| Pricing | Example public compare page: **~$2.99–$7.99/mo** tiers (vendor marketing; verify) |
| Strengths | Cheap, push alerts |
| Weaknesses | Easy to overclaim; not charter-validated |
| Relevance | **B: crowded low-end.** Shows **price ceiling** risk |

### Fishidy / FishAngler / Anglr / Fathom

Social/logbook/maps. Same B crowding. Pricing typically freemium. No serious A/C overlap.

### Navionics / C-MAP / Garmin charts

| Field | Content |
|---|---|
| Customer | Boaters, anglers |
| Use case | **Navigation charts**, sonar, crowdsourced depths |
| Data | HO charts + community sonar |
| Public/private | Paid regions |
| Prediction | Auto-guidance routing (nav) |
| Geo | Global regional cartridges |
| Business model | Chart licenses |
| Pricing | Navionics+ regions commonly **~$130–$200**; Platinum+ higher (dealer MSRP sheets) |
| Strengths | On the plotter already |
| Weaknesses | Not species encounter; **we must not become nav** |
| Legal | SOLAS/nav liability culture |
| Relevance | **B: workflow adjacent (plotter).** A/C: nav only |

### PredictWind / Windy / SailFlow

Weather routing and visualization. PredictWind Pro often **up to ~$499/yr**. **Out of our claim class** (weather-safety). Relevance: substitute for “do I go” — we refuse that job on all wedges.

---

## E. Aquaculture management software (mostly finfish/shrimp)

### BlueTrace (evolved from OysterTracker)

| Field | Content |
|---|---|
| Customer | Shellfish farms → broader seafood inventory/traceability |
| Use case | Farm activities (flip, tumble, harvest), inventory; later tagging/traceability for distributors |
| Data | Farmer-entered ops |
| Public/private | Private customer data |
| Prediction | Inventory/planning, not 72h environmental stress forecast |
| Geo | US + AU early customers; now broader seafood |
| Business model | SaaS |
| Pricing | n/p (had **paying farms at 2018 launch**, 15 clients then) |
| Strengths | **Oyster-native workflow**; labor/activity tracking; growers already pay this class |
| Weaknesses | Not env forecast; company pivoted toward traceability |
| Data moat | Customer inventory |
| Workflow moat | Daily farm tasks |
| Gaps | 72h OSI; we should **integrate later**, not recreate inventory |
| Legal | Food traceability regs (FSMA 204 etc.) — their world, not ours |
| Relevance | **A: highest software adjacent.** Partner, not clone. |

### aquaManager

| Field | Content |
|---|---|
| Customer | Fish/shrimp farms |
| Use case | Production, costing, IoT, biomass |
| Prediction | Production planning / analytics |
| Geo | International |
| Pricing | Quote; Start-up/Business/Enterprise |
| Relevance | A: low (wrong species). Shows **enterprise aqua ACV**. |

### Innovasea Farm360 / Realfish Pro / aquaBloom

| Field | Content |
|---|---|
| Customer | Finfish/shrimp, some env monitoring |
| Use case | Farm management, sensors, HAB **for farmed fish** (vendor marketing) |
| Data | Farm + sensors + remote sensing (vendor claims) |
| Prediction | Production + some event alerts (cold/warm fronts, HAB) |
| Geo | Global commercial aqua |
| Pricing | n/p |
| Strengths | Full stack, hardware+software |
| Weaknesses | Not WA oyster leases; expensive motion |
| Relevance | A: **conceptual** (env alerts to change ops). Not a WA oyster brief. |

### Aquabyte / AKVA / Observe / XpertSea / eFishery

Computer vision, feeders, shrimp counts. Quote-based; third parties sometimes cite **$5k–$50k/yr**. Species: salmon/shrimp. **Relevance A/B/C: low** except as proof that aquaculture **does** pay software when ROI is biomass/lice/feed.

### Manolin

| Field | Content |
|---|---|
| Customer | Mostly salmon (Norway heritage); investors/health staff on free maps |
| Use case | Fish health, lice, **predictive disease models**, benchmarks |
| Data | Farm private + public regional |
| Prediction | Disease/outbreak risk scores (vendor-reported high accuracy on PD/ISA — treat as **vendor claim**, not our validation) |
| Geo | Strongest Norway |
| Pricing | Free public-data tier historically; paid essentials reported **from NOK 10,000/yr** (older press); Observer reports **from ~$995**; current Explorer/Aquanaut quote |
| Strengths | Closest **“risk score subscription”** analog in aqua |
| Weaknesses | Finfish disease, not oyster ops-stress; needs dense farm data |
| Relevance | **A: analog business model.** Wrong biology. |

---

## F. GIS platforms

### Esri ArcGIS (and Taylor Shellfish public case)

| Field | Content |
|---|---|
| Customer | Enterprises, agencies, large farms |
| Use case | Bed mapping, workforce, Survey123, drones, inventory GIS |
| Data | Whatever the customer loads + Esri living atlas / EMUs etc. |
| Prediction | Suitability analysis if the customer builds it |
| Geo | Global |
| Business model | Licenses + SaaS |
| Pricing | Enterprise (n/p in this register) |
| Strengths | Taylor-scale farms **already live here**; we will not displace GIS |
| Weaknesses | No turnkey 72h oyster OSI |
| Moats | Entrenched IT |
| Gaps | Decision brief + outcome loop |
| Relevance | **A: complement for large farms (API later).** B/C: plotter/GIS adjacent |

Google Earth Engine / planetary-scale raster: analyst tool, not a farm email. Input possible; not a competitor for v0 UX.

---

## G. Vessel tracking and fishing-effort platforms

### Global Fishing Watch

| Field | Content |
|---|---|
| Customer | Public, NGOs, governments, researchers |
| Use case | Apparent fishing effort, encounters, transparency |
| Data | AIS + some VMS; ML “apparent fishing”; **not raw commercial AIS resale** |
| Public/private | Public map; APIs **CC BY-NC 4.0 / noncommercial** |
| Prediction | Apparent **effort**, not CPUE or abundance |
| Geo | Global, AIS-biased (lobster small boats poorly represented) |
| Business model | Nonprofit; commercial API **no public price** — contact for custom mission-aligned license |
| Pricing | Map free; commercial license n/p / generally unavailable |
| Strengths | Effort visualization |
| Weaknesses | **Must not be used as lobster abundance**; AIS coverage of ME lobster fleet is a known gap; NC license blocks naive commercial use |
| Legal | **NONCOMMERCIAL API**; HUMAN LEGAL REVIEW before any product use |
| Relevance | **C: dangerous false friend.** B: charter boats ≠ GFW fishing hours. A: none |

### MarineTraffic / Kpler (AIS) / Spire / historical exactEarth

| Field | Content |
|---|---|
| Customer | Maritime, logistics, some fisheries analytics |
| Use case | Vessel positions |
| Data | AIS |
| Public/private | Freemium map + paid AIS |
| Prediction | None biological |
| Pricing | n/p enterprise |
| Legal | Paid licenses; still **not CPUE** |
| Relevance | C/B: effort confounder if misused. **Do not.** |

---

## H. Fisheries compliance / e-logs

### Vericatch FisheriesApp / ELOG

| Field | Content |
|---|---|
| Customer | Canadian harvesters (DFO-qualified lobster and many fisheries) |
| Use case | Electronic logbooks, catch/effort, some CPUE viz |
| Data | Harvester-entered statutory |
| Prediction | None / descriptive analytics |
| Geo | Canada |
| Pricing | Public **~$60–$65/yr** reporting tiers |
| Strengths | Proof e-logs can be cheap if **mandated** |
| Weaknesses | Compliance ≠ forecast; US ME lobster not DFO |
| Relevance | **C: analog for logbook UX**, not a GOM forecast competitor |

Olrac, eCatch, NMFS eVTR: compliance. Partner-integration later, not v0.

---

## I. Seafood market intelligence

### Urner Barry (now inside Expana)

| Field | Content |
|---|---|
| Customer | Processors, distributors, foodservice |
| Use case | Protein/seafood **prices**, indices, news, forecasts of **markets** |
| Data | Analyst quotations + trade |
| Prediction | Price/supply market, not biology |
| Geo | US-centric protein, global trade |
| Pricing | Enterprise n/p |
| Strengths | What buyers actually pay for |
| Weaknesses | Not lease ops or CPUE |
| Relevance | Buyer program later; **not oyster v0** |

IntraFish, SeafoodSource, Undercurrent: media. Not products.

---

## J. Insurance / climate-risk analytics

Parametric aquaculture (e.g. AXA Climate-type heat/typhoon covers in some markets), Munich Re/Esri climate-risk GIS, Descartes-style underwriting. **n/p** pricing. Relevance: **possible future buyer of verified farm outcomes** — not an MVP competitor. Do not claim insurance partnerships.

---

## K. Environmental data vendors / “ocean weather”

### Sofar Ocean

| Field | Content |
|---|---|
| Customer | Navy, shipping, offshore, some weather-sensitive industry |
| Use case | Spotter-informed wave/wind/current forecasts |
| Data | Proprietary drifters + models |
| Prediction | Marine weather skill claims (vendor: up to 50% better close-range — **vendor claim**) |
| Geo | Global |
| Pricing | n/p (hardware + API) |
| Strengths | Wave/weather skill |
| Weaknesses | Not species/lease biology; we must not become weather-safety |
| Legal | Commercial licenses |
| Relevance | Possible **licensed wave input** for A/C; not the product |

Other vendors: Ocean Numerics, StormGeo, Orbia/planet-scale APIs, Intertrust (ex-Planet OS) data lakes. Inputs or enterprise clutter. Not a 60-second farm brief.

---

## L. Science / NGO “forecasts” that occupy mindshare

### GMRI lobster seasonal-timing forecast (Mills et al. lineage)

| Field | Content |
|---|---|
| Customer | Industry, public, managers |
| Use case | **When** ME landings shift into high-volume summer (phenology), updated in spring |
| Data | NERACOOS 50 m temps + historical landings |
| Prediction | Timing of landings rate change — **not next-trip CPUE** |
| Geo | Maine |
| Pricing | Public research product |
| Strengths | Trusted, actually used after 2012 glut |
| Weaknesses | Seasonal, not trip |
| Relevance | **C: occupying “lobster forecast” words.** Different decision. Respect and differentiate. |

Academic CPUE GAMs (NOAA/DMR papers): methods, not products.

---

## M. Relevance matrix (selected)

| Alternative | A oyster | B Chinook | C lobster |
|---|---|---|---|
| NANOOS NVS | **Substitute** | — | — |
| WDOH map/Vp | **Confusion / firewall** | — | — |
| SoundToxins / PNW HAB | Adjacent HAB | — | — |
| Fishbrain / FishTrack / RipCharts / Hilton | — | **Substitute** | SST only |
| ODFW/CDFW reports & seasons | — | **Gate** | — |
| BlueTrace / farm GIS | Complement | — | — |
| Manolin / Innovasea / aquaERP | Analog $ | — | — |
| GFW / AIS vendors | — | Misuse risk | **False friend** |
| NERACOOS / GMRI phenology | — | — | Input / different job |
| Vericatch | — | — | Logbook analog |
| Sofar / NWS | Weather input; refuse safety job | Same | Same |
| Expana/Urner Barry | Later buyer | — | Later buyer |

---

## N. What is **not** a moat for FishAI

- Saying “AI”
- Saying “terminal”
- Combining public datasets a grower can already open in three tabs
- A prettier map than NANOOS
- AIS
- Crowdsourced spots (anti-moat: leaks, bias, hostility)

## O. What could become a moat **if** gates pass

- Permissioned **lease/trip outcomes** linked to as-of env
- Trust from a **claims contract** that never burns the user on food-safety or catch-guarantee
- Habit: the 16:30 email is how the crew list gets made
- Later: integration into BlueTrace/Esri, not replacement

## P. Honest gap statement

There is **no** well-known paid product that emails a WA oyster farm a **72h operational (non-food-safety) stress brief** with uncertainty and a 30-second outcome form.

There **is** a well-known **free** stack that gets growers 80% of the way there. Commercial success is beating the last 20% on **specificity, synthesis, and loop** — or failing the 30-day interviews.

For Chinook, the gap is smaller than it looks: condition maps and social forecasts are sold for **<$200/yr**, and seasons may be closed.

For lobster, next-trip CPUE for a vessel is **not** a consumer app market; it is a **data-rights and trust** market. GMRI already owns phenology.

---

## Q. Sources used (public)

- nvs.nanoos.org/ShellfishGrowers  
- doh.wa.gov shellfish / Vibrio / temperature-data pages  
- fortress.wa.gov DOH viewers  
- soundtoxins.org  
- coastalscience.noaa.gov HAB forecasts  
- marine.copernicus.eu / Mercator DTO pages  
- fishbrain.com/pro · FishTrack App Store listing · ripcharts.com/register · realtime-navigator.com/terms  
- globalfishingwatch.org API license / commercial FAQ  
- vericatch.com  
- pcsga.org/shellfish-economics · WA legislative shellfish fee assessment (2025)  
- maine.gov/dmr landings news (2025 prelim.)  
- SeafoodSource / Aquaculture North America on OysterTracker · blue-trace.com about  
- esri.com Taylor Shellfish case  
- manolinaqua.com · fishfarmingexpert Manolin pricing anecdote  
- GMRI/Mills lobster forecast paper (Frontiers 2017)  
- ODFW 2026 ocean salmon season news · CDFW ocean salmon pages · Federal Register 2026 salmon measures  

Rights and exact license classes: **DATA_RIGHTS_AND_PRIVACY_AGENT** owns the register. This file records **commercial** alternatives, not a license approval.
