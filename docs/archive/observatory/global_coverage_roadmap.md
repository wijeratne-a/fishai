# Global coverage roadmap — what “coverage” is allowed to mean

**Date:** 2026-09-18  
**Agent:** COST_AND_DEPLOYMENT_ECONOMICS_AGENT + UI/EXPLAINABILITY  
**Rule:** Coverage is a **property of evidence**, not a paint bucket.

---

## 1. Coverage is five-dimensional

A cell is not “covered” because a polygon is colored. Report coverage as the tuple:

| Axis | P0 (Year 1) | Year 3 | Year 10 |
| --- | --- | --- | --- |
| **Taxon / life stage** | 1 species, farmed grow-out | 2–5 slices, named stages | Many T0–T2 cards; few T4–T6 slices |
| **Geography** | 1 estuary system (Willapa growing areas / leases) | A few named official polygons | Many EEZs with **sparse** support; not uniform |
| **Depth / vertical** | Emersion vs near-surface station; **no** 3-D oyster field | Some cells with bottom-T or acoustic depth bins | Depth-aware **where measured**; UNKNOWN elsewhere |
| **Time** | Hourly covariates; daily 72h forecast issuance | Prospective multi-season | Continuous issuance in operational cells; lagged surveys elsewhere |
| **Evidence class** | Mix of DIRECTLY OBSERVED env + FORECAST stress + UNKNOWN biology | Same, plus some SURVEY-DERIVED / OPERATIONALLY OBSERVED | Still dominated by UNKNOWN for most taxa×cells |

**Forbidden metric:** “X% of ocean pixels have a species probability.” That metric rewards interpolation.

**Required metrics:**

- Fraction of taxon×cell×depth-bin with **non-UNKNOWN** evidence of a stated class.  
- Observation latency and as-of completeness.  
- Distance to nearest in-situ constraint.  
- Support tier T0–T6 (no silent upgrades).  
- Privacy/ecological publish class (PUBLIC … NEVER_PUBLISH).

---

## 2. Honest coverage today (2026) — not our system, the planet

These are **capability statements** about the world, not claims that FishAI has ingested them.

| What exists globally | What that is **not** |
| --- | --- |
| Satellite SST, ocean color, altimetry, scatterometer winds | Fish, shellfish counts, subsurface DO, intertidal tissue temperature |
| Argo / GO-SHIP / glider physics (sparse) | Biological sampling at Argo density |
| OBIS/GBIF occurrences | Abundance, effort-corrected occupancy, real-time presence |
| Stock assessments for **data-rich fisheries** | 24–72h location of individuals |
| Acoustic surveys on assessment transects | Species ID for all backscatter; coverage between transects |
| Telemetry networks (OTN, ATN, Movebank) for tagged subsets | Population location |
| eDNA studies, mostly campaigns | A mesh |
| IOOS-class coastal sensors, uneven | Lease-scale microclimate |
| PAM archives for vocal mammals (selected basins) | Silent taxa |
| DAS **research** on some cables | Operational global mammal tracker; any fish census |

**Default global biological state in an honest twin:** **UNKNOWN / INSUFFICIENT DATA**, with habitat suitability (T2) only where occurrence+env allow, clearly labeled **not current presence**.

---

## 3. Path from sparse observations to “broader coverage”

Coverage grows by **adding constrained cells**, not by stretching a model.

```
T0 taxonomy card
  → T1 historical occurrences (biased)
    → T2 habitat suitability (NOT presence)
      → T3 nowcast of condition / encounter in a bounded cell with local labels
        → T4 short-horizon forecast with prospective skill
          → T5 direct tracks (individuals ≠ population)
            → T6 operational (calibrated, rights, feedback, resilience)
```

**Leverage order (information per dollar)** — matches hardware-last:

1. Reuse public env + official polygons.  
2. Unlock partner operational labels.  
3. Export existing sensors.  
4. Manual/mobile protocol.  
5. Opportunistic platforms (ferries, farms, fishing gear) with privacy aggregation.  
6. Targeted new sensing (eDNA, PAM, AUV) **on residual uncertainty**.  
7. Cable DAS / satellite tasking for **surface-visible or vocal** classes only.

Indirect paths that **do** exist (do not stop at “satellites can’t see fish”):

- Acoustics + catch + eDNA **fusion** on survey lines.  
- Tags teaching movement kernels for untagged animals (**with selection-bias caveats**).  
- Circulation + behavior for larvae/plankton (still not adults of most fishes).  
- Aquaculture sentinels for **local** water-column biology (not wild census).  
- Soundscape indices for ecosystem **change**, not headcounts.

---

## 4. Geographic rollout (scientific, not marketing)

| Wave | Geography | Why | Coverage claim allowed |
| --- | --- | --- | --- |
| 0 | Paper catalogs, no ingest | Rights + honesty | None |
| 1 | **Willapa Bay system** (or founder-locked named growing areas) | P0 twin | One estuary, one taxon |
| 2 | At most one additional WA basin **or** one other locked wedge cell | Transfer / second decision | Two cells ≠ “US West Coast” |
| 3 | Partner-rich basins (e.g. GOM statistical area if lobster DUAs) | Labels exist | Named SA only |
| 4 | IOOS RA mosaics as **env context** | Physics prior | Env coverage ≠ bio coverage |
| 5 | Global **T0–T2 cards** via OBIS/WoRMS | Honest emptiness | Taxonomy + range sketches |
| 6 | Cable landings, MPAs, polar programs via consortia | Decade vision | Vocal / physical / molecular **campaigns** |

Never announce Wave 5 as if it were Wave 1.

---

## 5. Depth coverage roadmap

| Zone | Year 1 | Year 3 | Year 10 still missing |
| --- | --- | --- | --- |
| Intertidal emersion | **In P0** (tide + air; optional bed temp) | Better microclimate if partners export | cm-scale bag physics everywhere |
| Estuarine mixed layer | Station point samples | More farms/ferries | 3-D DO every creek |
| Shelf surface | Satellite SST/chl as covariates | Same | Subsurface fish |
| Shelf bottom | Not in oyster P0 | Possible lobster cell (eMOLT-class) | Uniform bottom-T |
| Mesopelagic / deep | T0–T1 at best | Campaign acoustics | Census of deep life |
| Ice / polar night | Out of P0 | Research partners | Winter optical biology |

---

## 6. Taxon-class coverage (roadmap, not a registry)

Detailed matrix: sibling `observation_modality_catalog.md` / `observation_coverage_maps/`. This table is the **product implication**.

| Class | Honest 10-year “coverage” | Still not covered |
| --- | --- | --- |
| Farmed sessile bivalves (P0) | Local ops-stress T4–T6 in a few estuaries | Wild set, bay-wide abundance |
| Assessed commercial finfish | Seasonal survey indices; maybe T3–T4 encounter in tiny cells | 24h school GPS for all stocks |
| Sharks/rays | Some satellite/acoustic tags; rare clear-water imagery | Population real-time |
| Crustaceans (trap fisheries) | Private CPUE T3–T4 if logs | Stock maps from AIS |
| Cephalopods | Mostly T0–T2 | Operational forecast |
| Marine mammals | PAM/DAS/tags **coarsened**; T5 individuals | Public fine tracks; abundance of all odontocetes |
| Turtles / nesting | Beach programs; NEVER_PUBLISH nests | Foraging census |
| Seabirds (marine) | Colony + some tracking | At-sea census everywhere |
| Plankton / HAB | Satellites + nets + some imaging | Species-resolved 3-D globe |
| Jellyfish | Optical/acoustic campaigns | Global biomass |
| Corals / benthos | Occasional imagery/photogrammetry | Live 3-D every reef |
| Macroalgae / seagrass | Improving remote maps | Under-canopy fauna |
| Microbes | Molecular campaigns | Continuous global metabolome |
| Larvae | Transport models + sparse samples | Individual tracking |

---

## 7. What “global coverage” **still cannot mean in 10 years**

Even in a successful decade — public-good funding, partners, cables, molecular labs, honest software — **global coverage must not be sold as:**

1. **A census of individuals** of all (or even most) saltwater species.  
2. **Real-time tracking** of untagged populations.  
3. **Exact counts in unsurveyed cells.**  
4. **Abundance inferred from satellite surface temperature, chlorophyll, or vessel density.**  
5. **Uniform depth-resolved biomass** of the world ocean.  
6. **Operational (T6) forecasts** for more than a **small minority** of taxa×places.  
7. **Harvest legality, food safety, or navigation** as a model output.  
8. **ESA/MMPA fine-scale locations** of breeding, nesting, spawning, or listed stocks.  
9. **Private fishing grounds or farm performance** as a public layer.  
10. **A single foundation model that is confident in empty cells.**  
11. **Species identity of all acoustic backscatter.**  
12. **eDNA as a GPS fix** (transport and decay remain).  
13. **DAS as a fish-finder** (whale-class vocalizations ≠ nekton census).  
14. **Knowledge of the deep and polar night** comparable to coastal IOOS.  
15. **Closure of UNKNOWN** — the unknown map should **grow in resolution**, not disappear.

**What it *can* mean in 10 years (if funded and honest):**

- A **planetary unknown/coverage fabric** with provenance.  
- Operational twins in **dozens of bounded cells**, not millions of taxa.  
- Better fusion on survey lines (sonar × eDNA × catch × physics).  
- Partner meshes (farms, ferries, gear sensors) with privacy.  
- Cable/PAM networks for **vocal** megafauna, coarsened for public use.  
- T0–T2 cards for most named marine taxa, with the courage to stay there.

---

## 8. Coverage reporting template (use in checkpoints)

```
coverage_id: CELL-WILLAPA-MGIGAS-OSI72
as_of: 2026-09-18T00:00:00Z
taxon: Magallana gigas (Aphia 836033)
life_stage: farmed grow-out
geography: WA DOH growing areas, Willapa Bay system
depth_representation: emersion_binary + nearest_station_m
evidence_classes_present: [DIRECTLY_OBSERVED, REMOTELY_DETECTED, FORECAST, UNKNOWN]
support_tier: T2  # do not upgrade without prospective skill
fraction_hours_with_critical_inputs_fresh: UNKNOWN  # not measured yet
partner_outcome_completeness_28d: n/a
publish_class: PRIVATE farm outcomes; PUBLIC env only if rights allow
what_this_is_not: abundance, food-safety, harvest authorization
```

Until that block can be filled with measurements, **do not claim coverage**.
