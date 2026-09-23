# Species model factory

**Program:** Global Saltwater Life Observatory  
**Date:** 2026-09-18  
**Status:** Process specification. No species model has been built or published.  
**Does not ingest data.** Steps 2+ are catalog, design, and (later) gated computation.

This factory is how a WoRMS taxon becomes an evidence-typed estimate—or is honestly left at “UNKNOWN.” It is **not** an automated license to emit maps.

Commercial wedge models, if any are ever built, must still pass this factory **and** the narrower commercial gates (one geography, one decision, prediction contract). The factory must not be used to expand that product.

---

## Eligibility vs emission

| Concept | Meaning |
|---------|---------|
| Factory **eligibility tier** | Highest tier justified by cited evidence (CSV `support_tier`) |
| **Emitted** product | What an API or card actually returns |
| Iteration 1 emission | For every taxon: `UNKNOWN/INSUFFICIENT DATA` — no factory run has reached Step 7 |

---

## STEP 1 — Taxonomy resolution

**Goal:** a single accepted identity and the partitions that would otherwise leak into the label.

**Do:**

- Resolve accepted scientific name, authorship, AphiaID, LSID.  
- Collect synonyms needed for FAO, NOAA, literature, and occurrence joins.  
- Record common-name collisions.  
- Set marine / brackish / freshwater flags from WoRMS.  
- Declare life stage (do not default adults if the question is larvae).  
- Declare population unit (stock, ESU, management area, `not_partitioned`).  
- Mark ecological sensitivity (listed, spawning, nursery, harvest, Indigenous).

**Exit criteria:** fields in `taxonomy_graph/taxonomy_standard.md` §2 populated; `access_date` set.

**Stop if:** name is unavailable/Candidatus only (remain T0); freshwater-only; identity ambiguous between two accepted species.

**Output class:** not an observation. Identity metadata only.

**Capability:** (1) observable today as a name in WoRMS.

---

## STEP 2 — Data availability audit

**Goal:** know what could be used **if** rights later allow, without downloading bulk observations.

**Audit dimensions:**

- observation count (catalog metadata, e.g. OBIS `total` with `size=0`);  
- recency and latency;  
- geographic spread and gaps;  
- depth coverage;  
- sampling methods and effort bias;  
- survey programs;  
- tagging / acoustic / eDNA / imagery;  
- catch/effort (never as abundance without catchability model);  
- habitat and environmental coverage;  
- rights status;  
- privacy and ecological sensitivity.

**Exit criteria:** written audit with official URLs, access dates, `license=UNKNOWN` unless verified; `integration_status=CATALOG_ONLY` until rights approval.

**Stop if:** no lawful path; sensitive coordinates would be required to reach the claimed tier.

**Forbidden:** treating AIS/VMS as abundance; scraping paywalls; ingesting GBIF/OBIS point caches “to see.”

**Capability notes:** high OBIS counts are (1) for **historical compiled records**, not (1) for current census.

---

## STEP 3 — Ecological profile

**Goal:** mechanisms, not a kitchen-sink of ocean layers.

Record, with citation, only drivers with a stated mechanism:

temperature, salinity, depth, substrate, oxygen, pH, light, prey, currents, seasonality, spawning, migration, predators, habitat, life stage, climate sensitivity, disease, fishing selectivity, culture method (if farmed).

Mark each driver:

- causal vs correlative vs proxy vs unknown;  
- time scale (hours vs season vs climate);  
- whether satellite **surface** fields can stand in for the animal’s depth.

**Exit criteria:** profile stored under `species_ecology_profiles/` (later); known missing drivers listed.

**Chinook lesson (do not repeat):** juvenile chlorophyll-nearshore papers are the wrong ecological profile for adult ocean charter encounter.

**Oyster lesson:** air temperature × emersion is not the same as SST; pH/Ω is first-order for larvae, not 72 h adult farm mortality.

**Lobster lesson:** bottom temperature changes **catchability**; CPUE ≠ abundance.

---

## STEP 4 — Model eligibility (assign support tier)

Using [`global_species_registry/support_tier_framework.md`](global_species_registry/support_tier_framework.md), assign **one** tier for the declared life-stage × geography.

Decide which artifacts **may** be built:

| Artifact | Minimum tier |
|----------|----------------|
| Identity card only | T0 |
| Historical range / occurrence-coverage | T1 |
| Habitat suitability | T2 |
| Current occurrence/encounter or relative condition | T3 |
| Short-horizon forecast | T4 |
| Direct observation / tag overlay | T5 |
| Operational forecast with performance card | T6 |
| **No model** | default when evidence fails |

**Safety cap** may set `support_tier` below `evidence_ceiling_tier`.

**Iteration 1 result:** example taxa assigned T0–T2 only. T3–T6 require later factory iterations with validation artifacts.

**Output class of the assignment itself:** `HYPOTHETICAL/RESEARCH MODE` until Step 7.

---

## STEP 5 — Model selection

Pick the **simplest** method that matches the tier. Complexity is not a virtue.

| Data regime | Allowed family | Typical output class |
|-------------|----------------|----------------------|
| Low-data (T1 / thin T2) | Historical range + expert-informed habitat envelope + high uncertainty | `SURVEY-DERIVED` / `MODEL-INFERRED` |
| Moderate-data (T2) | Occurrence–environment suitability (e.g. envelope, GAM, occupancy **without** claiming current abundance) | `MODEL-INFERRED` |
| High-data (T3+) | Spatiotemporal occurrence, standardized survey index, or effort-normalized catch **explicitly not sold as abundance** | `MODEL-INFERRED` or `SURVEY-DERIVED` |
| Tagged subset (T5) | Individual movement; **separate** population model | `TAG/TELEMETRY-DERIVED` |
| Acoustic / eDNA-rich | Assimilation with transport and detection-probability; eDNA ≠ head count | `REMOTELY DETECTED` / `MODEL-INFERRED` |
| Operational partner data (T6 path) | Prospective forecast vs partner outcome | `FORECAST` + `OPERATIONALLY OBSERVED` labels |

**Baselines required before any ML:** seasonal climatology of the **label**; persistence; spatial mean. If the candidate does not beat the baseline, label `NOT READY FOR USE`.

**Rejected by default:**

- neural nets on AIS density as “fish”;  
- SST/chlorophyll as abundance;  
- transferring a model across ocean basins or life stages without a declared extrapolation flag.

**Capability:** T2 suitability is (2) inferable today only after Step 6. Claiming (3) forecastable today requires T4 evidence.

---

## STEP 6 — Validate

No model is accepted because it looks like a map.

**Minimum tests (T2+):**

- temporal holdout;  
- spatial holdout;  
- out-of-season holdout if seasonality is claimed;  
- independent source when possible (survey vs opportunistic);  
- calibration of uncertainty;  
- error analysis by region, season, effort.

**Additional red-team questions (spec §11):** data leakage; future data; learning sampling effort instead of biology; learning vessels instead of animals; confusing habitat with presence; hotspot overfitting; spatial autocorrelation; climate-anomaly failure; hidden low coverage; false cross-species generalization; sensitive-location leak; claim stronger than evidence; failure vs seasonal average.

**T3–T6:** prospective or time-forward tests. Retrospective skill is not operational grade.

**Output:** records in `species_model_registry/` and `scientific_red_team_reports/`. Status `NOT READY FOR USE` is a successful honest result.

---

## STEP 7 — Publish

Publish only what the tier allows, under [`user_output_contract.md`](user_output_contract.md).

**Species card contents:**

- taxonomy + geography + life stage;  
- evidence layer and sources;  
- current model tier and version;  
- prediction or suitability field **if** tier ≥ 2 and validation passed;  
- depth profile or explicit “depth unknown”;  
- time window;  
- uncertainty;  
- source attribution;  
- known limitations;  
- legal/privacy/ecological restriction;  
- output class and capability class.

Public grains must be coarsened per sensitive-location policy. Exact tracks, nests, spawning sites, private sets, and farm KPIs are not Step 7 public artifacts.

**Iteration 1:** no species card is published as a prediction. The CSV is a registry, not a map.

---

## STEP 8 — Monitor and update

After any live model (none today):

- new records and taxonomy updates;  
- source outages and licence changes;  
- model drift and ocean-regime change;  
- data-quality flags;  
- validation performance;  
- harm incidents.

Triggers to **downgrade** tier: failed prospective window, lost rights, WoRMS split, or ecological-harm finding.

Cadence hypothesised (not implemented): re-resolve taxonomy at least when WoRMS `modified` > last access; re-validate T3+ each season; checkpoint every `CHECKPOINT_INTERVAL_HOURS`.

---

## Factory stop conditions

Stop a taxon run (do not “fill gaps” with speculation) if:

- identity unresolved;  
- rights blocked;  
- only path to skill is prohibited data (secret spots, TEK without consent, listed-species pinpoint);  
- physical impossibility at the claimed grain (e.g. exact census of mesopelagic fishes from surface color);  
- budget for hypothesis iterations or prototype designs exhausted.

Record the stop as T0 or T1 with `UNKNOWN/INSUFFICIENT DATA`. That is a valid factory output.

---

## Relation to observatory architecture layers

| Factory step | Architecture layer (spec §7) |
|--------------|------------------------------|
| 1 | LAYER 0 taxonomy |
| 2 | LAYER 1–2 observations (catalog, not lake) |
| 3 | LAYER 4 ecology knowledge |
| 4–5 | LAYER 5–6 features and models |
| 6 | LAYER 8 uncertainty / evidence |
| 7 | LAYER 9 user outputs / API |
| 8 | LAYER 10 feedback |

Digital-twin assimilation (spec §10) is a **later** design object. It must consume factory outputs with their class labels intact. Assimilation does not convert `MODEL-INFERRED` into `DIRECTLY OBSERVED`.
