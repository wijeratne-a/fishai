# Species support-tier framework

**Program:** Global Saltwater Life Observatory  
**Date:** 2026-09-18  
**Status:** Binding for registry rows and for the species-model factory  
**Companion:** [`../species_support_tiers.csv`](../species_support_tiers.csv), [`../species_model_factory.md`](../species_model_factory.md), [`../user_output_contract.md`](../user_output_contract.md)

No taxon may be upgraded without cited evidence. Most saltwater taxa in the world are T0 or T1. That is the expected steady state, not a failure.

---

## 1. What a tier is

A support tier is the **strongest output class this observatory is allowed to produce** for a taxon × life-stage × geography, given:

- cited public evidence (or permissioned partner evidence after rights review);
- ecological-safety and privacy caps;
- whether a model, if any, has been validated at that claim strength.

A tier is **not**:

- a conservation status;
- a commercial priority;
- a statement that FishAI currently operates a live feed;
- a statement that individuals can be found.

Example CSV rows assign tiers as **factory eligibility from catalogued evidence**. They do not mean the observatory currently emits maps for those taxa. Until a factory publish step succeeds, the live output class remains `UNKNOWN/INSUFFICIENT DATA`.

---

## 2. The seven tiers

### TIER 0 — Taxonomy only / insufficient data

**Evidence required:** accepted (or documented Candidatus / unavailable) WoRMS record. Occurrence too sparse, too biased, or too stage-specific for even a coarse historical range.

**Allowed output:** taxon identity, synonyms, marine/estuarine/freshwater flags, and the sentence:

> Insufficient data to estimate distribution.

**Forbidden:** range polygons drawn from expert memory; “probably everywhere in the gyre” presented as an observation.

**Typical capability class:** (4) requires new data infrastructure and/or (7) not currently measurable at the requested grain.

**Output class:** `UNKNOWN/INSUFFICIENT DATA`.

### TIER 1 — Historical occurrence

**Evidence required:** compiled georeferenced records sufficient for **coarse** range and, if dates exist, coarse seasonality. In iteration 1, OBIS occurrence **counts** (metadata) plus a WoRMS identity are the cited floor; they are **not** a downloaded occurrence cube.

**Allowed output:** historical range sketch, occurrence density **of records** (effort-biased), data coverage, observation-date span. Explicitly a record of **where sampling happened to detect the taxon**, not where the taxon was absent.

**Forbidden:** current presence; abundance; “hotspots” at capture resolution for sensitive taxa.

**Typical capability class:** (1) observable today as compiled historical records, with severe sampling bias.

**Output class of the evidence:** `SURVEY-DERIVED` (OBIS/GBIF compilations mix survey, specimen, and opportunistic records; do not relabel them `DIRECTLY OBSERVED` without inspecting datasets).

### TIER 2 — Habitat suitability (not current presence / abundance)

**Evidence required:** T1 evidence **plus** documented environmental or habitat envelopes (peer-reviewed habitat paper, FAO culture sheet, NOAA species page with mechanistic covariates, or an equivalent official source).

**Allowed output:** habitat suitability, uncertainty, historical/seasonal context.

**Forbidden (non-negotiable):** current presence; abundance; biomass; harvest legality; food safety; “the animals are here now.”

**Typical capability class:** (2) inferable today as suitability, not as a census.

**Output class if a suitability surface is later published:** `MODEL-INFERRED`. Until published: `UNKNOWN/INSUFFICIENT DATA`.

SST, chlorophyll, and vessel density may be **covariates**. They are never the biological label.

### TIER 3 — Current condition estimate

**Evidence required:** time-aware model **or** a current observation system covering the claimed geography and depth band, **plus** validation against held-out or independent observations at the same grain. A stock assessment terminal-year biomass is **not** automatically T3 for a spatial grid.

**Allowed output:** current occurrence / encounter likelihood or a relative-condition index, with latency and uncertainty.

**Forbidden:** calling a lagged survey “now”; calling a habitat map “current condition.”

**Typical capability class:** (2) inferable today in well-instrumented regions only after validation; elsewhere (4).

**Output class:** `MODEL-INFERRED` or `SURVEY-DERIVED` depending on the method, never silently mixed.

**Iteration 1 assigned count:** 0. No observatory model exists.

### TIER 4 — Short-horizon forecast

**Evidence required:** T3-quality current state **plus** a forecast model of drivers **plus** prospective or time-forward validation at 24 h / 72 h / 7-day (as claimed).

**Allowed output:** forecast with uncertainty, issued-at, valid-from/to, source cutoff.

**Forbidden:** climatology labeled as a 48 h forecast; juvenile-survey papers used as adult-encounter forecasts.

**Typical capability class:** (3) forecastable today only where those tests exist.

**Output class:** `FORECAST`.

**Iteration 1 assigned count:** 0.

### TIER 5 — Direct observation / telemetry

**Evidence required:** recent lawful observation of **identified** organisms or tags, with time, place, depth if known, and detection-probability notes.

**Allowed output:** observation layer or tagged-animal track.

**Required disclaimer:** **individual or group ≠ population.** Selection bias of tagged animals is in-scope.

**Forbidden:** interpolating a few tracks into a census; publishing reconstructable paths of listed taxa, nesters, or commercially secret animals.

**Typical capability class:** (1) observable today for the tagged/observed subset; (4) or (5) for scaling to populations.

**Output class:** `DIRECTLY OBSERVED`, `REMOTELY DETECTED`, `TAG/TELEMETRY-DERIVED`, or `OPERATIONALLY OBSERVED` as appropriate.

**Iteration 1 assigned count:** 0. External tagging programs exist for several example taxa; this observatory has **not** ingested tracks and therefore does not claim T5.

### TIER 6 — Operational grade

**Evidence required:** T4 or T5 (as claimed) **plus** prospective validation, calibrated uncertainty, source resilience, documented data rights, and ongoing outcome feedback. Performance must beat a simple baseline (seasonal mean / persistence) or the product is `NOT READY FOR USE`.

**Allowed output:** operationally useful forecast or nowcast with documented historical performance.

**Forbidden:** marketing T6 because the subject is commercially important.

**Iteration 1 assigned count:** 0. The commercial wedge is also not T6.

---

## 3. Upgrade and downgrade gates

Upgrade T*n* → T*n+1* only when **all** of the following are true:

1. Written evidence URLs with access date.  
2. Rights status is not `blocked` for the intended use.  
3. Ecological-safety review: public grain cannot enable poaching, harassment, or secret-spot leakage.  
4. For T3+: independent or held-out validation recorded in `species_model_registry/`.  
5. Red-team sign-off that the claim is not stronger than the evidence.  
6. Human review if the taxon is listed, harvested, or culturally sensitive.

**Automatic caps (downgrade even if data exist):**

| Trigger | Public cap |
|---------|------------|
| Endangered / listed / CITES / aggregation / nesting / spawning / nursery | Often T1 coarsened or `NEVER_PUBLISH` coordinates; habitat surfaces that function as finding aids are not public T2 |
| Farm performance, private catch, VMS/AIS identity | `PRIVATE` / `NEVER_PUBLISH`; not a T5 public layer |
| Indigenous / TEK | Out of registry products unless a nation publishes and licenses the use |
| Observatory has not ingested the stream | Do not assign T5/T6 |

Downgrade immediately if a source is withdrawn, taxonomy splits, validation fails, or harm review fails.

---

## 4. Capability classes (mandatory on every row and output)

| Code | Name |
|------|------|
| 1 | Observable today |
| 2 | Inferable today |
| 3 | Forecastable today |
| 4 | Requires new data infrastructure |
| 5 | Scientifically plausible but unproven |
| 6 | Technically speculative |
| 7 | Physically impossible or not currently measurable |

Multiple codes may apply to different questions about the same taxon (e.g. white shark: (1) tagged subset; (7) exact location of all individuals). The CSV stores the code for the **assigned tier’s primary claim**.

---

## 5. Mapping to commercial-wedge prediction categories

The commercial red-team contract uses categories A–E (direct count, survey index, CPUE, habitat-encounter-risk, unverified indicator). Observatory tiers relate as follows:

| Observatory tier | Compatible commercial categories | Rejected |
|------------------|----------------------------------|----------|
| T0 | none | all quantitative maps |
| T1 | none as a “now” product; historical context only | A, C sold as abundance, E |
| T2 | D (habitat / stress / encounter **risk**), never A | E (SST/AIS/chl as the animal) |
| T3 | B or D, sometimes C as **evaluation** not abundance | A, E |
| T4 | D or C as forecast of the **declared** target | A, E |
| T5 | observation overlay | population A from a few tags |
| T6 | whatever was validated, still never A without a census design | E |

Commercial W1/W2/W3 remain **one geography, one decision**. A T2 global oyster row does not authorize a worldwide oyster product.

---

## 6. Honesty failures this framework exists to prevent

- Exact locations of all individuals.  
- Exact census.  
- Real-time tracking without contemporaneous observation.  
- Abundance from satellite surface image.  
- Abundance from vessel density.  
- Harvest legality or food safety from habitat.  
- Treating a model as an observation.  
- Upgrading Chinook or lobster to T3 because a stock assessment PDF exists.  
- Upgrading Pacific oyster to T5 because farmers know what they planted. That knowledge is `OPERATIONALLY OBSERVED` **on a private lease**, not a global observatory layer.
