# EMIV acceptance gate

**EMIV set:** v0.1  
**Registry:** v0.1-draft  
**Date:** 2026-09-18  
**Rule:** the platform is organized around EMIVs, not around APIs.

A source, sensor, model field, or engineered feature that **maps to no EMIV** and has **no validated unique decision value** is **deferred or rejected**. It does not enter the feature store, the twin state, training labels, or user-facing copy.

---

## 1. Gate outcome vocabulary

| Outcome | Meaning | What may happen next |
| --- | --- | --- |
| **ADMIT** | Maps to exactly one primary EMIV in [`emiv_registry.csv`](emiv_registry.csv); rights/privacy/QC tickets opened | Column may be *designed* (still no ingest in this program) |
| **ADMIT_PROXY** | Maps to a `W1_PROXY` or to `valid_proxy_methods` of a core EMIV; mismatch documented | May enter only with `proxy_mismatch` metadata; cannot be the label |
| **DEFER** | Measurand is plausible but blocked (rights UNKNOWN, privacy, wrong horizon, no protocol, registrar queue) | Stay out of v0 feature store; may propose a new EMIV rather than sneak a column |
| **REJECT** | Wrong measurand, unsafe publish, legal impersonation, or abundance-proxy abuse | Do not build; do not “just use it as context” in the same slot as the label |
| **REJECT_AS_ABUNDANCE_PROXY** | Attempt to treat SST, AIS, chlorophyll, ocean color, habitat suitability, or vessel density as taxon **N** | Maps to `EMIV-BIO-SSTN-001` / `AISN` / `CHLN` — dead ends |

Default when unsure: **DEFER**. UNKNOWN is a valid, high-quality output.

---

## 2. Questions (all must be answered in writing)

Evaluate **intent + what a user could do with the field**, not the vendor’s layer name.

1. **Measurand.** What physical, biogeochemical, biological, ecosystem, human-pressure, or quality quantity is actually measured or derived?
2. **Primary EMIV.** Which `variable_id`? If none, stop — do not skip to “it might help the model.”
3. **Claim-class (category C).** Direct count vs survey index vs CPUE vs suitability vs occupancy vs telemetry individual vs range envelope? If the source does not say, you may not upgrade it.
4. **Decision value.** For which locked (or candidate) decision is this required? If the only pitch is “fish map,” fail.
5. **Unique decision value exception.** Only if (2) is none: is there a documented operator decision that **cannot** be served by any existing EMIV, with a named user, geography, horizon, and label? If yes, file a **new-EMIV proposal** (defer until ID issued). If no → **DEFER/REJECT**.
6. **Proxy mismatch.** If using `valid_proxy_methods`, is the mismatch stated (skin vs bulk vs air; surface vs bottom; Hood Canal vs Willapa)?
7. **Label vs constraint vs covariate.** Which one? Mixing them is a reject for that slot (W1: DOH is constraint, farm logs are label).
8. **Privacy.** Would native grain be `NEVER_PUBLISH` under [`../sensitive_location_policy.md`](../sensitive_location_policy.md)? If yes, do not recommend a public EMIV product at that grain.
9. **Rights.** Is commercial use `YES` on an official page for the intended use? If `UNKNOWN`, DEFER paid/redistributed use.
10. **As-of / QC.** Can `EMIV-QUA-FRESH-001` and `EMIV-QUA-QFLAG-001` be populated? If the product leaks future or has no flags, DEFER.
11. **Impersonation.** Would copy be readable as harvest authorization, food-safe, navigation-safe, or catch guarantee? If yes, REJECT that use even if the EMIV itself is valid.
12. **Validation honesty.** `validation_status` stays `UNVALIDATED` / `PROTOCOL_ONLY` / `LITERATURE` until prospective skill exists. No silent `OPERATIONAL`.

---

## 3. Unique decision value (narrow exception)

**Unique decision value** means: a competent operator would change a recurring action using this quantity, **and** no existing EMIV already represents it, **and** the label is not abundance-by-proxy.

Examples that **pass the spirit** (and already have EMIVs in v0.1):

- Intertidal emersion hours on a named culture elevation → `EMIV-PHY-EMERS-001`
- Partner 72 h mortality/workability/intervention → `EMIV-ECO-OPSOUT-001`
- Detection probability → `EMIV-QUA-PDETECT-001`

Examples that **fail** (no exception):

- “AIS heatmap so we know where the fish are”
- “MUR SST as Chinook abundance”
- “Chlorophyll as lobster”
- “WA DOH closure as oyster kill”
- “Global Fishing Watch as biomass”
- “Suitability score as a count”
- “eDNA reads as N”
- An undocumented satellite index whose only justification is that the API is free

If someone needs a new variable, they propose a new `EMIV-*` ID. They do **not** hang a rogue column off Copernicus because the NetCDF is convenient.

---

## 4. Automatic rejects (abundance and label abuse)

| Incoming use | Gate | Maps to |
| --- | --- | --- |
| SST / thetao / MUR / GHRSST **as fish/shellfish/lobster abundance** | `REJECT_AS_ABUNDANCE_PROXY` | `EMIV-BIO-SSTN-001` (use `EMIV-PHY-SST-001` instead) |
| AIS / VMS / GFW / vessel density **as abundance** | `REJECT_AS_ABUNDANCE_PROXY` | `EMIV-BIO-AISN-001` |
| Chlorophyll / ocean color / CMEMS chl **as animal abundance** | `REJECT_AS_ABUNDANCE_PROXY` | `EMIV-BIO-CHLN-001` |
| Habitat suitability / SDM **as current N or presence** | `REJECT` | Keep as `EMIV-BIO-SUIT-001` only |
| eDNA detections **as live GPS or census** | `REJECT` | `EMIV-BIO-EDNA-001` occupancy only |
| Uncalibrated NASC / DAS strain **as biomass** | `REJECT` | Not `EMIV-BIO-BIOM-001` |
| WA DOH / NSSP class **as `ops_disruption_72h`** | `REJECT` | `EMIV-HUM-HARV-001` constraint only |
| Official closure **as wild abundance** | `REJECT` | Constraint, not `BIO-ABUND` |
| Moon phase as independent W1 72 h driver | `REJECT` | Tide already in `EMIV-PHY-TIDE-001` |
| Public native spawning/nest/telemetry grain | `REJECT` (publish) | `EMIV-ECO-SPAWN-001` / `EMIV-BIO-BEHAV-001` withhold |

---

## 5. Automatic defers (v0.1)

| Case | Why |
| --- | --- |
| Licence `UNKNOWN` for intended commercial use (many IOOS/state portals; LiveOcean) | Rights agent |
| GFW / NC layers | Do not ingest |
| Confidential VTR / LEEDS / raw RecFIN interviews | Lawful only under DUA; not public GT |
| OsHV-1 as WA 72 h driver | Literature: not detected at OR/WA sentinels 2020 (`EMIV-ECO-DIS-001` is `DEFERRED`) |
| Predator maps of protected mammals | Privacy + unobserved at horizon (`EMIV-ECO-PRED-001` `DEFERRED`) |
| Food-web-as-a-service | Wrong timescale (`EMIV-ECO-FOODWEB-001` `DEFERRED`) |
| AIS as W1/W2/W3 v0 feature | Privacy, incomplete carriage (`EMIV-HUM-AIS-001` `DEFERRED`) |
| Pathogen/vibrio as product | Food-safety impersonation wall; not in v0.1 as a headline EMIV |

---

## 6. Admit checklist (minimum)

A proposed column is **ADMIT** only if the crosswalk row contains:

- `source_id` / product ID  
- `primary_emiv_id`  
- `role` ∈ {`label`, `covariate`, `constraint`, `quality`, `proxy`}  
- `claim_class` (required if category C or if anyone might read it as biology)  
- `privacy_tier`  
- `rights_status`  
- `as_of_available`  
- `gate_outcome`  
- `notes` including mismatch and “explicitly not …”  

Template: [`source_to_emiv_crosswalk.md`](source_to_emiv_crosswalk.md).

---

## 7. W1 (Willapa oyster 72 h ops-risk) bindings

See [`w1_priority_emivs.md`](w1_priority_emivs.md).

| Slot | EMIV | Fail if… |
| --- | --- | --- |
| Label | `EMIV-ECO-OPSOUT-001` | DOH closures, WAHH volume, SST, chl used as `y` |
| Constraint (must-show) | `EMIV-HUM-HARV-001` | Copy sounds like NSSP authorization |
| Core covariates | ATEMP, TIDE, EMERS, WTEMP-001, DOXY, SALIN, WAVE, WIND | SST-only stack; missing emersion class |
| Proxy | SST, RUNOFF | Proxy presented as core truth |
| Quality | FRESH, QFLAG, CALIB, DCOV | Future leakage; SST filling DO |

**If no partner logs exist, the W1 label EMIV is unidentified.** Physics APIs do not close the gate.

---

## 8. Registrar one-liner

**No EMIV + no validated unique decision value → defer/reject.**  
**SST/AIS/chlorophyll as fish → reject.**  
**DOH closure as mortality → reject.**
