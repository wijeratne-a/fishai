# Essential Marine Intelligence Variables (EMIV)

**Program:** FishAI / Global Saltwater Life Observatory  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/emiv/`  
**Date:** 2026-09-18  
**EMIV set version:** `v0.1`  
**Registry artifact:** `v0.1-draft`  
**Ingest:** none. Catalog and cite only. UNKNOWN is valid.

This folder is the **versioned variable registry** the platform is organized around. APIs, sensors, and features are admitted only if they map to an EMIV (or pass the unique-decision-value exception in [`acceptance_gate.md`](acceptance_gate.md)). Popularity of a Copernicus, NOAA, or AIS endpoint does not mint a variable.

---

## What an EMIV is

An EMIV is a **named, decision-relevant marine quantity** with a definition, unit, claim-class (for biodiversity), preferred methods, valid proxies, metadata, uncertainty practice, privacy tier, and an honest validation status.

It is **not**:

- a product SKU, heatmap, or API field;
- “the fish”;
- harvest legality or food safety (those are official constraints, mapped as human-pressure EMIVs);
- a licence to publish native-grain sensitive locations.

FishAI EMIVs **may be a superset** of GOOS Essential Ocean Variables (EOVs), GEO BON Essential Biodiversity Variables (EBVs), and NOAA IOOS core variables. Every row still **must crosswalk**: matching standard, derived-from standard, or explicit `superset` with a reason.

---

## Versioning

| Token | Meaning |
| --- | --- |
| **EMIV set `v0.1`** | The conceptual set published in this folder (categories A–F, ID scheme, gate). |
| **Registry `v0.1-draft`** | The machine table [`emiv_registry.csv`](emiv_registry.csv). Draft because no human domain registrar has signed, no ingest has occurred, and almost no row is OPERATIONAL. |
| **Crosswalk vintage** | Same date as the registry row’s source-standards note; re-verify URLs on change. |

**Rules:**

1. **IDs are stable.** `EMIV-{CAT}-{SHORT}-###` is never recycled. Rejected mappings keep their IDs (e.g. `EMIV-BIO-SSTN-001`).
2. **Additive new variables** → bump set minor (`v0.2`) after registrar review.
3. **Breaking changes** (required field added/removed, definition that changes measurand, category move) → bump set major (`v1.0`).
4. **Wording/typo/crosswalk URL** → patch on the same set version; note in `agent_handoff.md`.
5. **Sources are not versioned as EMIVs.** A new API is a crosswalk row, not a new `variable_id`, unless the measurand is actually new.
6. **`model_use_status` and `validation_status` are registrar fields**, not vendor marketing. They may change without a new ID.

This observatory iteration does **not** write `project_state.json` or globe artifacts. Commercial wedge state remains whatever the parent program recorded.

---

## Files

| File | Role |
| --- | --- |
| [`emiv_registry.csv`](emiv_registry.csv) | Canonical machine registry (`v0.1-draft`) |
| [`emiv_catalog.md`](emiv_catalog.md) | Human-readable grouped catalog (A–F) |
| [`source_to_emiv_crosswalk.md`](source_to_emiv_crosswalk.md) | How sources map in; examples |
| [`engine_id_crosswalk.md`](engine_id_crosswalk.md) | Engine stub/slug → registry ID; files touched |
| [`acceptance_gate.md`](acceptance_gate.md) | Admit / defer / reject |
| [`w1_priority_emivs.md`](w1_priority_emivs.md) | Willapa Pacific oyster 72 h OPS-RISK subset |
| [`agent_handoff.md`](agent_handoff.md) | Handoff to orchestrator and sibling agents |

---

## ID scheme

```
EMIV-{CAT}-{SHORT}-###
```

| `CAT` | Category |
| --- | --- |
| `PHY` | A PHYSICAL |
| `BGC` | B BGC |
| `BIO` | C BIODIVERSITY |
| `ECO` | D ECOSYSTEM |
| `HUM` | E HUMAN PRESSURE |
| `QUA` | F OBSERVATION QUALITY |

Examples: `EMIV-PHY-WTEMP-001`, `EMIV-PHY-ATEMP-001`, `EMIV-QUA-PDETECT-001`.

`SHORT` is a stable mnemonic, not a product name. `###` starts at `001` per short-code. `9xx` is reserved for **rejected instantiations** (wrong measurand), not for real variables.

---

## Status vocabularies (binding)

**`model_use_status`**

| Value | Meaning |
| --- | --- |
| `W1_CORE` | Required for the recommended Willapa oyster 72 h ops-risk path (still UNRESOLVED commercially). |
| `W1_PROXY` | Allowed into W1 only as a documented proxy with mismatch; cannot headline the label. |
| `CANDIDATE` | In the v0.1 set; not W1-core. May be used later if the gate and rights pass. |
| `DEFERRED` | Measurand is real but FishAI must not build on it yet (privacy, rights, wrong geography/horizon, or missing protocol). |
| `REJECTED_AS_ABUNDANCE_PROXY` | Mapping a non-abundance source to taxon abundance. Do not instantiate. |

**`validation_status`**

| Value | Meaning |
| --- | --- |
| `UNVALIDATED` | No FishAI prospective or even local scored use. Default for biology and partner labels (none ingested). |
| `PROTOCOL_ONLY` | An agency/community protocol exists (QARTOD, GHRSST, CO-OPS, NSSP lab methods). FishAI has not shown decision skill. |
| `LITERATURE` | Peer-reviewed or official mechanistic support at a relevant scale/stage; still not a FishAI operational product. |
| `OPERATIONAL` | FishAI (or a named partner protocol under DUA) has prospective, time-forward skill on the locked decision. **Count in v0.1-draft: 0.** |

Agency-operational SST or tide products remain `PROTOCOL_ONLY` here until *this* program validates them for a locked decision.

---

## How sources map in

```
source / sensor / feature
        │
        ▼
identify measurand + claim-class
        │
        ▼
crosswalk → exactly one primary EMIV
        │
        ├─ no EMIV match ──► unique decision value? ──no──► DEFER / REJECT
        │                         │ yes (documented)
        │                         └── exception ticket (rare; still not abundance)
        │
        ├─ maps to REJECTED_AS_ABUNDANCE_PROXY ──► REJECT
        │
        └─ maps to valid EMIV
                  │
                  ├─ bind privacy from observatory/sensitive_location_policy.md
                  ├─ bind rights (UNKNOWN until official page for intended use)
                  ├─ bind as-of / QC (QUA EMIVs)
                  └─ only then may a feature store column exist
```

**Rules of mapping:**

1. **One primary EMIV per source field.** Secondary EMIVs are dependencies, not aliases.
2. **Biodiversity rows must declare claim-class** in the definition: `DIRECT_COUNT` | `SURVEY_INDEX` | `CPUE` | `SUITABILITY` | `DIRECT_DETECTION` | `MOLECULAR_OCCUPANCY_INDEX` | `TELEMETRY_INDIVIDUAL` | `RANGE_ENVELOPE` | `OPERATIONALLY_OBSERVED`.
3. **Physics and BGC never become abundance** by joining a species name.
4. **Official harvest/closure → `EMIV-HUM-HARV-001`**, never `EMIV-ECO-OPSOUT-001` and never `EMIV-BIO-ABUND-*`.
5. **Partner farm mortality/workability/intervention → `EMIV-ECO-OPSOUT-001`.**
6. **AIS / GFW / vessel density → `EMIV-HUM-AIS-001` (or FISH/SHIP)** and **fail** if aimed at `EMIV-BIO-ABUND-*`.
7. Native-grain EMIVs marked `NEVER_PUBLISH` in the registry **must not be recommended for public products**. Internal ACL stores are a later engineering question, not a v0.1 publish path.

Full gate: [`acceptance_gate.md`](acceptance_gate.md). Template: [`source_to_emiv_crosswalk.md`](source_to_emiv_crosswalk.md).

---

## Relation to GOOS EOVs, GEO BON EBVs, NOAA IOOS core variables

FishAI does not replace these frameworks. It **reuses their measurands** where they exist and **adds decision/ops/quality variables** they do not cover.

### Official URLs (access date 2026-09-18)

| Framework | What to cite | URL |
| --- | --- | --- |
| **GOOS** | Programme | https://goosocean.org/ |
| **GOOS EOVs** | Definition of Essential Ocean Variables | https://goosocean.org/what-we-do/framework/essential-ocean-variables/ |
| **GOOS EOV specification sheets** | Per-variable requirements and methods | https://goosocean.org/document-list/168 |
| **GOOS BioEco metadata** | Biological/ecosystem observing inventory | https://bioeco.goosocean.org |
| **GOOS EOV status (36 EOVs)** | Programme note 2026-02-16 | https://goosocean.org/news/goos-essential-ocean-variables-paper-published/ |
| **GEO BON EBVs** | What are EBVs? (6 classes, 21 names) | https://geobon.org/ebvs/what-are-ebvs/ |
| **GEO BON** | Programme | https://geobon.org/ |
| **NOAA IOOS core variables** | Physics / BGC / biology & ecosystems list | https://ioos.noaa.gov/about/ioos-by-the-numbers/ |
| **IOOC core-variable list** | Same 34-variable list (interagency) | https://iooc.us/task-teams/bio/ioos-core-variables |
| **IOOS QARTOD** | QC manuals for many core variables | https://ioos.noaa.gov/project/qartod/ |
| **GCOS ECVs** | Atmospheric air temperature (not an ocean EOV) | https://gcos.wmo.int/en/essential-climate-variables |

GOOS currently describes EOVs as the **minimum** ocean variables needed to assess state and variability and to support societal applications. GEO BON describes EBVs as standardized biodiversity state variables bridging raw observations and indicators. IOOS lists **34 core variables** required to detect and predict changes in U.S. oceans, coasts, and Great Lakes, with biology & ecosystems **aligned with GOOS BioEco EOVs**.

### Crosswalk principle

| If the EMIV… | Then `source_standards` says… |
| --- | --- |
| **Is** an EOV/EBV/IOOS core measurand | Named standard + URL |
| **Is derived from** one (emersion from sea level; Ω from inorganic carbon; MHW from SST) | `Derived from {standard}` |
| **Has no ocean standard** but is required for a locked decision (air T, farm ops outcome, harvest-open constraint, detection probability) | `Superset; no EOV/EBV; reason` plus the nearest GCOS/IOOS analogue if any |

### Superset (FishAI-only or decision-only) — still crosswalked

These are in `v0.1` **on purpose**. They are why the platform cannot be “just Copernicus + OBIS”:

- **Air temperature** (`EMIV-PHY-ATEMP-001`) — GCOS atmospheric ECV; not a GOOS EOV. First-order for intertidal heat-kill.
- **Incoming solar / insolation during emersion** (`EMIV-PHY-SOLAR-001`) — GCOS surface radiation / incoming shortwave; not chlorophyll; not underwater PAR.
- **Tissue or bag/bed thermistor temperature** (`EMIV-PHY-TISST-001`) — no ocean EOV; organism/gear thermal state; not SST.
- **Intertidal emersion** (`EMIV-PHY-EMERS-001`) — derived from sea-level EOV + operator elevation.
- **Culture method** (`EMIV-HUM-CULT-001`) — aquaculture metadata.
- **Farm operational outcome** (`EMIV-ECO-OPSOUT-001`) — ops label; not wild GOOS Fish EOV.
- **Official harvest/closure** (`EMIV-HUM-HARV-001`) — regulation, not biology.
- **Observation-quality suite (F)** — meta-variables; QARTOD/GHRSST flags are the method standards.
- **Claim-class splits** of abundance (direct count vs index vs CPUE vs suitability vs eDNA occupancy) — EBVs name “species abundances”; FishAI refuses to collapse those classes.

### Not a licence

Citing an EOV/EBV/IOOS name does **not** mean FishAI has global coverage, operational skill, or rights to redistribute a matching product.

---

## Privacy (registrar defaults)

Follow [`../sensitive_location_policy.md`](../sensitive_location_policy.md). Stricter than the most permissive source licence.

| EMIV class | Public native grain |
| --- | --- |
| Open environmental fields (SST, SSH, oxygen, GEBCO, tides) | Allowed after licence; fusion inherits biological tier |
| Fishing effort, AIS identity, reconstructed fishing patterns | **NEVER_PUBLISH** native; no competitor tracking |
| Telemetry-derived movement of sensitive taxa | **NEVER_PUBLISH** raw tracks |
| Spawning / nursery / nesting habitat | **NEVER_PUBLISH** native GPS, depth, moon timing |
| Rare / listed occurrence and rare eDNA | **NEVER_PUBLISH** native coordinates |
| Farm KPIs / mortality / disease / genetics | **PRIVATE** / **NEVER_PUBLISH** publicly |
| Official MPA / Slow Zone / growing-area class | **Exactly** as the authority publishes |

This registrar **does not recommend publishing** native-grain EMIVs the sensitive-location policy marks `NEVER_PUBLISH`.

---

## Honesty constraints (shared with the observatory README)

- A model is not an observation.
- Vessel density is not abundance.
- Satellite surface imagery is not a census of animals below the surface.
- Habitat suitability is not current presence, harvest legality, or food safety.
- WA DOH / NSSP closure is not farm ops-risk ground truth.
- Hood Canal ORCA is not Willapa instrumentation.

---

## What this version is not

- Not an ingest plan and not a globe schema.
- Not a claim that 84 EMIVs are observed globally.
- Not a wedge lock (W1 remains **RECOMMENDED, not DECIDED** in sibling commercial artifacts).
- Not legal advice; harvest/food-safety authority stays with NSSP/WA DOH and analogue bodies.
