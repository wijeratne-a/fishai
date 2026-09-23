# Physical limits — Global Saltwater Life Observatory

**Agents:** PHYSICS_AND_FEASIBILITY_RED_TEAM_AGENT (lead), with MODEL_VALIDATION_AND_UNCERTAINTY_AGENT + SCIENTIFIC_PEER_REVIEW_RED_TEAM_AGENT  
**Date:** 2026-09-18  
**Access date for cited URLs:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/physics_feasibility_reports/`  
**Status:** Pre-instrument, pre-ingest physics audit. No observatory sensors have been deployed by this project. No models trained.  
**Wedge lock (FishAI parent):** UNRESOLVED. This file audits the **product class** “global saltwater life observatory / track everything,” not a founder-locked species × geography.

**Binding rule:** Physics is not a hyperparameter. A claim that violates a hard stop below is `PHYSICALLY_UNLIKELY` or `PHYSICALLY_IMPOSSIBLE` regardless of model fit, marketing language, or fused-layer aesthetics.

Sibling FishAI artifacts (read, not overwritten): `artifacts/scientific_red_team/**`, `artifacts/quality_and_validation/**`, `artifacts/marine_domain/model_limitations.md`, `artifacts/geospatial_data_engineer/canonical_data_model.md`, `artifacts/data_rights_and_privacy/privacy_and_sensitive_location_policy.md`.

Companion observatory files: `../validation_protocol.md`, `../scientific_red_team_reports/observatory_red_team_01.md`, `../artifacts/validation_redteam/agent_handoff.md`, `../observation_modality_catalog.md` (modality DIRECT/IMPOSSIBLE classes — this file supplies quantitative hard stops; do not treat catalog optimism as a physics waiver), `../global_species_registry/support_tier_framework.md` (T6 operational grade).

---

## 0. Verdict

| Question | Answer |
|---|---|
| Can a satellite constellation, public AIS, ocean-color, and SST stack **see most fish**? | **No.** Ocean-color and thermal sensors observe a **skin layer** (first optical depth, typically meters to tens of meters in clear water; ~1 m or less in turbid coastal water). They do not image fish. |
| Can one acoustic frequency give **global range and species-level resolution**? | **No.** Absorption, spreading, and wavelength set an irreducible range–resolution–classification tradeoff. |
| Can eDNA, tags, DAS, or bioluminescence close the remaining gap into a **continuous census**? | **No.** Each modality answers a **different physical question** with its own latency, grain, and false-positive structure. Fusion does not promote Category D habitat into Category A counts (`artifacts/scientific_red_team/prediction_contract.md`). |
| Honest observatory product class | Sparse, modality-tagged **observations** + relative habitat/risk (Category D / support **T2**) + effort-normalized catch where partners exist (Category C). **T3–T6 assigned count = 0.** **Not** “track everything.” |
| Hardware in FishAI v0 | **Out of scope** until a locked wedge fails with public + partner logs (`artifacts/product_and_monetization/product_thesis.md`). This file exists so later hardware proposals cannot be sold as a census. |

---

## 1. What “seeing life in salt water” actually is

Salt water is an attenuating, scattering, moving, fouling medium. Every observatory layer is a **sampler of a physical field**, not a camera pointed at animals.

| Physical field | What a sensor can couple to | What it cannot couple to |
|---|---|---|
| Solar / IR radiance | Water-leaving radiance from ~first optical depth; sea-surface skin temperature | Animals below the optical skin; species ID; abundance |
| Acoustic pressure | Impedance contrast (swimbladder, tissue, bubbles, seafloor, ships) along a beam or a cable | Silent animals; animals outside the beam; species without a scattering model + ground truth |
| Dissolved nucleic acids | Shed DNA/RNA fragments in a water parcel | Live GPS of the shedder; biomass without shedding/decay/transport model |
| Radio (Argos/GPS) | Tags **at the sea surface** in view of a satellite | Submerged tracks except via archive/pop-up; untagged majority |
| Fiber strain (DAS) | Axial strain along a cable, often from **low-frequency sound** that couples into the seafloor/cable | Individual fish target strength; most of the water column away from the cable |
| Photons from organisms | Rare, bright, persistent surface glow (e.g. bacterial milky seas) or stimulated flashes in a chamber | Taxon maps from space; fish schools as a default signal |
| Electromagnetic RF | Almost nothing useful at Wi-Fi/cellular frequencies in seawater | A global RF mesh of fish tags |

**Category error this project will not make:** stacking Tier 3 rasters (SST, chlorophyll, currents, vessel density) until a heatmap *looks* biological. Sibling red team already falsifies that product class (`artifacts/scientific_red_team/scientific_red_team_report.md` RT-XCUT-04).

---

## 2. Optical attenuation — why satellites do not see most fish

### 2.1 Physics

Downwelling irradiance in the water column decays approximately as \(E(z) \approx E(0)\,e^{-K_d z}\). Ocean-color satellites invert **water-leaving radiance**. Gordon & McCluney (1975) showed that ~90% of that radiance originates in the **first optical depth** \(z_{pd} \approx 1/K_d\) (equivalently \(z_{eu}/4.6\) if \(z_{eu}\) is the 1% PAR depth). That is the layer of interest for satellite remote sensing (Organelli et al. 2017, *JGR Oceans*; first optical depth stated as the satellite-relevant layer).

Order-of-magnitude \(K_d(490)\) (not FishAI measurements; literature):

| Water class | Typical \(K_d(490)\) | First optical depth \(1/K_d\) | Euphotic depth ~4.6/\(K_d\) |
|---|---|---|---|
| Clear subtropical gyre | ~0.02–0.05 m⁻¹ | ~20–50 m | ~90–230 m |
| Much of the open ocean | \(\le 0.1\) m⁻¹ (~95.7% of global ocean in Shi & Wang 2010 MODIS analysis) | \(\gtrsim 10\) m | \(\gtrsim 46\) m |
| Modestly turbid | 0.1–0.3 m⁻¹ | ~3–10 m | ~15–46 m |
| Coastal / estuarine turbid | often \(>0.3\) m⁻¹; Chesapeake-class ~1 m⁻¹; Amazon plume mean ~5 m⁻¹ (Shi & Wang 2010) | **~0.2–3 m** | **~1–15 m** |

Willapa Bay, Puget Sound, Columbia plume, and inshore Gulf of Maine are **Case-2** waters: CDOM, sediment, and phytoplankton all raise \(K_d\). A 1 km SST or ocean-color pixel is already the wrong grain for a lease or a trap string (`artifacts/marine_domain/model_limitations.md`).

**SST** is a **skin** (IR) or near-surface (microwave) temperature. It is not intertidal oyster body temperature (Raymond et al. 2022: 2021 Salish Sea mortality was aerial heat + midday emersion). It is not Gulf of Maine **bottom** temperature (ASMFC 2025 peer review; Zhang et al. 2025). It is not the 8–12 °C adult Chinook volume, which fish occupy by going **deeper** when the surface warms (Hinke et al. 2005).

### 2.2 What satellites *can* do (honest)

- Map **habitat covariates**: SST, fronts, ocean color (chlorophyll pigment, not prey species), Kd, ice, SSH, winds.
- Detect **rare surface optical events**: some near-surface schooling in very clear, calm, high-contrast conditions; bacterial milky seas in VIIRS DNB (Miller et al. 2021 — ~0.742 km pixels, 500–900 nm bandpass, **not taxon ID**).
- Drive 24–72 h **physics** (heat, waves, currents) that matter to farms and catchability.

### 2.3 Hard stop

**PHYSICALLY_IMPOSSIBLE:** “Satellite observes most fish, most of the time, in three dimensions.”  
**PHYSICALLY_UNLIKELY:** Optical satellite as a global fish-presence layer, especially in turbid coastal product waters.  
**Allowed:** SST/chl as **Tier 3 covariates** with `geometry_precision` no finer than the native pixel and a vertical validity of “skin / first optical depth only.”

**VHR exception (does not lift PX-01):** Cubaynes/Fretwell-class work can **remotely detect** some large whales, haulouts, or penguin stains under VHR (~0.3–2 m), low sea state, and heavy analyst/CNN labor (`observation_modality_catalog.md`). That is **not** a census of finfish, not Sentinel/VIIRS ocean-color, and not T6. Individual ≠ population. Listed-taxon pixels follow `sensitive_location_policy.md` (`NEVER_PUBLISH` at native grain).

Lidar (ICESat-2, CALIOP, airborne) can reach deeper than passive color in **clear** water and can return subsurface optical structure. It still does not provide a species census, does not work through clouds the same way, and does not solve Case-2 estuaries. Do not market lidar as the missing fish camera.

---

## 3. Acoustics — frequency vs range vs resolution vs identity

### 3.1 The tradeoff (not optional)

Sound speed in seawater \(c \approx 1480\)–\(1520\) m s⁻¹. Wavelength \(\lambda = c/f\).

| Frequency | \(\lambda\) (at 1500 m s⁻¹) | Typical fisheries use | Absorption physics |
|---|---|---|---|
| 10–100 Hz | 15–150 m | Basin-scale, some baleen whales | Low absorption; no fish-body resolution |
| ~1–10 kHz | 0.15–1.5 m | Some marine mammals, fish choruses, long-range telemetry | Modest absorption; species ID from *sound*, not TS |
| **38 kHz** | **~4 cm** | Standard swimbladdered-fish biomass surveys | MgSO₄ relaxation dominates 12–500 kHz (Francois & Garrison 1982a,b; Macaulay, Chu & Ona 2020 JASA) |
| **120 kHz** | **~1.25 cm** | Smaller fish, some zooplankton, better vertical resolution | Higher \(\alpha\) → shorter useful range |
| **200 kHz** | **~0.75 cm** | Near-range, higher resolution, plankton/fish mix | Still higher \(\alpha\) |
| ~333 kHz | ~0.45 cm | Broadband classification; **formulas can be wrong** | Macaulay et al. 2020: measured \(\alpha\) **~15 dB km⁻¹ above** Francois–Garrison; variability **±2 dB km⁻¹** |

Absorption \(\alpha(f,T,S,p,\mathrm{pH})\) rises steeply with frequency (boric acid \(\lesssim 10\) kHz; magnesium salts in the fisheries band; pure water \(\gtrsim 1\) MHz). Two-way transmission loss includes \(2\alpha R\) **plus** spherical spreading. That is why a high-frequency sounder that can resolve a 5 cm fish cannot survey a basin, and a low-frequency sounder that can hear across a fjord cannot count those fish.

**Range resolution** of a pulsed echosounder is set by bandwidth / pulse length (\(\Delta R \approx c\tau/2\) or \(c/(2B)\)), **not** by absorption. Absorption sets **SNR vs range**, hence **detectable range**. Conflating the two is a classification error.

### 3.2 What calibrated fisheries acoustics can (and cannot) claim

ICES-style biomass acoustics can support **Category B** (survey-derived index) **inside a documented transect design**, with:

- sphere calibration,
- \(\alpha\) appropriate to the water mass (Doonan et al. 2003: at 38 kHz over ~1800 m two-way paths, switching absorption equations changed orange-roughy-class biomass by **17% lower vs Francois–Garrison** or **45% higher vs Fisher–Simmons**),
- target-strength model for the **species and length distribution actually present**,
- dead-zone, bubble, and seafloor exclusion rules,
- species mixing rules (multifrequency or biological sampling).

It cannot, from a single frequency heatmap, claim:

- global coverage (ships/gliders/buoys are sparse),
- species ID without a scattering model + biological samples,
- abundance of non-swimbladdered or near-bottom fish in the acoustic dead zone,
- 24–48 h cell-level encounter for Chinook from an opportunistic sounder of unknown calibration.

**Vessel-mounted sounder ≠ stock assessment.** An uncalibrated “AI fish-finder” fused into the observatory is Category E.

### 3.3 Hard stop

**PHYSICALLY_IMPOSSIBLE:** One acoustic frequency, one uncalibrated network, global species-resolved abundance.  
**PHYSICALLY_UNLIKELY:** Opportunistic DAS or hull sounders as a drop-in replacement for ICES/NOAA acoustic surveys.  
**Allowed:** Calibrated, designed surveys as **attributed Category B** in the surveyed unit; hull acoustics as **effort-context or research**, never as a public abundance map.

---

## 4. eDNA — decay, transport, and the GPS illusion

### 4.1 Physics / chemistry

Environmental DNA is a **dissolved/particulate tracer**, not an animal. A detection is: *this assay found this marker in this water bottle at this time*, after PCR/library prep biases.

**Decay (order of magnitude, marine fish, literature — not a FishAI constant):**

- Sassoubre et al. 2016 (*Environ. Sci. Technol.*): first-order decay \(k \approx 0.055\)–\(0.101\) h⁻¹ for Pacific sardine / mackerel / anchovy mesocosms → **half-lives ~7–13 h**.
- Collins et al. 2018 (*Commun. Biol.*): persistence **varies locally** (inshore decay ~1.6× faster than offshore in that study); salinity and microbial regime matter.
- Holman et al. 2021 (as reviewed by Jo et al. / Pastor Rollan line): substantial metabarcoding loss within **~48 h** for several marine taxa.
- Bay of Biscay Lagrangian study (Pastor Rollan et al., Archimer 2024/2025): modeled persistence **~5–30 h**; transport **0.3–39 km** depending on location, month, decay, and depth.

**Transport:** eDNA moves with the parcel. Andruszkiewicz et al. 2019 modeled O(10 km) in a few days. Murakami et al. 2019 reported empirical detections only tens of meters from a source. **The literature disagrees on spatial grain because hydrodynamics dominate.** A point sample is not a point animal.

**Shedding** varies with biomass, behavior, reproduction, stress, and tissue type. Copy number ≠ abundance without a calibrated production–decay–dilution model that almost no operational product has.

### 4.2 Hard stop

**PHYSICALLY_IMPOSSIBLE:** A bottle at a pier is a live GPS fix for a named fish.  
**PHYSICALLY_UNLIKELY:** Quantitative biomass maps from metabarcoding read counts at observatory scale.  
**Allowed:** Occupancy / relative community composition with **explicit transport kernel**, assay metadata, and `UNKNOWN` in unsampled cells. Category D at best for presence; **not** Category A.

Cross-contamination, inhibition, primer bias, and reference-database gaps are **lab physics** as binding as decay. A molecular ecologist will reject any pipeline that does not publish: marker, reference build date, blank rate, LOD, and inhibition protocol (`observatory_red_team_01.md` §5).

---

## 5. Tags — duty cycle, pop-up latency, and the tagged minority

### 5.1 What a tag actually reports

| Tag class | When you get a location | Typical error / latency | Population fraction |
|---|---|---|---|
| Fastloc-GPS / GPS snapshot at surface | Animal **must surface** with antenna wet-time | Wildlife Computers: GPS snapshot errors often **tens of meters** (their published 20–75 m class; ~95% within 55 m in vendor material — **vendor, not independent census**) | Tiny; large/valuable/research animals |
| Argos Doppler (PTT) | Surface + satellite in view; ≥4 uplinks/pass for classic classes | Argos classes: 3 \(<250\) m, 2 250–500 m, 1 500–1500 m, 0 \(>1500\) m; **A/B: no accuracy estimate** (Wildlife Computers spreadsheet docs / Argos manual) | Tiny |
| PSAT / MiniPAT pop-up | Tag **releases on a programmed date** (or mortality/premature release), then floats and **transmits summaries** | **Hours to days of surface drift** before a usable Argos fix; emergence-location errors **O(10–50 km)** documented (Horning et al. 2019 *Anim. Biotelemetry*; Nielsen et al. 2024 crab PSAT paper). Light-based geolocation between pop-ups is **still worse** (often 0.5–2° class, species- and processing-dependent). Duty cycling **thins Argos messages** to save battery (MiniPAT user guide). | Tiny |
| Acoustic coded tags | Only when inside a **receiver** range (typically hundreds of m to a few km, site-dependent) | No location between receivers; array geometry is the map | Only where arrays exist (OTN, FACT, etc.) |
| Archival (no telemetry) | **After recapture** | Zero live observatory value until recapture | Fishery-dependent |

Duty cycle is a **battery conservation law**. Continuous 1 Hz GPS from a non-surfacing animal is not a product you can buy at ocean scale.

### 5.2 Hard stop

**PHYSICALLY_IMPOSSIBLE:** Tag-derived “real-time tracks of saltwater life.”  
**PHYSICALLY_UNLIKELY:** Pop-up tracks as 24–48 h charter encounter labels (latency + n).  
**Allowed:** Sparse, permissioned movement priors; stock-structure research; **never** a global layer; **never** publish precise locations of listed species (`privacy_and_sensitive_location_policy.md`).

---

## 6. DAS — meter-scale strain is not meter-scale biology

### 6.1 What DAS measures

An interrogator launches pulses into fiber and records Rayleigh backscatter phase. Each **channel** is a virtual strainmeter. **Gauge length** (commonly **~4–10 m** in published marine mammal work; sometimes 30–40 m) is the **spatial averaging window**. Channel spacing can be 1–4 m; **resolution is not the spacing**.

Published marine examples (accessed 2026-09-18):

- Svalbard cable: 4.08 m spacing, **8.16 m gauge**, 120 km, ~645 Hz sample, **~320 Hz bandwidth**, ~7 TB/day (Landrø / Bouffaut et al. 2022 *Sci. Rep.* and *Front. Mar. Sci.*). Detected **baleen whale** calls, ships, quakes — **low-frequency, loud, coupling into a buried cable**.
- Oregon SMART-style analysis: 30 m gauge, 2 m spacing, 200 Hz sample, cable buried ~1.5 m, useful to first repeater ~95 km (2025 *Front. Mar. Sci.*).
- PAM-of-fish DAS trial: 1.02 m spacing, 4.08 m gauge, 3125 Hz sample — **can** localize **some fish sounds** over tens of meters on a **bespoke** cable; authors still note hydrophones remain superior at **higher frequencies** (spatial filtering of long gauges).

SNR decays along the fiber (Svalbard: ~−40 dB at 100 km vs 1 km). Bandwidth **falls** as you ask for longer range. You cannot have 50 kHz fish-resolution acoustics on a 120 km dark fiber at the far end.

### 6.2 Biological mismatch

A 20–80 cm fish has a body scale **much smaller than an 8 m gauge**. DAS does **not** implement a fisheries echosounder (no calibrated TS, no 38 kHz beam). It hears **sounds that strain the cable**. Most fish are silent most of the time. Schooling, vessel noise, wind, and earthquakes will dominate.

**Data volume** (TB/day) is an operational hard stop for a global “listen to all cables” product without on-interrogator reduction. That reduction **is** a model, and it must be validated like any other detector.

### 6.3 Hard stop

**PHYSICALLY_IMPOSSIBLE:** DAS as a global, species-resolved fish census at biology’s spatial scale.  
**PHYSICALLY_UNLIKELY:** Species maps of silent or high-frequency animals from telecom-fiber DAS at 8–30 m gauge and \(\lesssim 300\) Hz bandwidth.  
**Allowed:** Research detection of **loud, low-frequency** vocalizers (some whales, some chorusing fish) along **instrumented** cables, with localization uncertainty of **hundreds of meters to kilometers** off-axis, **NEVER_PUBLISH** for listed marine mammals at fine grain.

---

## 7. Bioluminescence — glow is not a species layer

VIIRS Day/Night Band: ~**0.742 km** pixels, **500–900 nm**, noise floor allowing detection of extremely faint light (Miller et al. 2021 *Sci. Rep.*). Confirmed spaceborne detections are **persistent bacterial milky seas**, distinguished from dinoflagellate **flashes** (~0.1 s, mechanically stimulated) by **persistence across nights** and drift with currents.

In-water identification of bioluminescent taxa uses **flash-kinetics libraries** in bathyphotometers (UBAT-class), not satellite pixels (Johnsen et al. 2014 *Sci. Rep.* polar-night work; PeerJ 2024 dinoflagellate/zooplankton FFKPs). Even then, libraries are incomplete and stimulated flashes in a chamber are not unstimulated ocean glow.

**Hard stop:** Satellite bioluminescence ≠ fish, ≠ dinoflagellate species, ≠ HAB toxin, ≠ Chinook forage. **PHYSICALLY_UNLIKELY** as an observatory abundance layer. Allowed as a **rare-event research** flag with independent in-water confirmation.

---

## 8. Underwater communications — bandwidth × power × range

Seawater kills RF: attenuation of order **10² dB m⁻¹** at 2.4 GHz (survey figures in Kaushal & Kaddoum / optical-UWC reviews; treat as **order of magnitude**, not a design number). Cellular-style meshes of fish tags are **PHYSICALLY_UNLIKELY**.

| Channel | Honest envelope | Failure mode |
|---|---|---|
| Acoustic modem | WHOI Micromodem-class **~80–5400 bps** (packet types; throughput much lower after ACK/travel time). Low-power research modems: **~0.5–1 kbps** at **hundreds of m**; some spread-spectrum minis **~0.5 kbps over ~2 km** at \(<1\) W Tx (Sanchez et al. 2012 *Sensors*; WHOI Micromodem page; Morozs et al. 2022 *Electronics*). Sound speed **~1.5 km s⁻¹** ⇒ **high latency**. | Multipath, Doppler, marine-mammal exposure, battery |
| Optical wireless | **Mbps–Gbps** possible at **meters to ~10² m** in **clear** water with alignment | Turbidity (same \(K_d\) as §2), pointing, fouling of windows |
| Inductive / cabled | High bandwidth **on the cable** | Only where you paid for the cable |
| Surface gateway | RF/Iridium/Starlink **once you have a float** | Biofouling, vandalism, waves; not a subsurface mesh |

**Implication for the observatory:** You cannot stream calibrated 38 kHz EK80 water-column data from a global glider fleet in real time over acoustics. You store, subsample, and surface. **Latency is physical.** Any “live global biomass cube” implies either cables, surface relays, or a lie.

---

## 9. Biofouling and the maintenance wall

Optical windows, conductivity cells, DO membranes, eDNA filters, hydrophone faces, and solar panels **accrete life**. Unattended coastal sensors routinely degrade on **week-to-month** scales without wipers, copper, UV, or human servicing (IOOS/QARTOD operational reality; NANOOS ORCA and NERR SWMP QC flags exist **because** of this).

Fouling is not cosmetic:

- Chlorophyll fluorescence and radiance **drift high or low**.
- DO **under-reads** after biofilm oxygen demand.
- Acoustic transducers change **impedance and beam**.
- eDNA intake **clogs and contaminates**.

**Hard stop:** A “set and forget global in-situ layer” is **PHYSICALLY_UNLIKELY**. Coverage maps that ignore last-service date are scientifically false. Every in-situ observatory record needs `last_service_at` and a fouling flag or it is **not operational**.

---

## 10. PHYSICALLY_UNLIKELY / IMPOSSIBLE register

Use this table in product copy review. Status is physics, not roadmap optimism.

| ID | Claim | Verdict | Why |
|---|---|---|---|
| PX-01 | Satellites see most fish | **IMPOSSIBLE** | First optical depth; fish are not the water-leaving radiance source |
| PX-02 | SST/chl = presence or abundance | **UNLIKELY** (false as physics; already HIGH in scientific red team) | Wrong variable, wrong depth, pigment ≠ prey |
| PX-03 | One frequency, infinite range and cm resolution | **IMPOSSIBLE** | \(\alpha(f)\) and \(\lambda(f)\) |
| PX-04 | Uncalibrated acoustics = biomass | **UNLIKELY** | TS, \(\alpha\), mixing, dead zone |
| PX-05 | eDNA pin = live animal now | **IMPOSSIBLE** | Decay hours–days; transport meters–tens of km |
| PX-06 | eDNA reads = abundance | **UNLIKELY** at observatory scale | Shedding/dilution uncalibrated |
| PX-07 | Pop-up tags = real-time tracks | **IMPOSSIBLE** | Duty cycle + pop-up + Argos drift |
| PX-08 | Tags represent the stock | **UNLIKELY** | n, size/species bias, tagging effect |
| PX-09 | DAS gauge meters = fish-body maps | **IMPOSSIBLE** | Strain along cable ≠ TS of a fish; bandwidth/range |
| PX-10 | DAS hears all fish | **UNLIKELY** | Most fish silent; coupling; noise |
| PX-11 | VIIRS glow = species | **IMPOSSIBLE** | Broadband km pixels; bacterial milky seas ≠ fish |
| PX-12 | RF mesh of underwater tags | **IMPOSSIBLE** at Wi-Fi/cellular bands | Conductivity / skin depth |
| PX-13 | Live HD video from basin-scale acoustics | **UNLIKELY** | Modem bps vs video Mbps; latency |
| PX-14 | Unmaintained global in-situ truth | **UNLIKELY** | Biofouling |
| PX-15 | Fusion of PX-01…14 yields a census | **IMPOSSIBLE** | Independent biases; fusion does not add photons or SNR |
| PX-16 | AIS/VMS = fish | **IMPOSSIBLE** as physics **and** as policy | Vessels, not biomass (prompt non-negotiable) |
| PX-17 | 24–48 h adult Chinook waypoints from ocean color | **UNLIKELY** | Scale + vertical habitat (Shelton 2021; Hinke 2005) |
| PX-18 | Intertidal oyster mortality from SST skin | **UNLIKELY** | Aerial + solar + tide (Raymond 2022) |
| PX-19 | Lobster density from SST | **UNLIKELY** | Bottom T and catchability |
| PX-20 | Global observatory without unknown cells | **IMPOSSIBLE** | Sampling theorem: unsampled ocean is **UNKNOWN** |

---

## 11. What *is* physically allowed (so this file is not a nihilism engine)

These are physically identified, if rights, labels, and validation exist:

1. **Environmental nowcast/forecast** (waves, tides, air T, 3D T/S where models are skillful) — not biology.  
2. **Calibrated, designed acoustic surveys** — Category B inside the design.  
3. **Partner catch/effort** — Category C.  
4. **Farm sensors + tide + air** — Category D ops-stress for sessile cultured animals.  
5. **eDNA occupancy** after assay + hydrodynamics disclosure — community composition research.  
6. **Sparse tags** as movement hypotheses.  
7. **DAS** as a whale/chorus research array on instrumented cables.  
8. **Explicit UNKNOWN** for the rest of the saltwater volume (most of it).

That list is the observatory. “Track everything” is not on it.

---

## 12. Implications for FishAI wedges (if later locked)

| Wedge | Physical implication |
|---|---|
| W1 oyster 72 h ops | Do **not** wait for satellites or eDNA. Air × emersion × in situ T/DO/waves are the identified physics. SST-only is PX-18. |
| W2 Chinook 24–48 h | Satellites and eDNA cannot identify tomorrow’s adult bite. Acoustics from a charter hull are uncalibrated and effort-selected. **Habitat rank is the ceiling** (already RT-CHK-01). |
| W3 lobster next trip | Bottom temperature and soak/effort are physical; SST and AIS are not. Tags/DAS will not appear at trap-haul grain. |

---

## 13. Sources (accessed 2026-09-18)

Indicative; not a training corpus. Papers cited, not copied.

- Gordon & McCluney 1975, first optical depth.  
- Organelli et al. 2017 *JGR Oceans* https://hal.science/hal-03137011 — Kd in first optical depth from BGC-Argo.  
- Shi & Wang 2010 *JGR* https://doi.org/10.1029/2010jc006160 — global Kd(490) occupancy.  
- Francois & Garrison 1982a,b *JASA* — seawater absorption.  
- Doonan, Coombs & McClatchie 2003 *ICES JMS* https://doi.org/10.1016/s1054-3139(03)00120-6 — 38 kHz biomass vs \(\alpha\).  
- Macaulay, Chu & Ona 2020 *JASA* 148:100 https://doi.org/10.1121/10.0001498 — 38–360 kHz field \(\alpha\); +15 dB km⁻¹ near 333 kHz.  
- Sassoubre et al. 2016 *EST* — marine fish eDNA shedding/decay.  
- Collins et al. 2018 *Commun. Biol.* https://doi.org/10.1038/s42003-018-0192-6 — marine eDNA persistence.  
- Pastor Rollan et al. Lagrangian eDNA, Archimer https://archimer.ifremer.fr/doc/00959/107120/120265.pdf  
- Wildlife Computers MiniPAT user guide; Argos location-quality table.  
- Horning et al. 2019 *Anim. Biotelemetry* https://doi.org/10.1186/s40317-019-0166-6 — pop-up emergence error 10–50 km class.  
- Nielsen et al. 2024 *Anim. Biotelemetry* https://doi.org/10.1186/s40317-024-00360-7 — PSAT drift vs first Argos.  
- Bouffaut et al. 2022 *Front. Mar. Sci.* https://doi.org/10.3389/fmars.2022.901348 — DAS baleen whales, 8.16 m gauge, 120 km.  
- Landrø et al. 2022 *Sci. Rep.* https://doi.org/10.1038/s41598-022-23606-x  
- HAL PAM-of-fish DAS https://hal.science/hal-05293208v1/file/PAM%20of%20fish%20with%20DAS%20neutre.pdf  
- Miller et al. 2021 *Sci. Rep.* https://doi.org/10.1038/s41598-021-94823-z — VIIRS milky seas.  
- WHOI Micromodem https://acomms.whoi.edu/micro-modem — 80–5400 bps class.  
- Sanchez et al. 2012 *Sensors* https://doi.org/10.3390/s120606837 — 1 kbps, 240 m, ~120 mW Tx.  
- Raymond et al. 2022 *Ecology*; Hinke et al. 2005 *MEPS*; Shelton et al. 2021 *Fish and Fisheries* — already in marine-domain / scientific-red-team files.

**Residual physics confidence:** **High** on hard stops (first optical depth, \(\alpha(f)\), RF skin depth, pop-up latency). **Medium** on exact Kd/eDNA-km numbers in unnamed future cells — those must be measured, not copied from this memo. **This agent is not a substitute for an acoustician or optical oceanographer sign-off on a hardware design.**
