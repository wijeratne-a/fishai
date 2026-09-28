# Agent handoff — Essential Marine Intelligence Variables (EMIV) registrar

**Date:** 2026-09-18  
**From:** EMIV registrar (this agent)  
**To:** Orchestrator; observatory architecture / DA; marine domain; data discovery; data rights; validation / red team; geospatial; product (read-only)  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/emiv/` only  
**Did not write:** `fishai/globe/**`, `fishai/artifacts/integration/**`, `project_state.json`, commercial `artifacts/**`  
**Did not ingest:** any dataset  

**EMIV set version:** `v0.1`  
**Registry artifact:** `v0.1-draft`

---

## 1. Executive finding

Organize FishAI / the Global Saltwater Life Observatory around a **versioned EMIV registry**, not around whichever ocean API is easiest. A source, sensor, or feature that **maps to no EMIV** and has **no validated unique decision value** is **deferred or rejected**.

v0.1 is a complete-but-not-bloated set: **84 rows** covering physical, BGC, biodiversity (with claim-class), ecosystem, human pressure, and observation quality. FishAI EMIVs are a **superset** of GOOS EOVs, GEO BON EBVs, and NOAA IOOS core variables (air temperature, emersion, incoming solar during emersion, tissue/bag T, farm ops outcome, harvest-open constraint, quality meta-variables) and **every row is crosswalked** (match, derived-from, or explicit superset). Official URLs are in `README.md`.

**Nothing is OPERATIONAL** (`validation_status=OPERATIONAL` count = **0**). W1 physics is `LITERATURE` / `PROTOCOL_ONLY`. The W1 label (`EMIV-ECO-OPSOUT-001`) is `UNVALIDATED` because partner logs do not exist in this program.

**W1_CORE (10):** air T, tide, emersion, incoming solar, bulk water T, DO, salinity, waves, wind, farm operational outcome.  
**Tissue/bag T** (`EMIV-PHY-TISST-001`) is CANDIDATE with high decision value; W1_CORE when a partner sensor exists.  
**WA DOH closure is not the ops label** (`EMIV-HUM-HARV-001` constraint).  
**SST is a proxy with mismatch** (`EMIV-PHY-SST-001`, `W1_PROXY`).  
**AIS is human pressure, not abundance** (`EMIV-HUM-AIS-001` DEFERRED; `EMIV-BIO-AISN-001` rejected mapping).

Native-grain fishing effort, telemetry movement, spawning habitat, and rare occurrence are **high sensitivity**. This registrar does **not** recommend publishing EMIVs that `sensitive_location_policy.md` marks `NEVER_PUBLISH`.

---

## 2. Return block (requested)

### Row count

**84** rows in `observatory/emiv/emiv_registry.csv` (all required fields present; 0 empty cells).

| Category | n |
| --- | ---: |
| A PHYSICAL | 19 |
| B BGC | 12 |
| C BIODIVERSITY (incl. 3 rejected mappings) | 17 |
| D ECOSYSTEM | 13 |
| E HUMAN PRESSURE | 13 |
| F OBSERVATION QUALITY | 10 |

`model_use_status`: CANDIDATE 65 · W1_CORE 10 · DEFERRED 4 · REJECTED_AS_ABUNDANCE_PROXY 3 · W1_PROXY 2.

### W1_CORE list

1. `EMIV-PHY-ATEMP-001` — Near-surface air temperature  
2. `EMIV-PHY-TIDE-001` — Tide stage / water level  
3. `EMIV-PHY-EMERS-001` — Intertidal emersion duration and timing  
4. `EMIV-PHY-SOLAR-001` — Incoming solar / insolation during emersion  
5. `EMIV-PHY-WTEMP-001` — Near-surface bulk water temperature  
6. `EMIV-BGC-DOXY-001` — Dissolved oxygen  
7. `EMIV-PHY-SALIN-001` — Practical salinity  
8. `EMIV-PHY-WAVE-001` — Sea state / waves  
9. `EMIV-PHY-WIND-001` — Surface wind  
10. `EMIV-ECO-OPSOUT-001` — Aquaculture operational outcome (mortality, workability, intervention)

High-value CANDIDATE (W1_CORE when partner sensor exists): `EMIV-PHY-TISST-001` — Tissue or bag/bed thermistor temperature.  
Required metadata (not separately W1_CORE): `EMIV-HUM-CULT-001`.  
Must-show constraint (not label): `EMIV-HUM-HARV-001`.  
W1_PROXY: `EMIV-PHY-SST-001`, `EMIV-BGC-RUNOFF-001`.

### Popular ocean APIs that **fail the EMIV gate if used as fish abundance**

These APIs can **ADMIT** as physics, BGC, pressure, or occurrence compilations. They **fail** (`REJECT_AS_ABUNDANCE_PROXY` or `REJECT`) when the intended use is taxon **N** / “where the fish are”:

| API / product class | Valid EMIV mapping | Fail-as-abundance ID |
| --- | --- | --- |
| **Copernicus Marine** PHY `thetao` / SST | `EMIV-PHY-SST-001`, `EMIV-PHY-WTEMP-*` | `EMIV-BIO-SSTN-001` |
| **Copernicus Marine** BGC `chl` | `EMIV-BGC-CHL-001` | `EMIV-BIO-CHLN-001` |
| **MUR / GHRSST / NOAA CoastWatch SST** | `EMIV-PHY-SST-001` | `EMIV-BIO-SSTN-001` |
| **VIIRS / OLCI / PACE ocean color** | `EMIV-BGC-CHL-001`, `EMIV-PHY-LIGHT-001` | `EMIV-BIO-CHLN-001` |
| **NDBC / CDIP** metocean | `EMIV-PHY-WIND/WAVE/ATEMP/WTEMP` | any BIO-ABUND use |
| **NANOOS ORCA / NERRS** in situ | `EMIV-PHY-WTEMP/SALIN`, `EMIV-BGC-DOXY` | BIO-ABUND; also not Willapa GT |
| **WCOFS / GoMOFS / RTOFS / CMEMS 3-D T/S/u/v** | PHY currents/T/S (MODEL-INFERRED) | BIO-ABUND |
| **AIS / MarineCadastre / GFW fishing hours** | `EMIV-HUM-AIS-001` / `FISH-001` (GFW: do not ingest, NC) | `EMIV-BIO-AISN-001` |
| **HF radar surface currents** | `EMIV-PHY-CURR-001` | BIO-ABUND |
| **WA DOH closures** | `EMIV-HUM-HARV-001` constraint | abundance **and** ops-mortality label |
| **OBIS / GBIF** (bonus: not abundance census) | `EMIV-BIO-OCC-001` compilation | `EMIV-BIO-ABUND-001` census / live tracking |

Habitat-suitability layers fail if sold as current presence/N (`EMIV-BIO-SUIT-001` must stay suitability). eDNA APIs fail as live GPS/census (`EMIV-BIO-EDNA-001`).

---

## 3. Evidence table

| Finding | Evidence | Confidence |
| --- | --- | --- |
| Platform must be EMIV-gated | Mission; sibling red team RT-XCUT-04 (SST/AIS/chl proxy misuse) | High |
| W1 label = farm outcomes, not DOH | `artifacts/data_discovery/ground_truth_relabel_W1.md`; WAC 246-282-006 | High |
| Air × emersion, not SST, for intertidal kill | Raymond et al. 2022; marine-domain matrix C1 | High |
| SST ≠ bottom T (lobster) | ASMFC 2025 peer review (cited in marine-domain matrix) | High |
| AIS ≠ abundance | Project non-negotiable; 33 CFR 164.46 carriage; Harley et al. 2001 CPUE≠N | High |
| GOOS/EBV/IOOS URLs live | Retrieved 2026-09-18 via search: goosocean.org EOV page; geobon.org/ebvs; ioos.noaa.gov/about/ioos-by-the-numbers | High (page existence); sheet-level EOV list may evolve (GOOS cites 36 EOVs) |
| No FishAI operational EMIV | No ingest, no partner DUA, no prospective score | Certain |
| LiveOcean / many IOOS commercial terms | Discovery: UNKNOWN | High that they are UNKNOWN |

---

## 4. Source / licence (this pass)

No datasets. Citations only.

| Source | URL | Use here |
| --- | --- | --- |
| GOOS EOVs | https://goosocean.org/what-we-do/framework/essential-ocean-variables/ | Crosswalk |
| GOOS EOV sheets | https://goosocean.org/document-list/168 | Crosswalk |
| GEO BON EBVs | https://geobon.org/ebvs/what-are-ebvs/ | Crosswalk |
| NOAA IOOS core variables | https://ioos.noaa.gov/about/ioos-by-the-numbers/ | Crosswalk |
| IOOC list | https://iooc.us/task-teams/bio/ioos-core-variables | Crosswalk |
| QARTOD | https://ioos.noaa.gov/project/qartod/ | QUA methods |
| Sensitive location policy | `observatory/sensitive_location_policy.md` | Privacy field |
| Variable relevance matrix | `artifacts/marine_domain/variable_relevance_matrix.csv` | W1 ranking (read only) |
| Discovery handoff / W1 relabel | `artifacts/data_discovery/*` | Source examples (read only) |

---

## 5. Confidence and limitations

| Item | Confidence | Limitation |
| --- | --- | --- |
| 84-row coverage of required A–F bullets | High | Not encyclopedic (no ice EOV, no mangrove IOOS core, no N2O EOV) |
| W1_CORE membership | High scientifically | Wedge still UNRESOLVED commercially |
| Rejected abundance mappings | High | Vendors will still name layers “fish” |
| Numeric RMSE / QL cutoffs | Not invented | Thresholds are qualitative + provider flags |
| Human registrar sign-off | None | `v0.1-draft` |
| This agent as fisheries scientist | Not qualified | HIGH items stay open for named humans |

---

## 6. Artifacts written

| File | Contents |
| --- | --- |
| `observatory/emiv/README.md` | Versioning; source-mapping; GOOS/EBV/IOOS URLs; superset rule |
| `observatory/emiv/emiv_registry.csv` | 84 × 21 required fields |
| `observatory/emiv/emiv_catalog.md` | Human catalog A–F |
| `observatory/emiv/source_to_emiv_crosswalk.md` | Template + Copernicus SST, NDBC/ORCA, WA DOH, farm logs, AIS |
| `observatory/emiv/acceptance_gate.md` | No EMIV + no unique decision value → defer/reject |
| `observatory/emiv/w1_priority_emivs.md` | Willapa 72 h OPS-RISK bindings |
| `observatory/emiv/agent_handoff.md` | This file |

---

## 7. Follow-ups (other agents / humans)

- **Architecture / globe (in flight):** bind twin state to EMIV IDs; do not invent parallel variable lists.  
- **Data discovery:** re-tag catalog `variable_name` → `primary_emiv_id`; DOH stays constraint.  
- **Rights:** LiveOcean, NANOOS commercial, DOH export, Copernicus attribution wording.  
- **Validation:** no OPERATIONAL promotion without V1–V9 on a locked label.  
- **BD / founder:** W1 still needs grower NDAs before `EMIV-ECO-OPSOUT-001` is identifiable.  
- **Counsel:** WAC 246-282-006 copy; never impersonate NSSP.  
- **Human domain registrar:** sign `v0.1-draft` → `v0.1` or send back rows.

---

## 8. Next experiment (no ingest)

Do **not** download Copernicus/ORCA/DOH. Optional paper exercise: fill 14 days of **empty** as-of columns for one Willapa growing area with the ten W1_CORE IDs + HUM-HARV constraint, and record `UNKNOWN` where sensors do not exist (including TISST if no partner thermistor). Success = two distinct columns (constraint vs label) and SST tagged `W1_PROXY`. Failure = using ORCA as Willapa or DOH as `y`.
