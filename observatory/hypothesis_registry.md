# Hypothesis registry — Global Saltwater Life Observatory

**Agent:** HYPOTHETICAL_TECHNOLOGY_AGENT  
**Project:** Ocean Intelligence Builder / FishAI (working name)  
**Date:** 2026-09-18  
**Access date for cited URLs:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/`  
**Wedge status:** UNRESOLVED. These hypotheses are **research options**, not a product lock and not a claim that any method currently measures global abundance.

This registry evaluates **beyond standard SST / chlorophyll / AIS dashboards**. It does **not** treat those layers as animals. It does **not** claim that unproven methods work. NASA Technology Readiness Levels (TRL 1–9) follow [NASA SCaN TRL](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/) and [NASA ESTO TRL table](https://esto.nasa.gov/trl/). Where a peer-reviewed or operational program does not publish a TRL, the cell is **UNKNOWN** plus an agent estimate labeled **ESTIMATE (not a NASA rating)**.

Companion files:

- One experiment card per major hypothesis: `hypothesis_experiment_cards/`
- TRL / readiness matrix: `technology_readiness_matrix.csv`
- Return payload: `artifacts/hypotheses/agent_handoff.md`

---

## 0. Epistemic rules (non-negotiable)

1. **Presence ≠ abundance ≠ catch ≠ legal harvest.** eDNA, acoustics, CPUE, AIS, ocean color, and soundscape metrics are different quantities.
2. **Do not manufacture confidence in sparse cells.** Foundation models, digital twins, and interpolated maps must **abstain** where observation density is low (see FishAI `uncertainty_policy.md`).
3. **Do not publish exact private fishing locations, farm KPIs, Indigenous knowledge, or protected-species tracks.**
4. **Food-safety, navigation, and harvest authorization remain with authorities** (NSSP/DOH, PFMC/CDFW/ODFW, USCG/NWS).
5. **Costs are order-of-magnitude ESTIMATEs** in 2026 USD. They are not quotes.
6. **Kill criteria are pre-registered.** If a hypothesis fails them, stop; do not rebrand the same claim.

### Readiness vocabulary (assigned to the *stated* hypothesis, not to a weaker cousin)

| Label | Meaning |
|---|---|
| `IMPLEMENTABLE_NOW` | Existing instruments, software, and lawful data can run a bounded experiment this year if partners consent. |
| `REQUIRES_PARTNERSHIP` | Physics and kits exist; access, vessels, farms, cables, tissue, or licenses are the bottleneck. |
| `REQUIRES_NEW_SENSOR_DEPLOYMENT` | Principle demonstrated; a new spatial mesh, platform, or instrument class must be fielded before the claim is testable at the stated scale. |
| `REQUIRES_RESEARCH_BREAKTHROUGH` | A scientific or inversion gap blocks the claim (e.g. eDNA→N, sparse-cell life maps). |
| `SPECULATIVE_BUT_PHYSICALLY_PLAUSIBLE` | Consistent with known physics; evidence is thin or analogical. |
| `PHYSICALLY_UNLIKELY_OR_UNSUPPORTED` | Conflicts with attenuation, resolution, or published negative evidence. **Kill or rewrite.** |

---

## 1. Ranking method (uncertainty reduction per dollar and per year)

Score is **not** a model output. It is a documented heuristic so ranks can be attacked.

\[
S = \frac{U \times D \times V}{\log_{10}(C) \times T}\ (1-L)(1-E)(1-X)
\]

| Symbol | 0–1 or units | Definition |
|---|---|---|
| \(U\) | 0–1 | Expected reduction in **biological** uncertainty vs climatology / persistence / official survey, for a named quantity. |
| \(D\) | 0–1 | Relevance to a recurring operator or conservation decision (not a prettier map). |
| \(V\) | 0–1 | **Validatability**: independent ground truth exists or can be collected in ≤18 months. Unvalidatable claims get \(V \approx 0\) and \(X \to 1\). |
| \(C\) | USD ESTIMATE | Order-of-magnitude cost to first falsifying experiment (not global scale-up). Floor \(C=10^4\). |
| \(T\) | years | Time to first scored result. Floor 0.25 y. |
| \(L\) | 0–1 | Legal / privacy harm if the product leaked or was misused (location leakage, ESA, MSA confidentiality, competitor tracking). |
| \(E\) | 0–1 | Ecological harm of the **measurement** (tagging, take, acoustic disturbance, effort concentration on listed stocks). |
| \(X\) | 0–1 | Penalty for **unvalidatable or category-error claims** (SST-as-fish, eDNA-as-N, FM-filled empty cells). |

**Penalties applied before ranking:** any experiment whose honest claim is abundance from AIS, chlorophyll, or uncalibrated eDNA; any public heatmap of catch or listed-species locations; any “high confidence” in cells with no local labels. Those are scored only as **negative controls** and are not in the top 15.

Top 15 experiments and the return top 10 are in **§4**. Hypotheses to kill now and 2026 partner-implementable set are in **§5–6**.

---

## 2. Required coverage (4.1–4.13)

### H-4.1 Global ocean eDNA mesh

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.1-EDNA-MESH` |
| **statement** | A standardized global mesh of water-column (and selected sediment/air) biomolecular samples can estimate **occupancy and community composition** of saltwater taxa from microbes to vertebrates at ecologically useful grain, if and only if transport, shedding, and decay are modeled and **abundance is not assumed**. |
| **target organisms** | Broad: microbes, phytoplankton, invertebrates, fishes, marine mammals (marker-dependent: 12S, 16S, 18S, COI). Not a single-species abundance product. |
| **measurement mechanism** | Filter or autonomous sampler → extract → qPCR / metabarcoding / metagenomics. Optional in situ qPCR (ESP-class). |
| **physical principle** | Shed nucleic acids persist hours–days in seawater, advect with water, and decay with temperature, light, microbes, and particle state ([Sassoubre et al. 2016](https://doi.org/10.1021/acs.est.6b03114); [Scriver et al. 2023](https://doi.org/10.1002/edn3.405); [Andruszkiewicz Allan et al. 2025](https://doi.org/10.1002/edn3.70021)). |
| **required sensors/infrastructure** | Sterile filtration or autonomous ESP/FIDO/Oceanic-WHOI samplers; cold chain or ethanol/freeze preservation; sequencing lab or in situ qPCR; occupancy + hydrodynamic model; contamination QA. |
| **expected spatial/temporal resolution** | Point sample; inference volume **unknown** without local decay+transport (literature: ~0.3–39 km, persistence ~5–30 h in some models — **not universal**). Typical program grain: station × depth × week-to-season, not 1 km × hour. |
| **depth range** | Surface to mesopelagic with platform (CTD, AUV, mooring). Deep-sea under-sampled. |
| **geographic scalability** | Coastal and SOOP: high. Open-ocean seasonal: medium. True global equal-area mesh: low without Decade-scale funding. |
| **estimated cost** | ESTIMATE: \(10^4\)–\(10^5\) per coastal occupancy experiment; \(10^6\)–\(10^7\) for 10 autonomous nodes; **\(10^8\)–\(10^9\)** for a maintained global mesh. Sequencing is no longer the dominant cost; platforms, QA, and people are. |
| **data rights/privacy** | Sequence data may reveal listed species and aquaculture pathogens. Do not publish fine-scale detections of ESA/MMPA taxa. Nagoya/ABS and CARE for Indigenous waters. License OBIS/GBIF derivatives. |
| **ecological/safety** | Low extractive impact vs trawls. Contamination and false invasion alerts can trigger harmful responses. Fixative chemicals need hazmat handling. |
| **validation method** | Paired nets/optics/qPCR; occupancy models vs independent gear; **pre-register that copies/L is not N**. |
| **FP/FN risks** | FP: contamination, primer bias, downstream transport from distant source, dead/decaying tissue. FN: PCR inhibition, marker gaps, low shedding, filtration volume, decay. |
| **current evidence** | [OBON](https://obon-ocean.org/); [UNESCO Ocean Decade OBON](https://oceandecade.org/actions/ocean-biomolecular-observing-network-obon/); [MBARI ESP/FIDO + U.S. National Aquatic eDNA Strategy](https://www.mbari.org/news/mbaris-advanced-technology-transforms-the-monitoring-of-aquatic-ecosystems/); WHOI Oceanic sampler pilot; [eDNA ≠ biomass for *Carcinus*](https://doi.org/10.1186/s12862-022-01969-z). |
| **TRL** | Metabarcoding lab workflow: **TRL 8–9 ESTIMATE**. Autonomous in situ samplers: **TRL 6–7 ESTIMATE** (site-specific). Global operational mesh: **UNKNOWN**, agent **TRL 4–5 ESTIMATE**. Quantitative abundance inversion: **TRL 3–4 ESTIMATE**. |
| **potential impact** | High for **occupancy, invasive/pathogen/HAB genes, community change**. Low for 24–72 h operator abundance. |
| **next experiment** | `EXP-EDNA-PAIRED-01` (card). |
| **kill criteria** | (i) Product copy uses eDNA as abundance or “count of fish in the cell”; (ii) paired-gear occupancy AUC/TSS does not beat a seasonal climatology in a pre-registered coastal box after two seasons; (iii) contamination blanks fail repeatedly; (iv) listed-species detections cannot be coarsened. |
| **readiness** | **REQUIRES_NEW_SENSOR_DEPLOYMENT** at stated **global mesh** scale. Regional occupancy with partners: `REQUIRES_PARTNERSHIP`. Abundance-from-eDNA: `REQUIRES_RESEARCH_BREAKTHROUGH`. |

---

### H-4.2 Global vessel sonar cooperative (privacy-preserving edge features)

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.2-SONAR-COOP` |
| **statement** | Fishing and research vessels can contribute **on-board processed** water-column acoustic features (NASC/Sv, depth bins, time, coarsened location) to a cooperative observatory **without** sharing raw echograms or fishing spots, using edge processing, delay, aggregation, and (if needed) federated updates. |
| **target organisms** | Gas-bladder pelagics, krill, micronekton; **not** species ID from single-frequency fishery sounders without optical/biological ground truth. Siphonophores confound gas-bladder interpretations ([ICES WGFAST](https://doi.org/10.17895/ices.pub.7444)). |
| **measurement mechanism** | Calibrated echosounder (EK/ES60/80 class) → edge processing (Echopype / Krillscan-class) → compact features → delayed, coarsened upload. |
| **physical principle** | Volume backscatter at kHz frequencies from impedance contrast (swimbladders, oil, tissue). NASC is an acoustic integral, **not** biomass until TS and species mix are known. |
| **required sensors/infrastructure** | Calibrated sounder, clock/GPS, processing PC or appliance, satellite/cellular backhaul, cooperative agreement, ICES SONAR-netCDF4 / AcMeta metadata. |
| **expected spatial/temporal resolution** | Along-track ~pings to 1 nmi EDSU; public product **≥10 km / ≥24 h** (FishAI privacy grain). |
| **depth range** | Typically epipelagic–upper mesopelagic; hull-mounted blind zone and bottom exclusion. |
| **geographic scalability** | High where industrial pelagic fleets operate; poor for artisanal fleets and uncalibrated recreational sounders. |
| **estimated cost** | ESTIMATE: \(5\times10^4\)–\(2\times10^5\) to instrument and run **one** cooperative vessel-year (software + QC + incentive); \(10^6\)–\(10^7\) for a regional fleet program. |
| **data rights/privacy** | Raw echograms can reconstruct secret aggregations. Norwegian fishers share only with **trust, reciprocity, anonymity, delay, access control** ([Marine Policy 2025](https://doi.org/10.1016/j.marpol.2025.106620)). Federated learning exists for maritime/plankton images, **not** proven on fisheries acoustics ([FL maritime review](https://www.mdpi.com/2077-1312/12/6/1034); [Plankton-FL](https://arxiv.org/pdf/2212.08990)). |
| **ecological/safety** | Active acoustics at survey levels are standard; avoid adding military-grade sources. Do not concentrate effort on listed stocks via public NASC maps. |
| **validation method** | Edge NASC vs scientific-survey NASC on the same transect; species mix from nets/optics; calibration sphere checks. |
| **FP/FN risks** | FP: bubbles, bottom, siphonophores, uncalibrated gain. FN: vessel avoidance, blind zone, empty surface over deep fish. |
| **current evidence** | [ICES GAIN / WKGAIN](https://github.com/ices-eg/wk_WKGAIN); [Haris et al. 2021 processed acoustics](https://doi.org/10.1038/s41597-020-00785-8); [Krillscan](https://www.researchgate.net/publication/383813725_KRILLSCAN_An_automated_open-source_software_for_processing_and_analysis_of_echosounder_data_from_the_Antarctic_krill_fishery); [Echopype](https://echopype.readthedocs.io). |
| **TRL** | Scientific echosounders: **TRL 9**. Edge processed-product sharing: **TRL 6–7 ESTIMATE** (krill fishery / IMOS). Privacy-preserving **global** cooperative: **UNKNOWN**, **TRL 4–5 ESTIMATE**. |
| **potential impact** | High for **pelagic acoustic biomass indices** if calibration + species ID hold. Zero if sold as a public fish-finder. |
| **next experiment** | `EXP-SONAR-EDGE-01`. |
| **kill criteria** | (i) Public or partner-leaked maps recover sets within 500 m; (ii) uncalibrated sounders enter the index; (iii) NASC treated as species abundance; (iv) fishers withdraw after first season due to privacy failure. |
| **readiness** | **REQUIRES_PARTNERSHIP**. Public fish-finder variant: **PHYSICALLY_UNLIKELY_OR_UNSUPPORTED** as an abundance product (effort-biased) and **kill**. |

---

### H-4.3 Marine life foundation model (no manufactured confidence)

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.3-FOUNDATION` |
| **statement** | A multi-modal foundation model (images, acoustics, omics, environment, text) can transfer representations across marine taxa and sensors, improving **identification and few-shot classification** where labels exist — and must **emit Low / abstain** in sparse geographic cells rather than hallucinating occupancy. |
| **target organisms** | Any taxa with images or sequences; FathomNet/GBIF-heavy taxa will dominate. Deep pelagic and polar taxa remain long-tailed. |
| **measurement mechanism** | Self-supervised / contrastive pretraining (BioCLIP-2, MarineInst) + calibrated heads; **not** a species-distribution interpolator. |
| **physical principle** | None as a life sensor. It is a **statistical compressor of existing observations**. Sparse-cell predictions are prior-driven, not measurements. |
| **required sensors/infrastructure** | Curated labeled corpora with licenses; GPU; abstention/uncertainty layer; blocked spatial CV ([Roberts et al. spatial CV](https://doi.org/10.1111/ecog.03109) family). |
| **expected spatial/temporal resolution** | Whatever the **labels** have. Must not emit finer grain than labels. |
| **depth range** | Image models: photic/ROV/drop-cam depths in training. Not a 4000 m census. |
| **geographic scalability** | High for **ID tools**; low for **maps of unsampled ocean**. |
| **estimated cost** | ESTIMATE: \(10^5\)–\(10^6\) to evaluate open weights on a bounded task; \(10^6\)–\(10^7\) to train a marine-specific multi-modal model with rights-cleared data. |
| **data rights/privacy** | FathomNet/GBIF/EOL licenses vary; do not train on private catch GPS, tribal TEK, or listed-species holding sites. Open weights can leak training locations if GPS is in captions. |
| **ecological/safety** | Indirect: high-confidence empty-cell maps can misallocate conservation or fishing effort. |
| **validation method** | Image/taxon accuracy on held-out FathomNet; **geographic block**; calibration (ECE); **explicit sparse-cell abstention test** (confidence must fall). |
| **FP/FN risks** | FP: visually similar taxa, background water as “empty” vs unobserved. FN: rare morphs, poor lighting, long tail. **Catastrophic:** fluent maps of unsampled basins. |
| **current evidence** | [MarineInst ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/00223.pdf); [BioCLIP 2 / TreeOfLife-200M](https://imageomics.github.io/bioclip-2/); [NicheFlow SDM preprint (reptiles, not marine)](https://doi.org/10.1101/2024.10.15.618541). NicheFlow few-shot AUC is **not** evidence for marine abundance maps. |
| **TRL** | Marine **vision ID**: **TRL 6–7 ESTIMATE**. Joint life-observing FM: **UNKNOWN**, **TRL 3–4 ESTIMATE**. Sparse-cell life maps: **TRL 2** (concept only). |
| **potential impact** | High as a **labeling copilot**. Harmful as an “AI ocean census.” |
| **next experiment** | `EXP-FOUND-ABSTAIN-01`. |
| **kill criteria** | (i) Any user-facing High confidence in cells with no local labels this season; (ii) ECE worse than a climatology on spatial blocks; (iii) product language “knows where the fish are.” |
| **readiness** | **REQUIRES_RESEARCH_BREAKTHROUGH** for observatory **life maps**. Vision copilot: `IMPLEMENTABLE_NOW` (evaluation only; no FishAI training until wedge/rights gates). Sparse-cell confident fill: **PHYSICALLY_UNLIKELY_OR_UNSUPPORTED** as measurement — **kill that claim**. |

---

### H-4.4 Digital twin with data assimilation

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.4-DTWIN-DA` |
| **statement** | A continuously assimilated physical–biogeochemical digital twin can provide **uncertainty-aware priors** (T, S, currents, nutrients, chlorophyll, oxygen) for life models. A twin that **assimilates fish/shellfish abundance** at operator grain is a different, unsolved problem. |
| **target organisms** | Directly: phytoplankton/BGC tracers. Indirectly: habitat envelopes for later biological models. **Not** Magallana, Chinook, or Homarus counts. |
| **measurement mechanism** | NEMO/PISCES or equivalent + 3DVar/EnKF + satellite OC + BGC-Argo; EU DTO/EDITO infrastructure. |
| **physical principle** | Primitive-equation hydrodynamics + biogeochemical ODEs; DA is Bayes/variational update. Life stages with behavior are **not** in standard BGC state vectors. |
| **required sensors/infrastructure** | CMEMS/EDITO access; BGC-Argo; ocean color; HPC. Fish twin would additionally need biological observing systems that do not yet exist at twin density. |
| **expected spatial/temporal resolution** | Global 1/12°–1/4° daily typical; coastal nested 100s of m in research configs. Biological skill does not inherit physical resolution. |
| **depth range** | Full column in models; DA constrained near surface (OC) and sparse profiles (Argo). |
| **geographic scalability** | High for physics/BGC via Copernicus. Low for a **global fish twin**. |
| **estimated cost** | ESTIMATE: \(10^4\)–\(10^5\) to **consume** CMEMS as priors; \(10^7\)–\(10^8\) to run a nested coastal twin with DA; fish-life DA: **unknown**, likely \(>10^8\) plus unsolved science. |
| **data rights/privacy** | CMEMS/EMODnet licenses; [EMODnet ToU](https://emodnet.ec.europa.eu/en/terms-use-emodnet-online-services-data-and-data-products) — products often CC BY 4.0, **source datasets may differ**. Do not assimilate confidential VMS/logbooks. |
| **ecological/safety** | Computational. Harm is **misuse** (twin output as harvest advice). |
| **validation method** | Hold-out BGC-Argo / glider; reliability of ensemble spread ([SEAMLESS-style ensemble BGC](https://os.copernicus.org/articles/20/155/2024/os-20-155-2024.pdf); [MedBFM NN+DA](https://os.copernicus.org/articles/20/689/2024/)). |
| **FP/FN risks** | Overconfident chlorophyll in Case-2 water; NN-reconstructed nitrate treated as observation; “what-if” scenarios presented as measurements. |
| **current evidence** | [EU DTO launch 2024](https://marine.copernicus.eu/news/european-digital-twin-ocean-launched-2024-digital-ocean-forum); [Copernicus role in DTO](https://marine.copernicus.eu/news/how-copernicus-marine-supports-european-digital-twin-ocean); [EDITO](https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe/eu-missions-horizon-europe/restore-our-ocean-and-waters/european-digital-twin-ocean_en). |
| **TRL** | Operational physics/BGC DA: **TRL 8–9**. EU DTO platform: **TRL 7 ESTIMATE** (pre-operational 2024–2025). Fish/shellfish DA twin: **UNKNOWN**, **TRL 2–3 ESTIMATE**. |
| **potential impact** | High as **covariate engine** for oyster stress, larval transport, hypoxia. Harmful if branded as a life census. |
| **next experiment** | `EXP-CMEMS-DA-01`. |
| **kill criteria** | (i) Twin emits animal abundance without biological assimilation; (ii) ensemble coverage fails pre-registered 80% intervals; (iii) SST-only twin beats BGC DA for the **stated biological** label (then the twin is not the mechanism). |
| **readiness** | **REQUIRES_PARTNERSHIP** to consume/adapt DTO/CMEMS. Full biological twin: `REQUIRES_RESEARCH_BREAKTHROUGH`. |

---

### H-4.5 Movement as fluid dynamics (larvae / plankton / jellies)

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.5-FLUID-MOVE` |
| **statement** | For organisms with weak swimming relative to currents (larvae, many plankton, some jellies), **Lagrangian transport in assimilated currents**, plus simple behavior (DVM, buoyancy), predicts connectivity and arrival windows better than Euclidean distance — **not** adult fish schools. |
| **target organisms** | Planktonic larvae (e.g. oyster veligers, crab zoeae), holoplankton, scyphomedusae with documented depth preference. Adult tuna/salmon: **out of hypothesis**. |
| **measurement mechanism** | Offline particle tracking (OpenDrift, LTRANS, ROMS floats) forced by CMEMS/ROMS; optional eDNA/GSI/otolith chemistry as destination labels. |
| **physical principle** | Advection–diffusion of nearly passive tracers; Stokes drift and vertical shear matter. Behavior is a **parameter**, not free AI. |
| **required sensors/infrastructure** | 3D currents, winds, rivers; spawning/release locations; PLD (pelagic larval duration); validation samples. |
| **expected spatial/temporal resolution** | Model 1–10 km typical; useful biological grain often **estuary / shelf / season**, not 100 m × hour. Global coastal atlas uses H3 res 5 (~10 km) and up to 180 d PLD ([Scientific Data 2025](https://www.nature.com/articles/s41597-025-05060-2)). |
| **depth range** | Surface to thermocline for most larvae; jellies often 0–40 m in cited Bering Sea work. |
| **geographic scalability** | Global atlases exist; **skill is local**. |
| **estimated cost** | ESTIMATE: \(10^4\)–\(10^5\) to apply published atlas + OpenDrift in one estuary; \(10^5\)–\(10^6\) with genetic/otolith validation. |
| **data rights/privacy** | Model output is not private; **release sites** of farms/hatcheries can be commercially sensitive — coarsen. |
| **ecological/safety** | Simulation. Do not use connectivity maps to target remaining wild spawners of listed stocks. |
| **validation method** | GSI/parentage, otolith chemistry, drifter matches, jellyfish isotope+model papers ([Pelagia 2025](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1608726/full)); tracker intercomparison ([GMD 2024](https://gmd.copernicus.org/articles/17/3341/2024/gmd-17-3341-2024.pdf)). |
| **FP/FN risks** | Wrong PLD, neglected behavior, unresolved estuarine residual flow, treating particles as adult habitat. |
| **current evidence** | Global connectivity dataset 2025; OpenDrift eDNA tracking literature; jellyfish particle-tracking (Bering Sea PLOS; Hangzhou Bay 2025). |
| **TRL** | Particle tracking: **TRL 8–9**. Operational biological arrival forecasts: **TRL 5–6 ESTIMATE** (site-specific). |
| **potential impact** | High for **oyster larval set windows, jellyfish/HAB transport, MPA connectivity**. None for 48 h Chinook bite. |
| **next experiment** | `EXP-CONNECT-01`. |
| **kill criteria** | (i) Connectivity probabilities do not rank observed assignment better than distance or random after one validation season; (ii) used as adult abundance; (iii) hatchery release GPS published. |
| **readiness** | **IMPLEMENTABLE_NOW** as a modeling experiment on public currents; **REQUIRES_PARTNERSHIP** for biological validation samples. |

---

### H-4.6 Underwater IoT / communications (acoustic / optical / EM, energy, biofouling)

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.6-UW-IOT` |
| **statement** | A hybrid underwater network (acoustic long-range, optical short-range high-rate, inductive/EM only at meters-to-tens of meters) can move **sparse biological sensor data** to shore if energy harvesting and antifouling are solved per node. A dense RF/EM ocean mesh is **not** proposed. |
| **target organisms** | Indirect (telemetry of whatever sensors are attached). |
| **measurement mechanism** | Acoustic modems; blue/green optical links in clear water; magnetic induction near nodes; surface gateway. |
| **physical principle** | Seawater is a conductor: EM skin depth at MHz–GHz is millimeters to meters. Acoustics: km-scale, low bandwidth, latency, mammal-noise issues. Optics: high rate, turbidity-limited ([2025 multimodal review](https://doi.org/10.54254/2755-2721/2025.22225)). |
| **required sensors/infrastructure** | Modems, energy (battery, wave, optical power transfer), UV/wiper antifouling ([wave-powered UV SBIR](https://sbir.org/awards/doe-DE-SC0020921-3)), surface telemetry. |
| **expected spatial/temporal resolution** | Node spacing: acoustics km; optics 10–100 m in clear water; EM ~1–10 m. Duty-cycled hours–days. |
| **depth range** | Full ocean with acoustics; optics mostly photic/clear; EM near-field. |
| **geographic scalability** | Poor as a **global mesh**. Viable as **cabled observatory + a few wireless hops**. |
| **estimated cost** | ESTIMATE: \(10^4\)–\(10^5\) per acoustic node-year; optical IoUT lab demos cheaper but not field-year. Regional IoUT: \(10^7\)+. |
| **data rights/privacy** | Underwater networks can leak vessel/mammal tracks. Encrypt; coarsen. |
| **ecological/safety** | Acoustic noise vs marine mammals; chemical antifoulants; battery waste. Prefer UV/mechanical wipers. |
| **validation method** | Packet delivery vs range/turbidity; biofouling days-to-failure; energy balance. |
| **FP/FN risks** | Not a biological FP/FN; **data loss** looks like “no animals.” |
| **current evidence** | UWSN reviews 2025; optical wireless power ISCAS 2025; hybrid acoustic-optical localization (Sensors 2018, still the physics). |
| **TRL** | Acoustic telemetry: **TRL 8–9**. Optical short-range: **TRL 5–6 ESTIMATE**. EM long-range: **TRL 2**, physically attenuated. Energy+fouling at year-scale: **TRL 5 ESTIMATE**. |
| **potential impact** | Enables other hypotheses; is not itself a life measurement. |
| **next experiment** | `EXP-UW-IOT-FOULING-01` (fouling/energy on one biological node — only if a partner already has a mooring). |
| **kill criteria** | (i) Architecture relies on long-range EM; (ii) node survival <30 days due to fouling/energy; (iii) acoustic duty cycle conflicts with PAM conservation goals. |
| **readiness** | **REQUIRES_NEW_SENSOR_DEPLOYMENT** for any dense IoUT. Long-range EM mesh: **PHYSICALLY_UNLIKELY_OR_UNSUPPORTED** — **kill**. Acoustic sparse telemetry: `IMPLEMENTABLE_NOW` as COTS. |

---

### H-4.7 Bioluminescence and optical ecology

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.7-BIOFLUORE` |
| **statement** | Stimulated or in situ bioluminescence (plus polarization/hyperspectral water-leaving radiance) is a **tracer of luminescent plankton and some micronekton**, useful for DVM and dinoflagellate ecology — **not** a species-resolved fish map. |
| **target organisms** | Bioluminescent dinoflagellates, many zooplankton, some fishes/cephalopods. ~75% of individuals in some mesopelagic counts are luminescent (Martini & Haddock 2017, cited by BIOLUMOPS). |
| **measurement mechanism** | Bathyphotometer / photon counter (Biosealight-class) on glider/CTD; mechanical stimulation; optional ocean-color dinoflagellate algorithms **as a separate, weaker proxy**. |
| **physical principle** | Luciferin–luciferase photon emission ~450–490 nm; stimulated flashes vs glow; Beer–Lambert attenuation of those photons. |
| **required sensors/infrastructure** | High-sensitivity PMT/SiPM, dark operation, stimulation grid, ancillary CTD/chl. |
| **expected spatial/temporal resolution** | Glider: km × hours × meters vertically. Satellite color: km × day, **surface only**, not photons from flashes. |
| **depth range** | Surface to mesopelagic (sensor-rated; Biosealight claims high-pressure rating — treat vendor depth as **unverified here**). |
| **geographic scalability** | Research campaigns. Not a planetary flash map. |
| **estimated cost** | ESTIMATE: \(10^5\)–\(10^6\) for a glider-season with dual bioluminescence sensors (BIOLUMOPS-scale). |
| **data rights/privacy** | Low, unless surveys overlay secret fishing. |
| **ecological/safety** | Mechanical stimulation disturbs a small volume. Avoid high-power strobes near listed turtles/mammals at night without review. |
| **validation method** | Net/IFCB/microscopy vs flash rate; classification of flash kinetics ([BIOLUMOPS 2024–2026](https://doi.org/10.5194/egusphere-egu24-8144); [Biosealight OCEANS 2025](https://doi.org/10.1109/oceans58557.2025.11104671)). |
| **FP/FN risks** | FP: cosmic rays/electronics, stimulated sediment, ship lights. FN: day-time, non-luminescent taxa, sensor saturation. Satellite dinoflagellate ≠ bioluminescence field. |
| **current evidence** | BIOLUMOPS; Biosealight; historical Atlantic bathyphotometer maps (Piontkovski). |
| **TRL** | Ship bathyphotometers: **TRL 7–8 ESTIMATE**. Compact autonomous sensors: **TRL 5–6 ESTIMATE**. Satellite bioluminescence: **TRL 2–3**, largely unsupported. |
| **potential impact** | Medium for plankton ecology and DVM carbon; low for FishAI 72 h farm stress unless HAB dinoflagellates are the target. |
| **next experiment** | `EXP-BIOFLU-01`. |
| **kill criteria** | (i) Flash rate sold as fish biomass; (ii) cannot separate dinoflagellate vs zooplankton flashes in the study area; (iii) ocean-color-only product labeled bioluminescence. |
| **readiness** | **REQUIRES_NEW_SENSOR_DEPLOYMENT**. Satellite-as-bioluminescence: `PHYSICALLY_UNLIKELY_OR_UNSUPPORTED` as a flash measurement. |

---

### H-4.8 Ocean sound fingerprints

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.8-SOUND-FP` |
| **statement** | Standardized hybrid millidecade (HMD) soundscape metrics plus detector outputs form a comparable **acoustic fingerprint of a site over time** (biophony, geophony, anthrophony). Fingerprints are **not** a census of silent taxa. |
| **target organisms** | Vocal fishes, soniferous invertebrates, marine mammals. Silent majority unobserved. |
| **measurement mechanism** | Calibrated hydrophone → HMD / decidecade spectra (SoundCoop / MANTA / PyPAM) → optional species detectors; archive at NCEI. |
| **physical principle** | Pressure waves 1 Hz–100s kHz; spreading, absorption, noise masking. |
| **required sensors/infrastructure** | Calibrated PAM instruments, clocks, metadata (Tethys), archive, detector libraries. |
| **expected spatial/temporal resolution** | Point / cabled; 1 min–1 h spectra; daily species presence products (SanctSound). Localization only with arrays/DAS. |
| **depth range** | Surface moorings to abyssal cabled observatories. |
| **geographic scalability** | High **where hydrophones already exist**; not globally uniform. |
| **estimated cost** | ESTIMATE: \(10^4\) to reuse NCEI products; \(10^5\)–\(10^6\) per new mooring-year. |
| **data rights/privacy** | Marine mammal detections are **NEVER_PUBLISH** at tracking resolution. Navy/SanctSound partnerships may restrict raw audio. |
| **ecological/safety** | Passive = low. Do not colocate with high-power active sources without review. |
| **validation method** | Manual audit of detector precision/recall; comparison across instruments ([NOAA PAM-Soundscapes](https://nmfs-ost.github.io/PAM_National_Network/content/SI%20coord/PAM_priority_projects/PAM-Soundscape.html); [SanctSound OBIS daily detections](https://obis.org/dataset/7a4427f6-67ee-4cc1-b95f-3045523420a1); [NCEI Passive Acoustic Data](https://www.ncei.noaa.gov/products/passive-acoustic-data)). |
| **FP/FN risks** | Detector FP on vessels/rain; FN in noise; treating HMD energy as biomass. |
| **current evidence** | SanctSound 2018–2021; Noise Reference Station network; SoundCoop HMD netCDF; IQOE. |
| **TRL** | PAM recording: **TRL 9**. Comparable HMD products: **TRL 7–8 ESTIMATE**. Biodiversity-from-soundscape for all taxa: **TRL 3**. |
| **potential impact** | High for vocal protected species **presence** and noise budgets; complementary, not a life mesh. |
| **next experiment** | `EXP-SOUND-HMD-01`. |
| **kill criteria** | (i) Soundscape energy labeled as fish abundance; (ii) fine whale tracks in any public layer; (iii) uncalibrated hobby hydrophones enter the fingerprint without flags. |
| **readiness** | **IMPLEMENTABLE_NOW** as reuse of archived metrics (rights review). New global array: `REQUIRES_NEW_SENSOR_DEPLOYMENT`. |

---

### H-4.9 Smart fishing gear as sensors

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.9-SMART-GEAR` |
| **statement** | Instrumented buoys, pots, and electronic monitoring cameras can report **effort, soak, temperature, motion, and (with EM) catch composition** for the owner and, if coarsened, for science. They do **not** measure stock abundance of unfished cells. |
| **target organisms** | Target catch + bycatch in that gear; water-column T as habitat covariate. |
| **measurement mechanism** | GPS/IMU/SST smart buoys (Farallon-class); EM cameras; optional in-trawl cameras/AI. |
| **physical principle** | GNSS at surface; inertial motion; thermistors; computer vision on catch. |
| **required sensors/infrastructure** | Buoy + satellite subscription; EM hardware; DUA; on-demand/ropeless integration where entanglement rules apply. |
| **expected spatial/temporal resolution** | Native: trap GPS × minutes. Public: statistical area / 10-minute square with rule-of-3. |
| **depth range** | Surface buoy; trap on bottom (lobster/crab); midwater for some pelagic gear. |
| **geographic scalability** | Follows commercial fleets that can afford units. |
| **estimated cost** | ESTIMATE: \(10^3\)–\(10^4\) per smart buoy-year subscription; [NOAA 2025 intent for 30 buoys](https://www.highergov.com/contract-opportunity/notice-of-intent-to-sole-source-smart-buoys-143021-25-0075-s-45b3a/) implies fleet packs ~\(10^5\). EM systems \(10^4\)–\(10^5\) per vessel-year. |
| **data rights/privacy** | Exact gear GPS is **PRIVATE / NEVER_PUBLISH**. Third parties see data only with permission or aggregate ([NOAA TPO Smart Buoy](https://techpartnerships.noaa.gov/blue-ocean-gear-smart-buoy/)). |
| **ecological/safety** | Ropeless + smart buoys can **reduce** entanglement if they replace vertical lines ([NOAA BREP 2025](https://dev-www.fisheries.noaa.gov/funding-financial-services/2025-bycatch-reduction-engineering-program-projects-recommended-funding)). Do not map whale locations from “anomalous buoy motion” to the public. |
| **validation method** | Buoy T vs independent logger; soak vs logbook; EM vs observer subsample ([NOAA TM SPO239 EM](https://spo.nmfs.noaa.gov/sites/default/files/TMSPO239.pdf)). |
| **FP/FN risks** | Motion FP as entanglement/catch; missed events; using fleet density as biomass. |
| **current evidence** | Blue Ocean Gear SBIR/operational; ropeless NEFSC procurement 2025; EM bycatch literature. |
| **TRL** | Smart buoys: **TRL 8–9 ESTIMATE**. EM: **TRL 8** in some U.S. fisheries. Abundance-from-gear-network: **TRL 2**. |
| **potential impact** | High for **effort, ghost gear, bottom T, private CPUE**. Aligns with lobster wedge **Category C**, not N. |
| **next experiment** | `EXP-GEAR-SST-01`. |
| **kill criteria** | (i) Public gear tracks; (ii) AIS/buoy density as lobster abundance; (iii) entanglement-motion detector unvalidated yet user-facing. |
| **readiness** | **REQUIRES_PARTNERSHIP** (and is **IMPLEMENTABLE_NOW** for metocean/effort on consenting vessels). |

---

### H-4.10 Aquaculture as sentinel network

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.10-AQUA-SENTINEL` |
| **statement** | Shellfish and finfish farms already occupy productive coastal water and can form a **sentinel network** for temperature, salinity, DO, HAB cells/toxins (non-legal), pathogens (eDNA), and **private** animal performance — informing farm ops-risk, **not** NSSP harvest legality. |
| **target organisms** | Farmed *Magallana gigas* / mussels / salmonids as sentinels; wild HAB taxa; pathogens (OsHV-1, *Vibrio* — **display ≠ safety determination**). |
| **measurement mechanism** | In-bag loggers (HOBO/AquaTROLL); SoundToxins-like microscopy; optional eDNA; grower mortality logs. |
| **physical principle** | Sessile animals integrate water-mass exposure; sensors measure state variables that drive stress (air T × emersion, DO, heat). |
| **required sensors/infrastructure** | Loggers, tide model, grower protocol, pathology backup, DUA. NANOOS-class dashboards already exist as **partial** infrastructure. |
| **expected spatial/temporal resolution** | Lease/bag microclimate × minutes internally; public **growing-area / sub-basin × 6–24 h**. |
| **depth range** | Intertidal to shallow subtidal farms; not oceanic. |
| **geographic scalability** | High in aquaculture regions (WA, Gulf, Europe, East Asia); zero in high seas. |
| **estimated cost** | ESTIMATE: \(10^4\)–\(10^5\) for 5–15 farm pilot (loggers + protocol + analysis); regional network \(10^6\). FARMS already NOAA-funded VA–TX ([UF/IFAS FARMS 2025–26](https://shellfish.ifas.ufl.edu/farms-2023/)). |
| **data rights/privacy** | Farm mortality **PRIVATE**. No leaderboards. CARE if tribal leases. |
| **ecological/safety** | Low. Disease reporting may have statutory duties — counsel. Never replace tissue toxin tests ([seawater PSP is operational warning only](https://sensoreal.com/seawater-testing-paralytic-shellfish-poisoning-psp-early-warning/)). |
| **validation method** | Pre-registered 72 h air×tide rule vs workability/mortality vs SST-only (FishAI marine-domain E1); SoundToxins vs DOH **as context split**. |
| **FP/FN risks** | FP: heat flag without mortality (handling, ploidy). FN: delayed death beyond 72 h; hypoxia off-sensor. Food-safety contamination of the label. |
| **current evidence** | FARMS; [ULTFARMS Belwind eDNA+sensors](https://ultfarms.eu/pilot-6-belwind/); Australian sensors+eDNA CRC 2024; NANOOS Shellfish Growers; Raymond et al. 2022 heatwave. |
| **TRL** | Farm loggers: **TRL 9**. Coordinated sentinel networks: **TRL 7–8 ESTIMATE**. eDNA disease surveillance: **TRL 5–6 ESTIMATE**. |
| **potential impact** | **Highest FishAI alignment** with recommended oyster wedge (still UNRESOLVED). |
| **next experiment** | `EXP-AQUA-SENTINEL-01`. |
| **kill criteria** | (i) Any harvest “safe/unsafe” model; (ii) SST-only beats air×tide+DO on holdout; (iii) partners will not log outcomes; (iv) public farm KPI map. |
| **readiness** | **IMPLEMENTABLE_NOW** with consenting growers (**REQUIRES_PARTNERSHIP** for data, not for physics). |

---

### H-4.11 Genetic stock / population-ID engine

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.11-GSI-STOCK` |
| **statement** | SNP GSI (and PBT/tGMR where pedigrees exist) can assign **sampled** fishes to reporting groups with quantified error, enabling mixed-stock composition. It cannot ID fish that were not sampled and must not emit ESA-listed **location maps**. |
| **target organisms** | Chinook (*Oncorhynchus tshawytscha*) is the mature case; other taxa need baselines. Shellfish population-ID is weaker/different (aquaculture lines, not ocean GSI). |
| **measurement mechanism** | Tissue/fin/scale → GT-seq / amplicon SNPs → baseline assignment; optional parentage. |
| **physical principle** | Mendelian markers + allele-frequency differences among populations. |
| **required sensors/infrastructure** | Baseline (Pacific Rim Chinook ~389–391 pops / ~391 SNPs); lab; representative fishery samples; chain of custody. |
| **expected spatial/temporal resolution** | Individual fish; mixture at **fishery × week/season**, not 1 km. |
| **depth range** | n/a (sampled catch). |
| **geographic scalability** | High where baselines exist (Pacific salmon). Global multi-taxon engine: decades. |
| **estimated cost** | ESTIMATE: \(20\)–\(100\) per sample processed at scale; \(10^5\)–\(10^6\) for a fishery-season program (18k BC marine Chinook were genotyped in published PBT+GSI work). |
| **data rights/privacy** | Individual genotypes + capture location can identify stocks of conservation concern. **No ESU pin maps.** Hatchery pedigrees may be restricted. |
| **ecological/safety** | Non-lethal fin clips possible; lethal samples from already-caught fish preferred. Effort concentration on weak stocks is a **management** risk even if biology is accurate. |
| **validation method** | Cross-validation of baseline; CWT concordance; mixture simulation ([Van Doornik et al. NAFM 2024](https://doi.org/10.1002/nafm.11019); [Dryad baseline](https://doi.org/10.5061/dryad.dz08kps5b); [PBT+GSI BC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8127719/); [tGMR Chilkat](https://doi.org/10.1111/eva.13647)). |
| **FP/FN risks** | Mis-assignment among close reporting groups; unrepresentative samples; using GSI as abundance without catch/effort. |
| **current evidence** | As above. tGMR can enumerate **some** salmon populations; sampling design biases are documented. |
| **TRL** | Chinook GSI: **TRL 8–9**. Multi-species global engine: **UNKNOWN**, **TRL 4 ESTIMATE**. |
| **potential impact** | High for **mixed-stock fishery composition**. Dangerous as a public “where listed Chinook are.” |
| **next experiment** | `EXP-GSI-CHINOOK-01`. |
| **kill criteria** | (i) Public ESU heatmaps; (ii) assignment accuracy below pre-registered reporting-group threshold on realistic mixtures; (iii) samples lack legal/ethical take authority. |
| **readiness** | **IMPLEMENTABLE_NOW** for Chinook **composition** with labs + lawful samples (`REQUIRES_PARTNERSHIP`). Other taxa: `REQUIRES_NEW_SENSOR_DEPLOYMENT` of baselines. |

---

### H-4.12 Predator–prey coupled tracking

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.12-PREDPREY` |
| **statement** | Simultaneous biologging of predators **and** independent prey-field observations (trawls, acoustics, prey tags, diet) can identify **coupling** (selection, facilitation, interference). Tagging only predators does **not** map prey biomass. |
| **target organisms** | Tunas, sharks, seabirds, marine mammals as platforms; forage fishes/cephalopods as prey. |
| **measurement mechanism** | PAT/archival/IMU/video tags; prey surveys; diet/trait electivity ([albacore trait selection](https://doi.org/10.1016/j.ecolind.2023.111473); [shearwater–dolphinfish–anchovy](https://doi.org/10.1098/rsbl.2024.0223); [bluefin eaten by orca](https://www.nature.com/articles/s41598-024-80744-0)). |
| **physical principle** | Animal motion + bioenergetics; encounter rates in a moving prey field. |
| **required sensors/infrastructure** | Tags, permits (MMPA/ESA), prey surveys, diet lab. |
| **expected spatial/temporal resolution** | Individual tracks seconds–days; prey fields often seasonal surveys — **mismatch is the scientific problem**. |
| **depth range** | Epipelagic to mesopelagic depending on species. |
| **geographic scalability** | Campaign-scale, not planetary. |
| **estimated cost** | ESTIMATE: \(10^3\)–\(5\times10^3\) per tag + vessel time; coupled campaign \(10^6\)–\(10^7\). |
| **data rights/privacy** | Tracks of listed species **NEVER_PUBLISH**. |
| **ecological/safety** | Tagging harm, capture stress; IACUC/permits required. |
| **validation method** | Video/gut overlap; prey survey electivity; independent acoustic prey. |
| **FP/FN risks** | Inferring prey from predator habitat (circular); tag effects; n=1 predation events over-generalized. |
| **current evidence** | Opportunistic coupled events exist; **no** operational coupled observatory. |
| **TRL** | Predator biologging: **TRL 8–9**. Operational coupled prey-field observatory: **TRL 4 ESTIMATE**. |
| **potential impact** | High scientific; low for 24–72 h FishAI operator product. |
| **next experiment** | `EXP-PRED-ELECTIVITY-01` (diet vs survey traits — **no new tagging** first). |
| **kill criteria** | (i) Predator tracks used as public forage-fish maps; (ii) tagging without permits; (iii) n too small to beat diet climatology. |
| **readiness** | **REQUIRES_NEW_SENSOR_DEPLOYMENT** (and permits) for coupled tracking. Desktop electivity: `IMPLEMENTABLE_NOW` on published datasets. Planetary coupling: `SPECULATIVE_BUT_PHYSICALLY_PLAUSIBLE`. |

---

### H-4.13 Planetary marine observation marketplace

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.13-MARKETPLACE` |
| **statement** | A governed marketplace can price **rights-cleared, coarsened, quality-flagged** ocean observations (physical, BGC, occupancy, acoustics features) with provenance — **not** a commodity market in secret fishing spots or farm yields. |
| **target organisms** | None directly; it is an institution over data about organisms. |
| **measurement mechanism** | Contracts, meters, license graphs, quality scores, privacy tests — not a sensor. |
| **physical principle** | n/a. Economic mechanism design + data law. |
| **required sensors/infrastructure** | Legal entity, DUA templates, coarsening pipeline, audit, payment, INSPIRE/FAIR metadata. FishAI already drafted partner DUA/privacy policy. |
| **expected spatial/temporal resolution** | Public SKUs at policy grain only. |
| **depth range** | n/a. |
| **geographic scalability** | Governance-limited, not physics-limited. |
| **estimated cost** | ESTIMATE: \(10^5\)–\(10^6\) to stand up a lawful **pilot** catalog; planetary liquidity **UNKNOWN**. |
| **data rights/privacy** | Core risk. GFW APIs are **CC BY-NC** ([GFW license](https://globalfishingwatch.org/our-apis/documentation/docs/license-rate-limits.md)); AIS is **not fish**. EMODnet products ≠ source licenses. |
| **ecological/safety** | Harm if marketplace sells targeting intelligence on listed species or remaining aggregations. |
| **validation method** | Reverse-engineering tests (FishAI privacy §4.2); license audits; contributor retention. |
| **FP/FN risks** | n/a biologically. Institutional FP: “open” data that is actually NC or confidential. |
| **current evidence** | EMODnet, IOOS, OBIS, CMEMS as **public goods**, not two-sided markets. No proven planetary **life-observation** commodity exchange. |
| **TRL** | Data portals: **TRL 9**. Two-sided observation marketplace with privacy-preserving biological SKUs: **UNKNOWN**, **TRL 3 ESTIMATE**. |
| **potential impact** | Could fund sentinels if SKUs are boring (HMD, occupancy, T/S). Catastrophic if SKUs are spots. |
| **next experiment** | `EXP-MARKET-SKU-01` (legal/privacy tabletop + one coarsened SKU — no ingestion of catch GPS). |
| **kill criteria** | (i) Any SKU is exact catch/farm/listed-species location; (ii) GFW/AIS sold as abundance; (iii) contributors cannot revoke; (iv) reverse-engineering test fails. |
| **readiness** | **REQUIRES_PARTNERSHIP** (counsel + contributors). Public catch marketplace: **PHYSICALLY_UNLIKELY_OR_UNSUPPORTED** as a lawful observatory function — **kill that variant**. |

---

## 3. Additional original hypotheses (≥5)

### H-4.14 Distributed acoustic sensing on submarine cables

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.14-DAS-CABLE` |
| **statement** | An interrogator on dark fiber in existing seafloor telecom cables can detect and localize **low-frequency baleen-whale calls and some vessels** along tens–hundreds of km. It is **not** demonstrated as a general fish census (most fishes vocalize at higher frequencies or not at all). |
| **target organisms** | Fin, blue, pygmy blue, Omura’s, other low-frequency mysticetes. Fish: unsupported. |
| **measurement mechanism** | Rayleigh backscatter strain along fiber (DAS) → FK/template/YOLO detectors → localization with one or two cables. |
| **physical principle** | Acoustic pressure induces strain in fiber; DAS samples every ~4–10 m; SNR decays with range (~0.2 dB/km optical). |
| **required sensors/infrastructure** | Cable-owner agreement, interrogator, power, huge data pipe, detection software. |
| **expected spatial/temporal resolution** | ~100 m localization in Arctic two-cable tests; detection along 40–120 km segments in published trials; near-real-time possible with research networks. |
| **depth range** | Seafloor cable depth (shelf–slope). |
| **geographic scalability** | Follows cable landings, not animal habitat. |
| **estimated cost** | ESTIMATE: \(10^6\)–\(10^7\) per cable-year (interrogator + ops + data); cheaper than equivalent hydrophone density **if** fiber is already there. |
| **data rights/privacy** | Cable owners, landing-state security, **NEVER_PUBLISH** whale tracks. |
| **ecological/safety** | Passive. Data could inform ship-strike mitigation **privately**. |
| **validation method** | Hydrophone arrays, airgun localization, AIS vessel matches ([Svalbard two-cable](https://doi.org/10.3389/fmars.2023.1130898); [Oregon 2025](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1603541/full); [NW Australia](https://doi.org/10.1071/ep23268); [JASA 2025 DAS vs hydrophones](https://doi.org/10.1121/10.0037512)). |
| **FP/FN risks** | FP: ships, quakes, cable coupling gaps. FN: high-frequency odontocetes/fishes, poor seafloor coupling. |
| **current evidence** | Multiple 2022–2025 peer-reviewed detections of baleen whales. |
| **TRL** | Whale-call detection research: **TRL 6–7 ESTIMATE**. Operational conservation feed: **TRL 5 ESTIMATE**. Fish DAS: **TRL 1–2**. |
| **potential impact** | High for **baleen presence along cables**. Off-wedge for FishAI operator product; on-wedge for a **saltwater life observatory** mammal module. |
| **next experiment** | `EXP-DAS-WHALE-01`. |
| **kill criteria** | (i) Marketed as fish abundance; (ii) public whale tracks; (iii) precision/recall below pre-registered vs hydrophones; (iv) no cable access after 90 days of outreach. |
| **readiness** | **REQUIRES_PARTNERSHIP**. Fish-census variant: **PHYSICALLY_UNLIKELY_OR_UNSUPPORTED**. |

### H-4.15 Animal-borne sensors as opportunistic network nodes

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.15-ANIBOS-NODE` |
| **statement** | Tagged marine animals already deliver **T/S/depth profiles** (AniBOS/MEOP) from under-sampled seas. Treating animals as **communications relays** for other sensors is a separate, speculative layer. |
| **target organisms** | Seals (elephant, Weddell, hooded, etc.) as platforms; fishes only if tags exist. |
| **measurement mechanism** | CTD-SRDL tags → Argos/Iridium; QC in MEOP. |
| **physical principle** | Conductivity/temperature vs pressure on diving animals; telemetry at surface. |
| **required sensors/infrastructure** | Tagging permits, Argos, MEOP QC. Mesh radios on animals: extra mass/drag — **not assumed**. |
| **expected spatial/temporal resolution** | Foraging-biased profiles; ~500 profiles/animal/year typical in AniBOS description; recovered tags denser. |
| **depth range** | To animal’s dive depth (100s–1000s m). |
| **geographic scalability** | Polar and some temperate shelves; not tropics uniformly. |
| **estimated cost** | ESTIMATE: \(10^4\) per tag deployment; reuse of public MEOP: \(10^4\) analysis. |
| **data rights/privacy** | MEOP public after form; animal welfare ethics; do not publish den/pupping sites. |
| **ecological/safety** | Tag burden. GOOS network exists because benefit/burden has been argued for seals — **do not casually expand to new taxa**. |
| **validation method** | Ship/Argo coincidences (MEOP literature); [AniBOS](https://anibos.com/); [GOOS AniBOS](https://goosocean.org/who-we-are/observations-coordination-group/global-ocean-observing-networks/animal-borne-ocean-sensors-anibos/); [MEOP-CTD 2024-03-08: 872,119 profiles](http://meop.net/database/meop-databases/meop-ctd-database.html). |
| **FP/FN risks** | Salinity biases on some tags; spatial bias to prey. Using seal tracks as fish maps. |
| **current evidence** | 20+ years; GOOS emerging network; UN Decade project. |
| **TRL** | Seal CTD observing: **TRL 8–9**. Animal mesh-network radios: **TRL 2–3**, `SPECULATIVE_BUT_PHYSICALLY_PLAUSIBLE`. |
| **potential impact** | High as **bottom/under-ice T,S prior** (lobster/Chinook thermal habitat). |
| **next experiment** | `EXP-ANIBOS-TS-01`. |
| **kill criteria** | (i) Tracks as public forage maps; (ii) salinity QC fails vs Argo in the study region; (iii) new taxa tagged without ethics. |
| **readiness** | **IMPLEMENTABLE_NOW** (data reuse). Relay-mesh: `SPECULATIVE_BUT_PHYSICALLY_PLAUSIBLE`. |

### H-4.16 FerryBox / SOOP molecular

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.16-FERRYBOX-MOL` |
| **statement** | Repeat commercial routes with FerryBox physics **plus** automated eDNA/IFCB sampling can produce **transect occupancy and plankton composition** at weekly–seasonal scale without dedicated research ships. |
| **target organisms** | Phytoplankton, microbes, some metazoan eDNA; not quantified fish N. |
| **measurement mechanism** | Engine-intake or scientific underway pump → FerryBox (T,S,chl,cDOM,turbidity,O2) + WASP/PPS filtration or passive sponges. |
| **physical principle** | Same as eDNA + fluorescence; intake depth is a **fixed biased sample**. |
| **required sensors/infrastructure** | Vessel operator agreement, space, power, biosecurity, lab. |
| **expected spatial/temporal resolution** | Along-route km × hours; repeat days–weeks. |
| **depth range** | Intake typically 3–8 m. |
| **geographic scalability** | Follows ferry/cruise networks (Europe high; global gaps). |
| **estimated cost** | ESTIMATE: \(10^5\)–\(5\times10^5\) for one route-year molecular add-on. |
| **data rights/privacy** | Operator contracts; port-state ABS. |
| **ecological/safety** | Intake already exists; added sampling volume small. Ethanol/fixatives aboard ships. |
| **validation method** | Manual filtration vs PPS ([JERICO WASP 2023–24 Oslo–Kiel](https://doi.org/10.13155/103701)); [passive sponges Tangaroa](https://doi.org/10.1016/j.scitotenv.2024.174354); [HX SOOP eDNA](https://www.soop-platform.earth/usecases/use-case-1-hx-de/). |
| **FP/FN risks** | Intake biofilm contamination; harbor vs sea mixing; eDNA transport. |
| **current evidence** | Demonstrations 2023–2024, not a global operational EOV. |
| **TRL** | FerryBox physics: **TRL 9**. Unattended eDNA on FerryBox: **TRL 6 ESTIMATE**. |
| **potential impact** | High cost-efficiency for **coastal community change**. |
| **next experiment** | `EXP-FERRY-EDNA-01`. |
| **kill criteria** | (i) Contamination indistinguishable from biology; (ii) operator exits; (iii) sold as fish counts. |
| **readiness** | **REQUIRES_PARTNERSHIP**. |

### H-4.17 Hyperspectral / lidar shallow-water schools

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.17-HYPERSPEC-SCHOOL` |
| **statement** | **Airborne** green lidar (and, secondarily, high-resolution hyperspectral/UAV imagery) can map **near-surface epipelagic schools** in clear shallow water, with species ID requiring cameras/catch. **Satellite** PACE (~1.2 km) cannot resolve individual schools. |
| **target organisms** | Sardine, anchovy, menhaden, other surface-schooling pelagics; kelp/slicks as confounders. |
| **measurement mechanism** | Polarized lidar backscatter vs depth; optional camera; HS for water constituents not fish bodies at satellite scale. |
| **physical principle** | 532 nm lidar scattering from fish vs particles; attenuation limits depth (typically tens of m in clear water). |
| **required sensors/infrastructure** | Aircraft/UAV lidar (NOAA FLOE heritage), calm/clear conditions, coincident echosounder. |
| **expected spatial/temporal resolution** | Airborne: meters × survey day. PACE: ~1 km, **habitat not schools**. PRISMA 30 m: water quality / bathymetry, **not demonstrated school ID**. |
| **depth range** | Upper tens of meters; fails in turbid estuaries (Willapa may be hard). |
| **geographic scalability** | Campaign, weather-limited. |
| **estimated cost** | ESTIMATE: \(10^5\)–\(10^6\) per survey campaign. |
| **data rights/privacy** | School maps are **spot maps** — PRIVATE / coarsen. |
| **ecological/safety** | Eye-safe lidar protocols; do not publish waypoints. |
| **validation method** | Lidar vs EK80 ([Churnside et al. ICES JMS 2003](https://psl.noaa.gov/technology/instruments/floe/pdf/A_comparison_of_lidar_and_echosounder_measurements_of_fish.pdf); [ML ROI 2022 NOAA](https://repository.library.noaa.gov/view/noaa/41012/noaa_41012_DS1.pdf)). PACE as **optical niche** not schools ([NOAA TM PACE fisheries](https://spo.nmfs.noaa.gov/sites/default/files/NMFS_TM_HyperspectralOC-SPO-TM-255_1.pdf)). |
| **FP/FN risks** | FP: kelp, wakes, bubbles. FN: deep/night/turbid schools. Satellite school claim: resolution failure. |
| **current evidence** | Airborne lidar **works** in published tests; not an operational global survey. PACE launched 2024 for ocean color, not fish bodies. |
| **TRL** | Airborne fisheries lidar: **TRL 6–7 ESTIMATE** (demonstrated, not routine NOAA ops). Satellite school detection: **TRL 1–2**. |
| **potential impact** | Medium for clear-water pelagic surveys. Low for WA oyster wedge. |
| **next experiment** | `EXP-LIDAR-SCHOOL-01` only if a clear-water pelagic question is in scope; otherwise **do not fund**. |
| **kill criteria** | (i) Satellite pixels labeled as schools; (ii) lidar FP from kelp/wakes unsolved; (iii) public school waypoints. |
| **readiness** | Airborne: **REQUIRES_NEW_SENSOR_DEPLOYMENT**. Satellite individual schools: **PHYSICALLY_UNLIKELY_OR_UNSUPPORTED**. |

### H-4.18 Coastal intake eDNA sentinels (power / desal / hatchery)

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.18-INTAKE-EDNA` |
| **statement** | Existing high-volume seawater intakes (power plants, desalination, hatcheries) are **continuous, powered sampling ports** for eDNA occupancy, larval entrainment, and fouling/jellyfish risk — a coastal sentinel cheaper than new moorings. |
| **target organisms** | Ichthyoplankton, jellies, foulers, farm pathogens near hatcheries. |
| **measurement mechanism** | Timed intake aliquots → eDNA/qPCR/metabarcoding; optional larval ID. |
| **physical principle** | Same eDNA physics; intake integrates a poorly known capture zone. |
| **required sensors/infrastructure** | Plant access, biosecurity, autosampler, lab. |
| **expected spatial/temporal resolution** | One point × hours–days; spatial footprint **unknown** without dye/hydro study. |
| **depth range** | Intake depth (typically 5–20 m coastal). |
| **geographic scalability** | All industrialized coasts; not ocean basins. |
| **estimated cost** | ESTIMATE: \(5\times10^4\)–\(2\times10^5\) per site-year. |
| **data rights/privacy** | Critical infrastructure access; pathogen results may be sensitive for hatcheries. |
| **ecological/safety** | Plants already kill larvae ([Kozienice metabarcoding 2023](https://www.kmae-journal.org/articles/kmae/full_html/2023/01/kmae230056/kmae230056.html)); sampling does not add that harm. Do not greenwash entrainment. |
| **validation method** | eDNA vs nets/pumps ([power-plant qPCR](https://doi.org/10.1002/edn3.286); [Fangchenggang jellies eDNA](https://pmc.ncbi.nlm.nih.gov/articles/PMC12967418/)). |
| **FP/FN risks** | Biofilm in pipes; chlorination; non-local DNA. |
| **current evidence** | Multiple 2022–2024 intake eDNA papers; not a U.S. West Coast oyster-hatchery network yet. |
| **TRL** | **TRL 5–6 ESTIMATE**. |
| **potential impact** | High near hatcheries (larval/pathogen watch) if **not** used as food-safety. |
| **next experiment** | `EXP-INTAKE-EDNA-01`. |
| **kill criteria** | (i) Pipe biofilm dominates signal vs intake water; (ii) plant denies access; (iii) results used as harvest legality. |
| **readiness** | **REQUIRES_PARTNERSHIP**. |

### H-4.19 In situ imaging plankton mesh (IFCB / UVP-class)

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.19-IFCB-MESH` |
| **statement** | Imaging FlowCytobot and similar in situ imagers already provide **cell-resolved phytoplankton/HAB time series**; a mesh of IFCBs (and shipboard UVP for particles/jellies) is a **true biological observing system** for the base of the food web. |
| **target organisms** | Nano–microplankton, HAB taxa; UVP: particles, some jellies. |
| **measurement mechanism** | Flow-through imaging + ML classification; volumes in mL–L. |
| **physical principle** | Optical scattering trigger + camera; morphology ≠ toxin. |
| **required sensors/infrastructure** | IFCB (~\(10^5\) class instrument), power, biofouling mitigation, classification models, dashboard. |
| **expected spatial/temporal resolution** | Mooring: hours at a point. Ship: along-track. Not basin maps without interpolation **with abstention**. |
| **depth range** | Typically near-surface pumped; UVP profiles deeper. |
| **geographic scalability** | Expanding U.S. HABON; not global. |
| **estimated cost** | ESTIMATE: \(1.5\times10^5\)–\(4\times10^5\) per IFCB site-year. |
| **data rights/privacy** | Generally public science; check HABON/WHOI terms. |
| **ecological/safety** | Low. Cell ≠ NSSP toxin. |
| **validation method** | Microscopy; toxin assays separate ([HABON-NE](https://northeasthab.whoi.edu/bloom-monitoring/habon-ne/); [IFCB dashboard](https://habon-ifcb.whoi.edu/dashboard)). |
| **FP/FN risks** | Classifier confusion; toxin decoupled from cells. |
| **current evidence** | MVCO multi-year; HABON-NE operational framework; 2024–2025 deployments. |
| **TRL** | IFCB HAB surveillance: **TRL 8–9 ESTIMATE**. |
| **potential impact** | High for HAB/forage-base; **validation backbone** for PACE PFTs. |
| **next experiment** | `EXP-IFCB-HABON-01`. |
| **kill criteria** | (i) Cell counts as harvest-safe; (ii) classifier F1 below pre-registered for target HAB; (iii) fouling gaps unflagged. |
| **readiness** | **IMPLEMENTABLE_NOW** via data reuse; denser mesh `REQUIRES_NEW_SENSOR_DEPLOYMENT`. |

### H-4.20 PACE hyperspectral phytoplankton functional types as forage-field **prior**

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.20-PACE-PFT` |
| **statement** | PACE-OCI hyperspectral radiances improve **phytoplankton community / optical-niche** fields that can enter habitat models as a **prior**. They are **not** fish, lobster, or oyster abundance ([NOAA PACE fisheries TM](https://spo.nmfs.noaa.gov/sites/default/files/NMFS_TM_HyperspectralOC-SPO-TM-255_1.pdf); [PACE fisheries blog](https://pace.oceansciences.org/blog.htm?id=31)). |
| **target organisms** | Phytoplankton groups; fish only as downstream, weakly coupled consumers. |
| **measurement mechanism** | OCI ~315–895 nm, ~1.2 km, near-daily, glint-tilt. |
| **physical principle** | Absorption/scattering fingerprints of pigments and IOPs. |
| **required sensors/infrastructure** | NASA Earthdata; matchups with IFCB/HPLC/BGC-Argo. |
| **expected spatial/temporal resolution** | ~1 km × 1 day, clouds; coastal Case-2 harder. |
| **depth range** | First optical depth. |
| **geographic scalability** | Global. |
| **estimated cost** | ESTIMATE: \(10^4\)–\(10^5\) for a matchup study (data are free). |
| **data rights/privacy** | NASA public. |
| **ecological/safety** | None. Misuse: “PACE shows the fish.” |
| **validation method** | IFCB/HPLC matchups; pre-register that skill is for PFT/chl, **not** CPUE. |
| **FP/FN risks** | Coastal adjacency, CDOM, sediment; optical niche ≠ adult Chinook. |
| **current evidence** | PACE launched 2024-02-08; NOAA applications workshop: optical niche added **12±8%** explained variance in some fish SDMs — **habitat, not count**. |
| **TRL** | Ocean color: **TRL 9**. Hyperspectral PFT products: **TRL 6–7 ESTIMATE** (early mission). |
| **potential impact** | Honest forage/habitat covariate; cheap uncertainty reduction if claims stay bounded. |
| **next experiment** | `EXP-PACE-PFT-01`. |
| **kill criteria** | (i) Any user-facing “fish from PACE”; (ii) PFT skill fails IFCB matchups in the study region; (iii) used as oyster mortality label. |
| **readiness** | **IMPLEMENTABLE_NOW** (analysis). |

### H-4.21 Spaceborne lidar particulate backscatter as plankton-layer prior

| Field | Content |
|---|---|
| **hypothesis_id** | `H-4.21-SPACE-LIDAR-BBP` |
| **statement** | CALIOP heritage, ICESat-2 ATLAS, and EarthCARE ATLID retrieve **upper-ocean particulate backscatter / chlorophyll-related quantities**, including night and high latitude, as a **plankton/POC layer prior** — not nekton. |
| **target organisms** | Particles, phytoplankton; krill only as **speculative, weakly supported** secondary literature. |
| **measurement mechanism** | 532/355 nm space lidar subsurface return after instrument-artifact correction. |
| **physical principle** | Elastic backscatter from particles; few optical depths penetration. |
| **required sensors/infrastructure** | NASA OB.DAAC CALIOP bbp v1; ICESat-2; optional ATLID. |
| **expected spatial/temporal resolution** | Along-track lidar curtains; not hourly maps. |
| **depth range** | Upper tens of meters typically. |
| **geographic scalability** | Global, orbit-sampled. |
| **estimated cost** | ESTIMATE: \(10^4\)–\(10^5\) analysis. |
| **data rights/privacy** | NASA public. |
| **ecological/safety** | None. |
| **validation method** | BGC-Argo bbp/chl ([Lu et al. 2021](https://doi.org/10.1029/2021ea001839); [CALIOP bbp product](https://www.earthdata.nasa.gov/data/catalog/ob-cloud-calipso-caliop-l3-bbp-1); [ATLID 2026 abstract](https://doi.org/10.5194/egusphere-egu26-10155)). |
| **FP/FN risks** | Crosstalk/afterpulsing artifacts; calling bbp “fish.” |
| **current evidence** | Validated bbp/chl retrievals; CALIOP ended Jul 2023 but archive remains. |
| **TRL** | **TRL 6–8 ESTIMATE** for bbp/chl. Nekton: **TRL 2**. |
| **potential impact** | Complements PACE at night/poles. |
| **next experiment** | Fold into `EXP-PACE-PFT-01` as night/high-lat extension; standalone `EXP-SPACE-LIDAR-01` only if polar/night is in scope. |
| **kill criteria** | (i) bbp as fish/krill N without acoustic/net truth; (ii) uncorrected artifacts. |
| **readiness** | **IMPLEMENTABLE_NOW** as archive analysis. |

---

## 4. Ranked experiments (uncertainty reduction per dollar per year)

Costs are **first falsifying experiment**, not global scale-up. Scores are heuristic ranks (1 = best). Full scoring notes live in each card.

### Top 15

| Rank | Experiment ID | Hypothesis | Honest quantity | C ESTIMATE | T (y) | L | E | X | Why this rank |
|---:|---|---|---|---|---:|---:|---:|---:|---|
| 1 | `EXP-AQUA-SENTINEL-01` | H-4.10 | Farm stress covariates + private mortality/workability | \(5\times10^4\) | 0.3 | 0.15 | 0.05 | 0.05 | Highest D for recommended wedge; validatable; cheap loggers |
| 2 | `EXP-IFCB-HABON-01` | H-4.19 | HAB/phytoplankton cell time series | \(2\times10^4\) reuse | 0.25 | 0.05 | 0.05 | 0.05 | Operational biology; free-ish reuse |
| 3 | `EXP-PACE-PFT-01` | H-4.20 | PFT/optical niche vs IFCB/HPLC | \(2\times10^4\) | 0.4 | 0.05 | 0.00 | 0.10 | Cheap; X penalty if anyone says “fish” |
| 4 | `EXP-CMEMS-DA-01` | H-4.4 | BGC twin skill vs hold-out Argo | \(2\times10^4\) | 0.4 | 0.05 | 0.00 | 0.10 | Priors, not life |
| 5 | `EXP-ANIBOS-TS-01` | H-4.15 | Animal CTD T/S vs independent profiles / lobster bottom-T gap | \(2\times10^4\) | 0.3 | 0.10 | 0.00* | 0.05 | *no new tagging |
| 6 | `EXP-SOUND-HMD-01` | H-4.8 | Calibrated soundscape metrics as context | \(2\times10^4\) | 0.3 | 0.25 | 0.05 | 0.10 | L penalty for mammal detections |
| 7 | `EXP-CONNECT-01` | H-4.5 | Larval connectivity vs genetic/otolith | \(1\times10^5\) | 0.7 | 0.15 | 0.05 | 0.10 | Needs samples |
| 8 | `EXP-FERRY-EDNA-01` | H-4.16 | Route occupancy vs IFCB/microscopy | \(2\times10^5\) | 0.6 | 0.10 | 0.05 | 0.10 | Partnership latency |
| 9 | `EXP-EDNA-PAIRED-01` | H-4.1 | Occupancy vs nets (not N) | \(1.5\times10^5\) | 0.6 | 0.15 | 0.05 | 0.15 | X if quantification creeps |
| 10 | `EXP-SONAR-EDGE-01` | H-4.2 | Edge NASC vs survey | \(1.5\times10^5\) | 0.6 | 0.35 | 0.10 | 0.15 | Privacy penalty |
| 11 | `EXP-GEAR-SST-01` | H-4.9 | Gear T/effort vs loggers/logbooks | \(8\times10^4\) | 0.5 | 0.40 | 0.10 | 0.15 | GPS leakage risk |
| 12 | `EXP-INTAKE-EDNA-01` | H-4.18 | Intake occupancy vs nets | \(1\times10^5\) | 0.6 | 0.20 | 0.05 | 0.15 | Access risk |
| 13 | `EXP-GSI-CHINOOK-01` | H-4.11 | Stock composition vs CWT | \(2\times10^5\) | 0.7 | 0.55 | 0.35 | 0.10 | ESA/effort-concentration penalties |
| 14 | `EXP-DAS-WHALE-01` | H-4.14 | Whale-call P/R vs hydrophone | \(1\times10^6\) | 0.8 | 0.50 | 0.05 | 0.10 | Cost + listed-species L |
| 15 | `EXP-LIDAR-SCHOOL-01` | H-4.17 | Airborne lidar vs EK80 | \(5\times10^5\) | 0.8 | 0.45 | 0.10 | 0.15 | Weather, spots, off-wedge |

**Not ranked in top 15 (low S or kill):** foundation life maps; public marketplace SKUs of catch; EM IoT mesh; satellite school ID; coupled planetary tagging; bioluminescence-from-ocean-color as biomass; fish-from-DAS.

### Return top 10 experiments

1. `EXP-AQUA-SENTINEL-01` — farm sentinel loggers + private outcomes  
2. `EXP-IFCB-HABON-01` — reuse IFCB/HABON as biological GT  
3. `EXP-PACE-PFT-01` — PACE PFT vs IFCB/HPLC (habitat prior only)  
4. `EXP-CMEMS-DA-01` — digital-twin BGC skill, no animals  
5. `EXP-ANIBOS-TS-01` — MEOP/AniBOS T/S prior  
6. `EXP-SOUND-HMD-01` — NCEI soundscape fingerprints as context  
7. `EXP-CONNECT-01` — larval fluid-dynamics vs genetic assignment  
8. `EXP-FERRY-EDNA-01` — one SOOP molecular route  
9. `EXP-EDNA-PAIRED-01` — coastal eDNA occupancy, not abundance  
10. `EXP-SONAR-EDGE-01` — privacy-preserving edge NASC on 1–3 vessels  

---

## 5. Hypotheses / variants to **kill now**

Kill means **do not fund, do not put in product copy, do not keep as a live scientific claim**. Keep the parent hypothesis only if a weaker honest variant survives.

| ID | Kill target | Reason |
|---|---|---|
| `H-4.3` variant | Confident marine-life maps in sparse cells | Not a measurement; fails uncertainty policy; \(X \approx 1\) |
| `H-4.13` variant | Marketplace for catch spots, farm yields, listed-species locations | Legal/privacy/ecological harm; FishAI NEVER_PUBLISH |
| `H-4.17` variant | Satellite (PACE/PRISMA) detection of individual fish schools | Resolution/physics unsupported |
| `H-4.6` variant | Long-range underwater EM/RF mesh | Skin-depth physics |
| `H-4.1` variant | Global eDNA as quantitative abundance / 24–72 h counts | Decay, transport, shedding unidentified |
| `H-4.2` variant | Public cooperative sonar as fish-finder; AIS-as-fish | Category error + privacy |
| `H-4.14` variant | DAS as general fish census | Frequency/coupling unsupported |
| `H-4.7` variant | Ocean-color “bioluminescence field” as biomass | Different physical quantity |
| `H-4.9` variant | Gear/AIS density = stock N | Forbidden in project_state |
| `H-4.12` as 2026 product | Planetary coupled food-web telemetry | Cost, permits, unvalidatable at that scale |
| `H-4.4` variant | Fish abundance digital twin without biological DA | Unvalidatable claim |

**Do not kill** (honest cores remain live): regional eDNA occupancy; private edge acoustics; vision FM with abstention; CMEMS/DTO as **physical/BGC** twin; larval particle tracking; PAM fingerprints; smart gear as **effort/T**; aquaculture sentinels; Chinook GSI **composition**; DAS **whale** research; AniBOS T/S; FerryBox molecular; airborne lidar in clear water; intake eDNA; IFCB; PACE PFT; space lidar bbp.

---

## 6. Implementable **with partners this year** (2026–early 2027)

Assuming DUAs, no ingestion until DATA_RIGHTS approval, no advanced ML until gates.

| Hypothesis | 2026 partner move | Blocker if missing |
|---|---|---|
| **H-4.10** | 5–15 WA (or FARMS) growers, loggers, 72 h protocol | Outcome logs; food-safety wall |
| **H-4.19** | HABON/IFCB/SoundToxins data-use review | License |
| **H-4.20 / 4.21** | NASA matchups, no partner animals needed | Claim discipline |
| **H-4.4** | CMEMS/EDITO account, hold-out protocol | Treating twin as fish |
| **H-4.15** | MEOP download for bottom-T prior | QC in region |
| **H-4.8** | NCEI PAM products, coarsened mammal presence | Raw audio / tracks |
| **H-4.5** | OpenDrift + published atlas on one estuary | Validation tissue/drifters |
| **H-4.9** | 1–N smart buoys on consenting gear, T/effort only | GPS leakage |
| **H-4.2** | 1 research or pelagic vessel, Krillscan/Echopype edge features | Calibration + DUA |
| **H-4.16** | One ferry/SOOP operator | Ship access |
| **H-4.1** | Occupancy grid with university lab | Not a mesh yet |
| **H-4.11** | Only if Chinook wedge + tissue authority | ESA maps |
| **H-4.18** | One hatchery/plant intake | Critical-infrastructure access |
| **H-4.14** | Only if a cable owner is already in conversation | Unlikely in 2026 remaining days without an existing relationship |

**Not this year as observatory builds:** global eDNA mesh, fish DA twin, IoUT mesh, airborne school lidar (unless a pelagic partner funds it), coupled tagging fleet, planetary marketplace liquidity.

---

## 7. Cross-walk to FishAI unresolved wedge

| If founder locks… | Raise | Do not raise |
|---|---|---|
| W1 oyster WA | H-4.10, H-4.5 (larvae, not 72 h adults), H-4.19/4.20 (HAB/food, not legality), H-4.18 hatchery intake | Chinook GSI maps, whale DAS public, sonar fish-finder |
| W2 Chinook charter | H-4.11 composition **private**, H-4.8 context, H-4.20 optical niche as **weak prior** | 48 h SDM from PACE, ESU pins, AIS |
| W3 lobster GOM | H-4.9 effort/T, H-4.15 bottom T, H-4.2 only if calibrated + private | CPUE heatmaps, whale-from-DAS in UX, AIS abundance |

---

## 8. Agent limitations

- No datasets ingested; no new field work; no TRL certificates from NASA for these systems.
- Costs and TRLs marked ESTIMATE.
- “Beyond standard methods” does not mean “better than surveys.” Surveys remain the abundance gold standard where they exist (e.g. ASMFC lobster, PFMC salmon).
- Parent agents must not cite this registry as evidence that FishAI can observe global ocean life.

**Handoff:** `artifacts/hypotheses/agent_handoff.md`
