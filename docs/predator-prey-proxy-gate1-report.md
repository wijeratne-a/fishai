# Predator–prey proxy experiment — GATE 1 report

Branch: `cursor/fishai-predator-prey-proxy-48df`  
Date (UTC): 2026-10-12  
Hypothesis: public electronic-tag foraging locations for CPS predators validate or improve prey SDMs.

**Outcome: GATE 1 STOP (clean negative).** TOPP public telemetry in the pilot domain ends by **2009**; CPS prey presence events after **2010** have **zero** overlapping-era predator points. GATE 2 modeling was **not** run.

Machine-readable summary: `artifacts/predator_prey_proxy/gate1_overlap_summary.json`  
Reproduce: `python3 scripts/predator_prey_gate1_overlap.py`

---

## STEP 1 — Repo orientation (jack mackerel all-sizes encounter)

| Item | Location / value |
|------|------------------|
| Config | `configs/models/jack_mackerel_encounter_all_sizes.yaml` |
| CV harness | `scripts/jack_mackerel_encounter_spatial_block_cv.R` → `run_cv_spatial()` (fishaisdm) |
| Training table | `data/processed/adult_cps/adult_cps_training_table.parquet` |
| Events / folds | `data/processed/adult_cps/adult_cps_events.parquet`, `artifacts/spatial_block_cv/adult_cps_fold_assignment.csv` |
| Product label | **jack mackerel encounter probability (all sizes)** (not adult-length) |
| Validated CV spec | Linear GLORYS covariates, **spatial off**, rw0 time random walk |
| Baseline (committed artifact) | `artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json`: **4/4 folds converged**, **OOF AUC 0.7622**, ELPD −423.96, **253** presences / **536** fit rows |

Survey coverage (public ERDDAP, pilot bbox 32–35°N, 121–117°W):

- **Mid-water trawl** `FRDCPSTrawlLHHaulCatch`: **2003-07-09 → 2025-09-10** (`docs/adult-data-availability-report.md`).
- **Nearshore purse seine** `FRDCPSNearshoreSetCatch`: **2019-06-21 → 2026-06** (same doc).
- Jack mackerel encounter fit frame spans recent nearshore/trawl years including **2024–2025** (fold-4 holdout note in `docs/jack-mackerel-encounter-all-sizes-readout.md`).

---

## STEP 2 — Public predator tag sources

### TOPP (Tagging of Pacific Predators, Census of Marine Life; program ~2000–2010)

Public distribution used here: **GBIF / OBIS-SEAMAP** (two datasets whose titles explicitly include “TOPP”):

| Dataset | GBIF URL | Global occurrences | Pilot-bbox occurrences | Notes |
|---------|----------|-------------------:|-----------------------:|-------|
| TOPP Summary of SSM-derived Telemetry | [10.82144/d127533f](https://www.gbif.org/dataset/50914b57-6c66-4432-91c7-edbc7a296a9f) | **10,692** | **57** | SSM-derived; many **1°** grid cells |
| TOPP Albatrosses 2002-06 | [dataset](https://www.gbif.org/dataset/e737f8ca-6176-4e3a-9ab1-dc5a77d46194) | **33,789** | **415** | Point-level shearwater/albatross tracks |
| **Combined TOPP-titled GBIF** | | **44,481** | **472** | |

Literature/program scale (~4,306 tags, 23 species, UCSC-led, ended **2010**) is **not** fully mirrored as separate GBIF dataset titles; only the two rows above are explicitly labeled TOPP on GBIF as of 2026-10-12.

**Pilot-bbox predator years:** **2003–2009** only (**472** locations; **0** in **2011+**).

Top taxa in pilot bbox (location counts): *Phoebastria immutabilis* **417**, *Zalophus californianus* **11**, *Balaenoptera musculus* **11**, *Puffinus griseus* **9**, other marine mammals/turtles **≤8** each.

### IOOS ATN

- Portal: https://portal.atn.ioos.us/
- **2026-10-12:** site loads; no bulk **ERDDAP** or **`/api/`** export found (`404` on probed paths). No automated pull of California Current tag tracks in this run.

### Ocean Tracking Network (OTN)

- https://oceantrack.org/data/ — infrastructure/program pages; **no** California Current bulk track endpoint used (network is Atlantic-centric).

### IMOS Animal Tracking Facility

- https://animaltracking.aodn.org.au/ — **Australian** domain; out of SCB geography (not queried).

---

## GATE 1 — Spatiotemporal overlap

**Prey** (CPS **presence** rows, pilot bbox, public ERDDAP pull in script):

| Metric | Value |
|--------|------:|
| Presence events (jack mackerel + sardine + anchovy) | **968** |
| Year range | **2005–2026** |
| Presence events with year **≥ 2011** | **911** |
| By species (presences) | sardine **312**, anchovy **375**, jack mackerel **281** |
| By source | trawl **720**, nearshore **248** |

**Predator** (TOPP GBIF, pilot bbox): **472** locations, years **2003–2009**, **0** locations **≥ 2011**.

**Overlap rules:** ≤ **50 km** great-circle and ≤ **14 days** between predator location time and prey presence event time.

| Overlap set | Predator points | Prey presences | Predator matched | Frac. predator matched | Prey events matched | Frac. prey matched |
|-------------|----------------:|---------------:|-----------------:|-----------------------:|--------------------:|-------------------:|
| All years in bbox | 472 | 968 | **35** | **0.0742** | **2** | **0.00207** |
| **Post-2010 prey era** (pred ≥2011 vs prey ≥2011) | **0** | **911** | **0** | **0.0** | **0** | **0.0** |

The all-years overlap (**7.4%** of predator points) is confined to the **pre-2011** trawl/nearshore tail (**57** prey presences with year ≤2010 in this pull vs **911** after 2010). It does **not** intersect the jack mackerel encounter model’s dominant training era (nearshore **2019+**, trawl-heavy **2011+**).

### GATE 1 verdict

**STOP — temporal mismatch.** Public TOPP GBIF telemetry in the SCB pilot box ends **2009**; **911** post-2010 prey presence events have **zero** co-era predator tags. **GATE 2** (predator-density covariate + spatial-block CV) was **not** attempted.

This is an **honest clean negative** for the TOPP→prey-SDM proxy under the repo’s CPS training windows—not a modeling failure.

---

## Baseline retained for future GATE 2 (not run)

Jack mackerel encounter (all sizes): **OOF AUC 0.7622**, Brier not stored in CV JSON; **4/4** folds, linear + spatial-off spec unchanged.
