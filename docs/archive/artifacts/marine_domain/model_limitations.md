# Model limitations — three candidate wedges

**Agent:** MARINE_DOMAIN_AGENT  
**Date:** 2026-09-18  
**Access date for cited URLs:** 2026-09-18  
**Wedge status:** UNRESOLVED.

This document is the scientific “do not claim” list. It is not a product requirements document.

---

## Global prohibitions (all candidates)

1. **Do not treat SST, AIS, or chlorophyll as abundance.** They may be habitat, effort, or food-web **proxies**. Using them as fish/shellfish counts is a category error (target class E).
2. **Do not emit precise locations of protected species** (ESA Chinook ESUs, North Atlantic right whales, other listed marine mammals/turtles). Stock-mix and entanglement are **management constraints**, not map layers.
3. **Do not ingest datasets in this artifact.** URLs are citations. No pipelines, no scraped catch, no AIS stores.
4. **Do not confuse legal authorization with biology.** Harvest closures (NSSP, biotoxin, PFMC in-season, lobster size/v-notch) change what operators may do; they are not measurements of animals in the water.
5. **Catch ≠ abundance.** Especially trap and troll CPUE (Category C).
6. **Horizon mismatch is a silent failure mode.** Annual assessments and juvenile surveys are not 24–72 h operator truth.

---

## Candidate 1 — Pacific oyster, WA, 24–72 h farm stress

### What a model can honestly do

Rank **relative stress/disruption risk** on a **named lease type** (intertidal bag vs subtidal vs bottom) using tide + forecast air temperature + local water temperature/DO/salinity **if those in situ series exist**, plus a storm/wave flag.

### Structural limits

| Limit | Why it cannot be wished away |
|-------|------------------------------|
| **Microclimate** | Bag color, mud temperature, shade, elevation in centimeters, and emersion hour dominate aerial heat. A 1-km SST pixel is the wrong grain. |
| **Culture metadata** | Same estuary, opposite outcomes for triploid vs diploid, seed vs market, crowded vs thinned. Without operator inputs, residual error stays large. |
| **Multi-stressor mortality** | Cheney et al. 2000 and WDFW 2019: heat + neap + hypoxia + food/HAB. Single-variable “heat maps” will false-alarm and miss-kill. |
| **Delayed death** | 2021 heatwave: some oysters died **days to weeks later**. A 72 h window can miss the labeled mortality even when the causal event was inside the window. |
| **OsHV-1** | Documented CA farm killer; **not detected** at OR/WA sentinel sites in 2020 (Dumbauld et al. 2023 *DAO*). Do not import Mediterranean/Australian herpes timing into Willapa. |
| **OA / pH** | First-order for **larvae**, weak for 72 h adult farm mortality. Featuring Ω_aragonite as the adult-farm headline repeats the 2009 hatchery story on the wrong stage. |
| **Food-safety overlap** | SoundToxins, HAB forecasts, and *Vibrio* warnings will be scraped by a naive system. **PSP closure ≠ oyster dying.** Keep them out of the stress target. |
| **No public mortality panel** | There is no ASMFC-like farm-mortality index. Skill cannot be claimed from NANOOS temperature alone. |
| **Spatial non-transfer** | Willapa (well-mixed, ocean-influenced) ≠ Hood Canal (stratified, hypoxia) ≠ South Sound. A WA-wide model without basin ID is misspecified. |

### Predictability at 24–72 h

- **High:** coincidence of extreme air temperature with daytime low tide for intertidal culture (2021 analogue).
- **Medium:** storms/gear; freshwater pulses after named rain (if discharge/salinity observed).
- **Low without local sensors:** hypoxia, HAB feeding stress, disease.
- **Not a prediction:** harvest open/closed, larval set, “oyster abundance.”

### Evaluation pitfalls

- Scoring against DOH growing-area status (wrong label).
- Scoring against satellite SST (wrong exposure).
- Pooling Olympia and Pacific oysters (2021: different mortality).
- Using hatchery larval survival as farm-adult truth.

---

## Candidate 2 — Chinook, CA/OR charter, 24–48 h encounter

### What a model can honestly do

In an **open** management area, emit a **relative encounter-risk** (Category D) vs recent port CPUE, driven by (i) whether fishing is allowed, (ii) whether weather allows fishing, (iii) whether thermal/depth habitat is in a historically fishable configuration. Evaluate later with **effort-normalized catch** (Category C). Never promise fish.

### Structural limits

| Limit | Why |
|-------|-----|
| **Patchiness** | Juvenile and adult literature: many zero hauls, high variance-to-mean (e.g. Pool/Bi WA–OR surveys). Adults are not a smooth chl field. |
| **Vertical refuge** | Hinke et al.: fish keep 8–12°C by going **deeper** when SST warms. Surface-only “hotspot” maps can point captains to empty surface water. |
| **Stock mixture** | One “Chinook” CPUE mixes hatchery Central Valley fall fish with ESA-listed and constrained stocks. Improving catch of the mixture is not a conservation-neutral act. **No ESU-resolved maps.** |
| **Stage mismatch** | JSOES, Newport Line stoplight, and chlorophyll–juvenile models answer **cohort survival**, not tomorrow’s legal bite off Monterey or Newport. |
| **Regulation is first-order** | 2023–2024 CA ocean sport closure; 2026 harvest guidelines and in-season closures (CDFW/NOAA). Habitat scores in closed water are not encounters. |
| **Effort confounding** | Good weather raises trips and can dilute or inflate CPUE. AIS of other boats is **effort/crowding**, not biomass. |
| **Skill and information** | Captain knowledge dominates small samples. A model that “beats” public CRFS half-month means may still lose to a competent local. |
| **Prey unobserved** | Adult Chinook track forage. Public 48 h forage-fish fields of known quality generally do not exist. |
| **River-mouth concentration** | Biologically real for returning fish; **often illegal** (CDFW special closures). Modeling it is a protected-stock and compliance risk. |

### Predictability at 24–48 h

- **High:** closed vs open; small-craft warning (zero encounter because no trip).
- **Medium:** relative thermal-habitat availability (with depth caveat); swell/wind effects on catchability.
- **Low:** rank-order of specific waypoints; CPUE magnitude; stock identity of the next fish.
- **Not a prediction:** abundance, catch guarantee, ESA locations, juvenile indices as adult counts.

### Evaluation pitfalls

- Training on commercial troll CPUE to predict charter CPUE (different spatial distribution; NOAA CWT analyses).
- Training on WA/OR June juvenile catch to predict CA August adults.
- Treating chlorophyll or SST as the label.
- Ignoring bag limits and “limit early, go home” truncation of CPUE.

---

## Candidate 3 — American lobster, GOM statistical area, next-trip CPUE

### What a model can honestly do

Inside **one** statistical area or zone, rank **expected legal CPUE** among a few depth/ground classes for the next haul window, using **bottom temperature**, season/molt prior, weather, and operator effort metadata. Label it **catch**, not abundance.

### Structural limits

| Limit | Why |
|-------|-----|
| **Catchability ≠ density** | Activity, feeding, and molt are temperature-cued. McLeese & Wilder (1958) and decades of trap studies: warmer → more trap encounters. A “hot CPUE” forecast can be a **temperature-catchability** forecast. ASMFC 2025 builds this into survey models; a product that forgets it will be scientifically false. |
| **SST ≠ bottom T** | 2025 peer review: satellite SST is routine; **bottom** temperature is the data gap. FVCOM interpolations were too coarse for some assessment needs. eMOLT-type sensors are the relevant covariate source **when lawfully available** — not ingested here. |
| **Survey grain ≠ trip grain** | VTS is summer, 276 sites, 3-day soaks. NEFSC trawl is seasonal and offshore-biased for coastal lobster. Settlement is annual YOY. None is next-trip truth. |
| **Legal vs all lobster** | Vents, gauges, v-notch, eggers: landings CPUE ignores most animals the VTS was designed to see. |
| **Gear competition** | Trap saturation and neighbor traps. Unobserved without fleet density. |
| **Bait and soak** | First-order CPUE; if not in the feature set, they are residual “skill” that is actually husbandry. |
| **Spatial divergence** | DMR 2024: eastern vs western Maine sublegal trends differ. A GOM-wide next-trip model is the wrong geography. |
| **Recruitment lag** | *Calanus* and settlement explain **future** legal abundance (years), not tonight’s haul — except as a slow prior. |
| **Protected whales** | Take-reduction rules change gear. Predicting whale locations is disallowed. |

### Predictability at next-trip horizon

- **High:** weather go/no-go; seasonal molt window as a **prior** (Mills et al. 2017 is a **season-start** forecast, skill in weeks, not hours).
- **Medium:** relative CPUE across depths given a bottom-T field of known quality; storm effects.
- **Low:** absolute pounds per trap; abundance; moon-phase effects (weak published support).
- **Not a prediction:** stock status, SNE hypoxia imported to GOM, chlorophyll as lobsters.

### Evaluation pitfalls

- Calibrating to dealer landings without trap-hauls (landings ≠ CPUE ≠ abundance).
- Using NEFSC trawl as inshore next-trip label.
- Using VTS sublegal CPUE as legal landings.
- Crediting SST for bottom-T mechanisms.

---

## Confounders that look like “AI features”

| Tempting layer | Actual quantity | Harm if mislabeled |
|----------------|-----------------|--------------------|
| SST | Skin temperature | False abundance; missed deep Chinook / missed intertidal **air** heat |
| Chlorophyll | Phytoplankton pigment | False salmon/lobster/oyster counts; sometimes a real **food** or **juvenile habitat** proxy |
| AIS | Vessel presence | False fish; privacy and crowding |
| Growing-area class | Fecal coliform legality | False oyster health |
| Upwelling index | Wind-driven physics | Real habitat driver, still not a fish count |
| Stock-assessment biomass | Annual, stock-wide | Wrong horizon and grain |
| Social media bite reports | Biased effort | Overfit to weekends and influencers |

---

## Resolution limits (all three)

Even with perfect lawful data, **useful resolution** is:

- **C1:** lease or sub-basin + culture method + 24–72 h. Not pixel-level “this bag.”
- **C2:** PFMC recreational area or port + 24–48 h **relative** encounter. Not a waypoint and not a fish count.
- **C3:** statistical area or zone + depth band + next trip **CPUE**. Not a single trap, not animals per km².

Anything finer is, with present public science, **Category E**.
