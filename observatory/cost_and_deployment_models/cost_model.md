# Cost and deployment model — Global Saltwater Life Observatory

**Agent:** COST_AND_DEPLOYMENT_ECONOMICS_AGENT  
**Date:** 2026-09-18  
**Access date for URLs:** 2026-09-18  
**Status:** Order-of-magnitude planning model. Not a quote, not a grant budget, not a claim that hardware should be bought.  
**Currency:** USD unless noted. FX conversions are **ESTIMATE**.

**Scope firewall:** This file prices a *scientific observatory*. The commercial FishAI product stays **ONE species × ONE geography × ONE customer × ONE decision** until traction gates are met. Do not treat Year-1 observatory spend as a license to build a global taxa map.

**Recommended Year-1 spend object:** a public-data-first software twin of **one bounded cell** that could later serve the commercial wedge (Pacific oyster × Willapa Bay growing-area / lease × 24–72h operational stress). Hardware is last.

---

## 0. How to read every number

| Label | Meaning |
| --- | --- |
| **CITED** | A figure from a named public page, tender, peer-reviewed paper, or lab price list. May be outdated, vendor-list, or internal-recharge — still not *our* invoice. |
| **ESTIMATE** | This agent’s order-of-magnitude band, combining cited unit costs with staffing, cloud, legal, and failure rates. Uncertainty is typically **×2–×5**. |
| **UNKNOWN** | No defensible public price; do not invent a precise dollar. |

Never average CITED unit prices into a fake “market cost of observing the ocean.” Vessel-day rates, DAS fiber access, and partner DUAs dominate many stacks and are not in the instrument sticker.

**Inflation / vintage:** several acoustic and PAM figures are 2015–2021. Treat them as **order-of-magnitude anchors**, not 2026 RFQs.

---

## 1. Procurement order (binding)

Buy capability in this order. Skip a step only with a written residual-uncertainty argument (what the previous layer cannot observe, what the next layer uniquely adds, kill criteria).

| Rank | Layer | Year-1 default |
| ---: | --- | --- |
| 1 | **Public data** (IOOS/NANOOS, CO-OPS, NWS, CMEMS, tides, official polygons as *context*) | **DO THIS** |
| 2 | **Partner export** of data they already collect (farm logs, existing thermistors, haul/work forms) | **DO THIS** if DUA signed |
| 3 | **Existing sensors** already in the water (IOOS, farm, ferrybox) — export, don’t replace | **DO THIS** |
| 4 | **Manual observations** (protocol counts, 30-second outcome form, photos) | **DO THIS** |
| 5 | **Mobile** capture of those observations | **DO THIS** (form, not an app store) |
| 6 | **Integrations** (email/PDF, later BlueTrace/Esri/API) | After a human brief works |
| 7 | **New hardware** (own sonar, eDNA mesh, hydrophones, DAS, AUVs, tasked VHR) | **NOT Year-1** unless a named micro-experiment (<$25k) or a partner already owns the kit |

A “planetary sensor mesh” is a **decade-scale research program**, not a prototype prerequisite.

---

## 2. Six stacks compared

All stacks are scored for a **single prototype cell** (one estuary or one statistical area, one taxon, one decision) and for a **naive global fantasy**. The global column is there to kill the fantasy, not to authorize it.

### 2.1 Public-data-only software twin

**What it estimates:** environmental state + **Category D** relative operational-stress / habitat-condition index in a named cell. Not abundance. Not harvest legality. Not “where every oyster is” (they are planted).

**Evidence class of outputs:** MODEL-INFERRED or FORECAST on top of DIRECTLY OBSERVED / REMOTELY DETECTED covariates; UNKNOWN where stations are missing.

| Item | Band | Label | Source |
| --- | --- | --- | --- |
| Copernicus Marine products (physics/BGC, incl. SST) | **$0** to user through **2028-06-30** (program-funded) | CITED | [CMEMS service commitments and licence](https://marine.copernicus.eu/user-corner/service-commitments-and-licence) — free of charge to user; worldwide royalty-free licence to create value-added products; **attribution + DOI required**; third-party datasets may differ |
| NOAA CO-OPS / NWS / many USGov streams | **$0** licence (rate limits, no-endorsement) | CITED (policy) | [NWS disclaimer](https://www.weather.gov/disclaimer); CO-OPS API. Per-stream commercial use still needs DATA_RIGHTS review (NANOOS DMP exceptions exist) |
| Cloud + object store for **one estuary**, as-of snapshots, 1–3 years | **$5k–$40k / year** | ESTIMATE | Small NetCDF/Parquet + email; not a planetary lake |
| 2–4 FTE (scientist, engineer, product/ops) fully loaded US | **$400k–$1.1M / year** | ESTIMATE | $180k–$280k fully loaded per specialist FTE is a planning band, not a salary survey |
| Legal / DUA / insurance-adjacent review | **$20k–$80k / year** | ESTIMATE | HUMAN LEGAL REVIEW; not optional |
| Domain reviewer (shellfish / acoustics as needed) | **$15k–$60k / year** | ESTIMATE | Contract or in-kind Sea Grant/extension |
| 3 design-partner farms, travel, incentives | **$10k–$40k** | ESTIMATE | Pilot SKU is $0–$1.5k; cost is *our* time + incentives, not ARPU |

**Year-1 cell total:** **$0.4–1.2M** ESTIMATE (lean founder-heavy **$0.25–0.5M**; staffed **$0.8–1.5M**).

**What this stack cannot buy:** on-lease microclimate, farm mortality labels, species ID of wild fish, global coverage.

**Scale path:** software cost grows with **QA and partner ops**, not with km² of Copernicus. Adding a second ocean basin without partners is cheap computationally and scientifically worthless.

---

### 2.2 Partner vessel sonar (cooperative acoustics)

**What it can observe:** calibrated acoustic backscatter along **tracks that vessels already steam**. School/biomass *indices* after calibration — **not** species counts, **not** a public hotspot map.

**Hardware-last reading:** most value is **export of existing sounders** + edge features + privacy grid. Buying EK80s for a startup fleet is the expensive, late path.

| Item | Band | Label | Source |
| --- | --- | --- | --- |
| Portable EK80 mini (200/333 kHz kit, 2021 quote) | **$54,580** | CITED | MBARI Kongsberg quote 165049.01 (2021-06-03): [PDF](http://docs.mbari.org/internal/projects/706007%20USGS%20LRAUV/Documents/Purchasing/1650049.01%20EK80%20Mini%20200%20333%20MBARI.pdf) |
| Full scientific EK80 / multi-beam package (DFO Canada tender estimate) | **CAD $441,248** (HST extra) | CITED | [CanadaBuys PW-PWB-013-3930](https://canadabuys.canada.ca/en/tender-opportunities/tender-notice/pw-pwb-013-3930) |
| University recharge, single EK80 transceiver | **$36–$163 / day** equipment only | CITED | [FIU Marine Acoustics Recharge Center](https://research.fiu.edu/facilities-and-administrative-costs/facilities/recharge/fiu-marine-acoustics-recharge-center/) |
| Echoview / processing labor | **~$568 / day** data synthesis (internal recharge) | CITED | Same FIU rate table |
| Privacy-preserving edge pipeline + DUA + calibration protocol for **N existing boats** | **$80k–$250k** Year-1 software/science | ESTIMATE | Does not include boats |
| Scientific survey vessel-day (if you *run* surveys instead of riding partners) | **$10k–$40k+ / day** class (operator-specific; older UNOLS planning tables cited ~$12k–$37.5k) | CITED vintage / UNKNOWN 2026 | [Scripps: request operator quote](https://scripps.ucsd.edu/ships/planning/ship-rates); UNOLS 2014 planning table is **not** a 2026 rate |

**Year-1 honest sonar program (partner export, 3–10 vessels, no new ships):** **$0.1–0.4M** ESTIMATE on top of the software twin — *after* DUAs.

**Year-1 dishonest sonar program (buy calibrated scientific kit + charter ship time):** **$0.5–2M+** ESTIMATE and still not a species map.

**Global cooperative:** UNKNOWN. Dominated by vendor NDAs, calibration, selection bias (boats go where fish or weather send them), and **privacy**. A public biomass globe from recreational sonar would be a scientific and commercial disaster.

**Kill if:** partners will not allow even coarsened, delayed, on-device features; or outputs get read as abundance/species ID.

---

### 2.3 eDNA mesh

**What it can observe:** **recent presence / community composition** in a water parcel, with large spatial-temporal smear from transport and decay. Not “the fish is here now.” Not biomass without taxon-specific calibration.

| Item | Band | Label | Source |
| --- | --- | --- | --- |
| Outsourced extraction + sequencing, marine energy-site study assumption | **$200 / sample** | CITED | DOE/PNNL OSTI [10.2172/1984522](https://doi.org/10.2172/1984522) (Table 10 subcontract line) |
| CALeDNA 30-sample, 6-marker service | **$7,500 / 30 samples ≈ $250 / sample** | CITED | [ucedna.com/nps-costs-biodiversity](https://ucedna.com/nps-costs-biodiversity) |
| Academic amplicon prep+seq (not full marine 12S fish assay) | **tens of USD / sample** + **$1k–$1.5k / project** bioinformatics | CITED | [IMR pricing Nov 2025 PDF](http://imr.bio/docs/IMR-CompletePricing-Nov2025.pdf) — **wrong assay class** if used as a fish-eDNA quote; listed to show lab floors |
| Open-source SASe automated filter | **~$280** build | CITED | Beste-Garrido et al. / *HardwareX* [10.1016/j.ohx.2021.e00239](https://doi.org/10.1016/j.ohx.2021.e00239) |
| Commercial DOT-class sampler | **$55,000** instrument + **$5k–$10k** reagents/cassettes | CITED | Hendricks et al. 2023, PMC10063616 (Dartmouth Ocean Technologies list) |
| MBARI ESP-class autonomous molecular lab | **>$100k** class historically | UNKNOWN 2026 list | Do not pretend we have a current quote |
| **One estuary monthly mesh** (20 sites × 12 months × $200–$250 seq + labor + QC) | **$80k–$250k / year** | ESTIMATE | Lab is cheap vs **field + contamination QC + reference library + transport model** |
| **Coastal “mesh” 1,000 sites weekly** | **$10M–$50M / year** sequencing+field | ESTIMATE | Still not global; still not abundance |
| **Global autonomous mesh** | **$100M–$1B+ / decade** | ESTIMATE | Governance and ships, not PCR |

**Year-1 prototype:** **$0** required. Optional **micro-experiment:** 30–60 samples against known farm/wild presence **$8k–$20k** ESTIMATE — only if it reduces a named uncertainty (e.g. HAB vs oyster stress confusion). Do not build a mesh to decorate an oyster work-window brief.

**Kill if:** transport/decay makes the spatial grain coarser than the decision cell; contamination rate unacceptable; reference library gaps for the target taxon.

---

### 2.4 Hydrophone arrays and DAS

**What it can observe:** **vocalizing** taxa (many marine mammals, some fish choruses, snapping shrimp soundscapes), ships, storms. DAS on existing fiber: baleen-whale-class signals have been shown along cables. **Silent life stages and most invertebrates:** not this stack.

| Item | Band | Label | Source |
| --- | --- | --- | --- |
| C-POD odontocete logger | **~€4,000** + **€250–€500** mooring | CITED (2015) | Culloch et al. 2015 review citing then-current Chelonia price |
| HARP battery line (pre-upgrade) | **~$10,000 / instrument-year** batteries (~50% of refurb) | CITED (2018 $) | Scripps MPL TM-666 (2023) describing 2018 HARP costs |
| Seabed monitoring platform purchase | **£2,800–£50,000** | CITED | [JNCC MMPG-04](https://data.jncc.gov.uk/data/012d92ed-6d93-4339-9251-2ffe29ef2772/jncc-mmpg-04.pdf) |
| Deployment/recovery | **£1,200–£37,000** per op | CITED | Same JNCC guideline (vessel + two scientists) |
| Commercial DAS interrogator (industry commentary) | **$200k–$1M+ / unit** | ESTIMATE citing secondary | [MapYourTech DAS overview](https://mapyourtech.com/%cf%86-otdr-vs-das-submarine-cable-acoustic-sensing/) — **not a vendor quote** |
| OptoDAS range / gauge | up to **~150 km**, gauge **2–40 m** | CITED (capability, not price) | ASN OptoDAS sheets; [ASN fiber sensing](https://www.asn.com/fiber-sensing/) |
| DAS data volume (one Arctic experiment) | **~7 TB / day**, ~300 Hz bandwidth, 44 days | CITED | Bouffaut et al. 2022 *Front. Mar. Sci.* [10.3389/fmars.2022.901348](https://www.frontiersin.org/articles/10.3389/fmars.2022.901348) |
| Fiber **access** (landing station, dark fiber, telecom coexistence, permits) | UNKNOWN — often **larger than the box** | UNKNOWN | Partnership / governance |
| Compute/storage for continuous DAS | **$50k–$500k / year / landing** | ESTIMATE | Implied by TB/day |

**Year-1 for oyster cell:** **$0**. Oysters do not advertise on hydrophones. PAM/DAS is a **different taxon class** (mammals, soniferous fish) and a **privacy/MMPA** minefield if published as tracks.

**A “global hydrophone/DAS observatory”:** scientifically exciting for **vocal mammals along cables**; **not** a saltwater-life census. Cost is cable politics + data plumbing, not the microphone.

---

### 2.5 AUV / glider adaptive sampling

**What it can observe:** profiles the model is **most uncertain** about (T, S, optics, sometimes acoustics/cameras/eDNA payload). Adaptive sampling can beat a naive grid **if** the value function is honest (uncertainty, not “go find fish for the heatmap”).

| Item | Band | Label | Source |
| --- | --- | --- | --- |
| 6× Slocum G3 + spares (UK RN) | **£1.8M inc VAT** initial; option to **£3.3M** | CITED | [Find a Tender 011996-2025](https://www.find-tender.service.gov.uk/Notice/011996-2025); ~**£300k / vehicle-equivalent** including spares — ESTIMATE allocation |
| Slocum G3 spare/section line items | **$13.7k–$44.2k** per part | CITED | [USM sole-source notice](https://www.usm.edu/procurement-contract-services/_documents/23031.pdf) |
| Glider at-sea, Europe (GROOM) | **€3k–€30k / month**; Iridium **~€80 / day** | CITED | [GROOM RI D3.2](https://www.groom-ri.eu/wp-content/uploads/2024/04/d3.2.pdf) (marginal vs fully consolidated) |
| Survey-class AUV (REMUS 600 class) | purchase **UNKNOWN** public list; endurance **~70 h** | CITED spec / UNKNOWN $ | [WHOI OSL REMUS 600](https://www2.whoi.edu/site/osl/vehicles/remus-600/) |
| Launch/recovery small boat | **$1k–$8k / day** | ESTIMATE | Site-dependent |
| Dedicated UNOLS-class ship to move robots | **$10k–$40k+ / day** | ESTIMATE on vintage UNOLS class tables | Operator quote required |

**Year-1 oyster cell:** **$0**. Intertidal heat×tide is not a glider problem. A glider in Willapa would mostly measure the wrong boundary layer for emersion mortality.

**When it becomes rational:** offshore / hypoxia / subsurface thermal habitat (Chinook depth refuge; lobster bottom-T) **after** public models and partner sensors fail a named gate. Then **rent/borrow one glider-month ($10k–$50k ESTIMATE ops if a partner owns the vehicle)** before buying a fleet.

**Global adaptive AUV mesh:** physically possible as a **research fleet of hundreds**, **$50M–$500M / decade** ESTIMATE, still sparse vs the ocean’s volume.

---

### 2.6 Satellite tasking (commercial VHR) vs public ocean color / SST

**What satellites can observe today:** SST, ocean color/chlorophyll, fronts, altimetry, waves (scatterometer/altimeter), **surface-visible** megafauna in some conditions, blooms, Sargassum, shallow bright benthos, ships. **Not** most fish at depth. Optical attenuation in water is a physics limit, not a product gap (see physics red-team sibling).

| Item | Band | Label | Source |
| --- | --- | --- | --- |
| Public SST / ocean color / altimetry (CMEMS, NOAA, NASA) | **$0** | CITED | CMEMS licence above; USGov public |
| Planet SkySat archive | **$6 / km²** | CITED | [Planet Support: monitoring vs tasking](https://support.planet.com/hc/en-us/articles/27016165868957-What-s-the-Difference-Between-Monitoring-and-Tasking-Subscriptions) |
| Planet flexible tasking | **$12 / km²**, min **25 km²** | CITED | Same |
| Planet assured tasking | **$40 / km²** | CITED | Same |
| SkyWatch catalog SkySat tasking (indicative Jun 2026) | **$12 / km²** (stereo **$24**) | CITED | [skywatch.com Planet page](https://skywatch.com/geospatial-data-providers/planet/) |
| Maxar/Vantor WorldView | quote / credits; reseller bands often **~$25–$65 / km²** class | ESTIMATE / UNKNOWN official | Public list incomplete; [Maxar tasking docs](https://pro-docs.maxar.com/en-us/Tasking/Tasking_requests_EO.htm) |
| Willapa Bay water area on the order of **~100–300 km²** (planning, not a GIS area of record) | one assured SkySat collect **$1k–$12k** | ESTIMATE | min order 25 km² × $40 = **$1,000** CITED math; cloudy revisits multiply |

**Year-1 oyster cell:** **use public SST as a *covariate*, never as oyster body temperature or abundance.** Do not task VHR. Intertidal mortality in 2021 was an **air-heat × emersion** event (Raymond et al. 2022) — a SkySat picture of the bay does not rank OSI-72.

**When tasking is rational:** surface-visible taxa (some sharks/rays in clear water, whale-slicks research, bloom extent) with a validation plan. Still not a fish census.

---

## 3. Comparison table (one prototype cell, Year-1)

| Stack | Decision it can serve in Willapa oyster P0 | Year-1 $ | Hardware last? | Global fantasy $ | Honest output class |
| --- | ---: | ---: | --- | ---: | --- |
| **Public software twin + partner logs** | 72h ops-stress / work-window | **$0.4–1.2M** ESTIMATE | Yes — this *is* the first stack | N/A (doesn’t globalize) | FORECAST / MODEL-INFERRED + UNKNOWN |
| Partner export of **existing** sonar | Not the oyster decision | **$0.1–0.4M** extra ESTIMATE | Export before buy | UNKNOWN | REMOTELY DETECTED index |
| Buy scientific echosounder + ship | Wrong problem | **$0.5–2M+** | **No — skip** | — | Same, more $ |
| eDNA mesh | Weak for planted oysters | **$0** required; **$8k–$20k** micro-test | After public+partner | **$100M–$1B+** decade ESTIMATE | SURVEY-DERIVED / lab presence |
| Hydrophone / DAS | Wrong taxon | **$0** | Later, other taxa | Cable politics + **$M–$100M+** | DIRECTLY/REMOTELY DETECTED vocalizers |
| AUV adaptive | Wrong boundary layer | **$0** | Later, offshore cells | **$50M–$500M** decade ESTIMATE | DIRECTLY OBSERVED profiles |
| VHR tasking | Wrong physics for emersion heat | **$0** | After public SST fails a *stated* gate | Unlimited and still surface-only | REMOTELY DETECTED surface |

**Information per dollar (P0 oyster cell), ranked:**

1. Partner 30-second outcome logs (nearly free, uniquely the label).  
2. Tide + NWS + existing NANOOS/CO-OPS (already in the grower ritual).  
3. On-lease **existing** thermistor export.  
4. Software that *synthesizes* those into a claims-contract brief.  
5. Everything else is a different observatory.

---

## 4. Recommended Year-1 budget band

**Observatory + first prototype cell, public→partner→existing sensors→manual→mobile, no hardware fleet:**

### **$0.4 – $1.2 million USD (ESTIMATE)**

| Scenario | Band | What you staff |
| --- | --- | --- |
| Lean | **$0.25–0.50M** | Founder-operator + 0.5–1 FTE science/eng + cloud + legal hours + 3 farms |
| **Recommended** | **$0.4–1.2M** | ~2–3 FTE, domain reviewer, rights, replay store, 60–90 day prospective briefs |
| Overbuild (avoid) | **>$2M** | Global catalog theater, DAS, AUVs, foundation-model cluster, multi-taxon UI |

**What the band does *not* include:** ship time, EK80 purchases, DAS interrogators, glider fleets, commercial VHR subscriptions, insurance products, food-safety labs.

**Unit of value:** a **decision-grade, uncertainty-aware brief** for one cell — not km² mapped.

---

## 5. 3-year and 10-year cost envelopes (honesty)

| Horizon | If gates pass | If gates fail |
| --- | --- | --- |
| **Year 2–3** | **$1–4M** ESTIMATE cumulative: keep one operational-ish cell; add **at most 1–2** additional bounded taxa/cells; optional partner-sonar or eDNA *experiments* at **$0.1–0.5M** each | **Stop or restart wedge.** Do not spend the 3-year envelope “because the observatory is global.” |
| **Year 4–10** | **$10–50M** ESTIMATE for a multi-cell scientific network (software + partnerships + a few owned platforms). **$100M–$1B** only if governments/consortia fund **shared observing infrastructure** (cables, IOOS-class, molecular labs) — that is not a startup P&L | A pretty global map with UNKNOWN hatched everywhere is still the correct product |

IOOS/NANOOS/NERACOOS already spent public money on the physical backbone. The observatory’s comparative advantage is **claims + assimilation + unknown maps + partner labels**, not out-observing NOAA.

---

## 6. Cost of false “coverage”

Publishing a smooth global abundance layer is **negative EV**:

- Ecological harm (poaching, harassment).  
- Partner flight (farms, captains).  
- Scientific reputation (SST-as-fish).  
- Legal exposure (harvest/food-safety impersonation).

Price that as **infinite** for v1: **no public global biological heatmap**. Coarsen, delay, restrict, or do not ship.

---

## 7. Deployment path (ops, not science fiction)

```
public covariates (rights-approved)
        ↓
manual brief (14 days)
        ↓
as-of software twin for ONE cell
        ↓
partner outcomes (mobile form)
        ↓
existing on-site sensors if any
        ↓
integrations (email/PDF → later API)
        ↓
STOP unless traction
        ↓
only then: named hardware/micro-mesh experiments
```

Cloud region, SSO, and multi-tenant SaaS are **not** Year-1 cost drivers. Replayability and provenance **are**.

---

## 8. Open cost uncertainties (do not fill with fiction)

- NANOOS provider-level redistribution exceptions (some streams).  
- 2026 UNOLS / charter day rates (request quotes).  
- DAS interrogator + fiber IRU actual invoices.  
- REMUS / ESP current list prices.  
- Willingness-to-pay for the commercial brief (zero interviews as of 2026-09-18).

---

## 9. Pointers

- Plans: `../1_year_plan.md`, `../3_year_plan.md`, `../10_year_plan.md`  
- Coverage honesty: `../global_coverage_roadmap.md`  
- Prototype: `../product_roadmap.md` and blueprint §24  
- UI: `../artifacts/product_cost/sample_evidence_ui_spec.md`
