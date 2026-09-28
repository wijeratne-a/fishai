# Agent handoff — HYPOTHETICAL_TECHNOLOGY_AGENT

**Project:** Global Saltwater Life Observatory / Ocean Intelligence Builder (FishAI working name)  
**Date:** 2026-09-18  
**Access date for URLs:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/` only  
**Wedge status:** UNRESOLVED. Nothing here locks W1/W2/W3 or authorizes ingestion or product ML.

**Non-negotiables observed:** no abundance from SST/AIS/chlorophyll/uncalibrated eDNA; no manufactured confidence in sparse cells; no public catch/farm/listed-species pins; no food-safety or harvest authorization; costs and TRLs labeled **ESTIMATE** unless an operational system is obviously TRL 9; unproven methods are not claimed to work.

---

## 1. Executive finding (return block)

### Ranked top 10 experiments

Ranked by expected **biological uncertainty reduction per dollar per year**, after penalties for legal/privacy harm, ecological harm, and unvalidatable claims. Formula in `hypothesis_registry.md` §1. These are **first falsifying experiments**, not global deployments.

| Rank | ID | Honest quantity | Why it wins U/$/y |
|---:|---|---|---|
| 1 | `EXP-AQUA-SENTINEL-01` | 24–72 h farm **stress/workability** covariates + private outcomes | Cheap loggers, validatable, highest decision fit if oyster wedge locks |
| 2 | `EXP-IFCB-HABON-01` | Cell-resolved phytoplankton/HAB time series | Operational biology already exists; best GT backbone |
| 3 | `EXP-PACE-PFT-01` | PACE PFT / space-lidar **bbp** vs IFCB/HPLC/Argo | Free NASA data; only if never called “fish” |
| 4 | `EXP-CMEMS-DA-01` | Physics/BGC twin skill vs hold-out Argo | Consume Copernicus; do not build a fish twin |
| 5 | `EXP-ANIBOS-TS-01` | MEOP/AniBOS T/S as thermal prior | Public profiles; **no new tagging**; kill if regional n is too low |
| 6 | `EXP-SOUND-HMD-01` | Calibrated soundscape fingerprints + vocal **presence** | Archive reuse; coarsen/omit mammals |
| 7 | `EXP-CONNECT-01` | Larval/jelly **connectivity** vs genetic/spat | Mature particle tracking; not adult schools |
| 8 | `EXP-FERRY-EDNA-01` | One SOOP/FerryBox molecular transect | Ships already steam; occupancy not \(N\) |
| 9 | `EXP-EDNA-PAIRED-01` | Coastal eDNA **occupancy** vs nets | Mesh is not this experiment |
| 10 | `EXP-SONAR-EDGE-01` | Privacy-preserving edge **NASC** on 1–3 calibrated vessels | High privacy penalty; still better U/$ than DAS or lidar campaigns |

**Not in the top 10 (still live as bounded science):** smart-gear SST/effort, intake eDNA, Chinook GSI composition (heavy ESA penalty), DAS whales, airborne lidar schools, vision-FM **abstention** test, marketplace **tabletop**.

### Hypotheses / variants to **kill now**

Kill means do not fund, do not put in product copy, do not keep as a live measurement claim. Honest parent hypotheses may survive.

1. **Sparse-cell foundation-model life maps with High confidence** (`H-4.3` variant) — not a measurement.  
2. **Marketplace for catch spots, farm yields, or listed-species locations** (`H-4.13` variant).  
3. **Satellite detection of individual fish schools** (`H-4.17` PACE/PRISMA variant) — pixel scale vs school scale.  
4. **Long-range underwater EM/RF mesh** (`H-4.6` variant) — seawater skin depth.  
5. **Global eDNA as quantitative abundance / 24–72 h counts** (`H-4.1` variant).  
6. **Public cooperative sonar or AIS as fish** (`H-4.2` variant).  
7. **DAS as a general fish census** (`H-4.14` variant).  
8. **Ocean color as a bioluminescence biomass field** (`H-4.7` variant).  
9. **Smart-gear / AIS density as stock \(N\)** (`H-4.9` variant; already rejected in `project_state.json`).  
10. **Planetary coupled predator–prey telemetry as a 2026 product** (`H-4.12` as ops).  
11. **Fish-abundance digital twin without biological assimilation** (`H-4.4` variant).

### Implementable **with partners this year** (remainder of 2026 into early 2027)

Physics/kits exist; DUAs, DATA_RIGHTS approval, and claim discipline are the gates. No ingestion until rights review.

| Ready with partners | What “this year” actually means |
|---|---|
| **H-4.10** aquaculture sentinels | 5–15 consenting growers, loggers, 72 h air×tide vs SST-only |
| **H-4.19** IFCB/HABON | License review + reuse as GT |
| **H-4.20 / H-4.21** PACE + space lidar | Matchups; no animal partner required |
| **H-4.4** DTO/CMEMS | Consume BGC/physics; do not emit animals |
| **H-4.15** AniBOS/MEOP | Download T/S; no new tags |
| **H-4.8** soundscapes | NCEI/SanctSound products, coarsened |
| **H-4.5** connectivity | OpenDrift/atlas + one estuary’s validation samples |
| **H-4.9** smart gear | SST/soak **for the owner**; coarsened science SKU only after privacy test |
| **H-4.2** sonar cooperative | 1–3 **calibrated** vessels, delayed features |
| **H-4.16** FerryBox molecular | One operator, two seasons |
| **H-4.1** eDNA | Occupancy grid, not a global mesh |
| **H-4.11** GSI | Only if Chinook wedge + lawful tissue; **no maps** |
| **H-4.18** intake eDNA | One hatchery/plant |
| **H-4.13** marketplace | Legal tabletop + dummy SKU only |
| **H-4.3** FM | Evaluation of abstention on open weights — **not** a customer model |

**Not this year as builds:** global eDNA mesh, fish DA twin, IoUT mesh, airborne school lidar (unless a pelagic program funds it), DAS without an existing cable relationship, coupled tagging fleet.

---

## 2. Evidence table

| Claim | Finding | Evidence | Implication |
|---|---|---|---|
| Global eDNA mesh is ready | **No.** Labs and some autonomous samplers exist; decay/transport unidentified for \(N\) | OBON; Sassoubre 2016; *Carcinus* eDNA≠biomass | Occupancy yes; abundance no |
| Vessel acoustics can be shared | Processed products yes; fishers require delay/anonymity | ICES GAIN; Krillscan; Marine Policy 2025 | Partnership + privacy architecture |
| Marine FMs census the ocean | Vision ID is advancing; maps in empty cells are priors | MarineInst; BioCLIP 2; NicheFlow is reptiles | Abstention test or kill |
| Digital twins include marine life | EU DTO/CMEMS are physics/BGC | EDITO 2024–25; MedBFM DA | Priors for habitat, not fish DA |
| Larvae follow fluids | Particle tracking mature; skill is local | Scientific Data 2025 atlas; OpenDrift | Validate per estuary |
| Underwater EM mesh | Physically attenuated | 2025 multimodal UWC review | Kill EM long-range |
| Bioluminescence maps fishes | In situ photon sensors exist; satellite is not flashes | BIOLUMOPS; Biosealight | Research, not v0 |
| Sound fingerprints all life | HMD comparable; silent taxa invisible | SanctSound; NCEI; SoundCoop | Context layer |
| Smart gear = abundance | Measures effort/T/motion | Blue Ocean Gear; EM TM | Category C only |
| Farms as sentinels | FARMS/NANOOS-class already operate | UF/IFAS FARMS 2025–26 | Top-ranked experiment |
| GSI engine | Chinook baselines strong | Van Doornik 2024; PBT+GSI BC | Mix, not maps |
| Coupled predator–prey observatory | Anecdotes and diet electivity; not an observatory | Bluefin–orca; albacore traits | Desktop first |
| Observation marketplace | Portals exist; spot markets must not | EMODnet; GFW NC | Boring SKUs only |
| DAS | Baleen yes; fish no | Svalbard/Oregon/Australia 2022–25 | Partnership, NEVER_PUBLISH |
| AniBOS | CTD profiles operational | MEOP 872k profiles | Thermal prior |
| FerryBox molecular | 2023–24 demos | JERICO WASP | One route |
| Satellite schools | Unsupported at ~1 km | PACE OCI spec | Kill; keep PFT prior |
| IFCB | Operational HAB imaging | HABON-NE | Rank 2 |

---

## 3. Source / license table (indicative, not DATA_RIGHTS approval)

No datasets ingested.

| Source | URL | Use | License note |
|---|---|---|---|
| NASA TRL | https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/ ; https://esto.nasa.gov/trl/ | TRL language | Public |
| OBON | https://obon-ocean.org/ | eDNA programme | Programme pages |
| CMEMS / EDITO / EMODnet | marine.copernicus.eu ; emodnet.ec.europa.eu ToU | Twin priors | Products often CC BY 4.0; **sources may differ** |
| GFW | CC BY-NC API terms | Negative control (not fish) | **Non-commercial**; not an abundance SKU |
| NCEI PAM / SanctSound / OBIS | ncei.noaa.gov ; obis.org dataset 7a4427f6-… | Soundscapes | Raw audio may be restricted |
| MEOP | http://meop.net/database/meop-databases/meop-ctd-database.html | Animal CTD | Access form; cite |
| PACE / CALIOP bbp | pace.oceansciences.org ; earthdata.nasa.gov | Optical/lidar priors | NASA public |
| Chinook GSI baseline | doi:10.1002/nafm.11019 ; Dryad dz08kps5b | Stock ID | Paper/data licenses |
| FARMS / HABON-NE / IFCB dashboard | shellfish.ifas.ufl.edu/farms-2023/ ; northeasthab.whoi.edu ; habon-ifcb.whoi.edu | Sentinels / GT | Confirm before reuse |
| ICES GAIN | github.com/ices-eg/wk_WKGAIN | Acoustic sharing | Community conventions |

**HUMAN LEGAL REVIEW** before any access beyond citation.

---

## 4. Confidence / limitations of this dossier

| Area | Confidence | Limitation |
|---|---|---|
| Category errors (SST/AIS/eDNA-as-\(N\), sparse-cell FM) | **High** | Physics and project non-negotiables |
| Rank order of top ~5 experiments | **Medium–high** | Heuristic \(S\); costs ESTIMATE |
| Exact TRLs | **Low** unless TRL 9 operational | Agent ESTIMATE; NASA did not rate these systems |
| 2026 partner availability | **Low** | No interviews; no signed DUAs |
| Willapa IFCB existence | **Unknown** | HABON is New England-heavy |
| MEOP overlap with GOM lobster | **Likely low** | Coverage fail is a kill, not an interpolation excuse |
| This agent as domain sign-off | **Invalid** | Not a human reviewer |

**Did not do:** ingest data, contact cable owners, fly lidar, train models, lock a wedge.

---

## 5. Recommended decision

1. Treat the observatory as a **network of bounded, validatable measurements** with abstention — not an AI globe of life.  
2. If the founder later locks **W1 oysters**, fund rank 1 (farm sentinels) immediately after DUA; use PACE/IFCB only as HAB/food **context**, never legality.  
3. If **W3 lobster**, prioritize AniBOS/eMOLT-class **bottom T** and private smart-gear effort — never AIS.  
4. If **W2 Chinook**, GSI composition is scientifically ready and **ethically expensive**; do not ship encounter heatmaps.  
5. Keep CMEMS/DTO as the physical twin; **kill** the fish-twin slogan.  
6. Re-run DATA_RIGHTS on every URL before access.

---

## 6. Rejected alternatives

See kill list in §1. Additional rejects: HiveClaw/Atlas as ocean sensors; social-media bite reports; moon-phase lobster v1; using WA DOH closures as oyster-stress labels (already red-teamed).

---

## 7. Follow-ups

1. Founder wedge lock (still blocking).  
2. Rights agent: NANOOS, HABON, MEOP, NCEI PAM, CMEMS.  
3. If W1: design-partner farms for `EXP-AQUA-SENTINEL-01`.  
4. Independent red team of this registry against `prediction_contract.md` (sparse-cell language).  
5. Do not start `EXP-DAS-WHALE-01` or `EXP-LIDAR-SCHOOL-01` without a named funder outside the 24–72 h operator brief.

---

## 8. Artifacts produced

All under `/Users/wijeratne/dev/fishai/observatory/`:

| File | Role |
|---|---|
| `hypothesis_registry.md` | 4.1–4.13 + eight originals (4.14–4.21), required fields, ranking, kills |
| `hypothesis_experiment_cards/` | 21 cards (H-4.1 … H-4.21) |
| `technology_readiness_matrix.csv` | Readiness, TRL ESTIMATE, penalties, 2026 flags |
| `artifacts/hypotheses/agent_handoff.md` | This file |

---

## 9. Residual questions for humans

- Is a 72 h oyster rule still needed vs grower checklists (red-team leftover)?  
- Which ferry, hatchery, or calibrated fishing vessel would actually sign in 2026?  
- Does any Willapa/Puget partner already run IFCB, or is New England GT only a PACE matchup?  
- Cable DAS: is there a pre-existing landing relationship? If not, drop from 2026.  
- Counsel: coarsened NASC + AIS reverse-engineering — pass/fail design.

---

## 10. Next experiment (smallest falsifying test)

**Do not train a neural ocean-life model.**

**Default (wedge still unresolved, highest S):** `EXP-AQUA-SENTINEL-01` on one consenting lease cluster — pre-registered 72 h air×tide×wave rule vs persistence vs SST-only, private outcomes, DOH as a **separate** official feed.

**In parallel, zero-partner biology:** `EXP-PACE-PFT-01` + `EXP-IFCB-HABON-01` matchups, labeled habitat/cells not fish.

**Stop** if either experiment needs public hotspots, AIS-as-fish, eDNA-as-\(N\), or High confidence in empty cells.

---

**Handoff complete.** Parent return payload is §1: top 10 experiments; kill-now variants; 2026 partner-implementable set.
