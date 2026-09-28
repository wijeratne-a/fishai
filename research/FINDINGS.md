# Findings from `research/`

**Read:** 2026-09-23  
**Contents:** 25 PDFs. Twenty-four are articles from *Fisheries Research* volume 109 (2011). One is the journal’s editorial-board page for that volume.  
**What this file is:** a reading note. It does not approve a dataset, fit a model, or change `NOT_PUBLISHED`.

The only paper that describes the Florida reef-fish survey behind the current milestone is Smith et al. (2011). The other articles are a mixed 2011 journal issue. They do not contain a Reef Visual Census extract, a rights grant, or a count of Atlantic goliath grouper.

---

## What matters for the Florida Keys detection nowcast

**Paper.** Smith, S. G., Ault, J. S., Bohnsack, J. A., Harper, D. E., Luo, J., and McClellan, D. B. (2011). Multispecies survey design for assessing reef-fish stocks, spatially explicit management performance, and ecosystem condition. *Fisheries Research* 109(1), 25–41. https://doi.org/10.1016/j.fishres.2011.01.012

**File.** `Multispecies-survey-design-for-assessing-reef-fish-stocks--spa_2011_Fisherie.pdf`

### Design the paper actually specifies

- The sampling domain in this paper is the Florida Keys, from Miami to Key West, and the Dry Tortugas. The stated domain area is 885 km². Southeast Florida from Miami to Martin County is a later NCRMP region. It is not the domain this paper analyzes.
- Habitat and no-take reserve boundaries are used as strata so that fish density varies less inside a stratum than across the whole domain.
- The primary sample unit is a 200 m × 200 m map cell.
- The second-stage unit is a circular plot 15 m in diameter, about 177 m². That is the same stationary plot the NCEI pages describe as a 7.5 m radius cylinder.
- A second-stage unit was usually searched by two divers working as a buddy pair. Later FWC text describes two buddy pairs and four surveys at a site. Those are not the same effort statement. A future extract has to say which rule applies to each year.
- Divers were sent to randomly chosen cells. The paper treats that randomization as the control on where divers choose to look.
- For each species, the survey estimates three different things: the portion of second-stage units where the species was recorded, the mean number per unit, and a domain-wide abundance. Those are not interchangeable.
- Precision reported for 1999–2008 is a coefficient of variation of about 7–20% for most of 13 primary exploited species in the Keys and Dry Tortugas, and about 6–15% for density of most of 36 non-target species. Those figures are for the species the paper highlights. They are not a goliath detection rate.
- The design was adjusted over time. Past surveys changed how later years were stratified and how effort was allocated. A model that pools 1999–2008 as one unchanging protocol would ignore that.

### What this does to the detection target

The useful overlap with the milestone is the sample frame. The paper’s “portion of second-stage units occupied” is an occurrence rate on a completed visual search. That is the same family of target as a detection given documented survey effort.

The paper’s other products are density and abundance for stock assessment and reserve evaluation. Those are outside the milestone. A goliath model must not inherit the abundance estimator, the reserve-effectiveness claim, or a map of sample cells.

The paper does not name *Epinephelus itajara*. Its grouper example in the methods figure is red grouper. Nothing in this PDF verifies that the species code `EPIITAJ` is present in NCEI Accession 0208321, or that zeros are stored in that file.

### What this paper does not unlock

- It is not written permission to train on or display NCEI Accession 0208321.
- It does not identify which archived file is the analysis-ready table, and it does not hash one.
- It does not show a 2018 survey. Its reported precision window is 1999–2008.
- It does not add a second year to the 2018 accession, so it does not create a time-forward test.
- Rights status stays `CONDITIONAL_REVIEW_REQUIRED`. Exit gate stays `BLOCKED`.

---

## The rest of the folder

These papers were read from their titles, abstracts, and opening sections. None is a Florida reef visual-census table. None is used as goliath evidence.

| File stem | Subject | Bearing on the goliath nowcast |
|---|---|---|
| Editorial-Board_2011 | Journal masthead for volume 109 | None. Not a study. |
| A-future-for-marine-fisheries-in-Europe | European fisheries manifesto: lower fishing pressure, restore stocks | Policy essay. Not a survey frame. |
| A-model-of-fishing-periods-applied-to-the-European-sard | Fishing-day limits and TAC risk for European sardine; costs fall unevenly on Portugal and Spain | Management model. Not animal location. |
| Calculating-optimal-effort-and-catch-trajectories | Effort and catch paths for three Australian prawn species under mixed population models | Shows that model form changes the catch trajectory. Not a reef survey. |
| Estimating-natural-mortality-within-a-fisheries-stock-assessmen | Whether natural mortality can be estimated inside Stock Synthesis | Assessment method. Needs age or length composition. Not this milestone. |
| Evaluation-of-methods-for-predicting-mean-weight-at-age | Weight-at-age forecasts for four Northeast Atlantic haddock stocks | Growth forecast. Different species and target. |
| Integrating-imputation-and-standardization-of-catch-rate-data | Filling missing time-area cells before standardizing tuna and billfish catch rates | A warning: commercial catch rates with systematic gaps are a poor abundance index. Not a substitute for the visual survey. |
| Modeling-growth-and-reproduction-of-chilipepper-rockfish | Bioenergetic allocation for female chilipepper under good and poor years | Life-history simulation. Not a detection model. |
| Six-decades-of-pike-and-perch-population-dynamics-in-Wi | Age-structured perch and pike in Windermere | Closed freshwater fishery. Sex-selective fishing can collapse a stock. Not marine survey design. |
| Decline-of-a-blue-swimmer-crab | Cockburn Sound crab fishery closed after recruitment and effort interacted | Environmental edge, method change, and continued fishing during poor years. A cautionary management history, not a data source. |
| Life-history-of-the-meagre-Argyrosomus-regius | Growth and maturity of meagre in the Gulf of Cádiz | Life history from landings. Not effort-aware reef counts. |
| Gonad-development-in-the-commercially-exploited-deepwater-shrim | Ovary stages of a Costa Rican deepwater shrimp | Reproductive staging. Not relevant. |
| Effect-of-netting-direction-and-number-of-meshes-around | T90 and mesh count in Baltic cod codends | Gear selectivity. |
| Refining-a-Nordm-re-grid-for-a-Brazilian-artisanal-penaei | Nordmøre grid in a southern Brazil shrimp canoe trawl | Gear selectivity. |
| Selectivity--efficiency--and-underwater-observations-of-modifie | Escape rings in Newfoundland snow-crab traps | Gear selectivity. |
| The-modeling-of-single-boat--mid-water-trawl-systems | Simulator for a midwater trawl, for crew training | Gear simulation. The paper itself says towing speed was overestimated. |
| On-the-cause-of-premature-FAD-loss-in-the-Maldives | Anchored fish-aggregating-device moorings in the Maldives | Mooring mechanics. Not a biological survey, and not a map of fish. |
| Differences-in-acoustic-target-strength-pattern | Horizontal target strength of six European freshwater fishes | Acoustics. Swimbladder shape changes the echo. Not goliath. |
| Identifying-fish-scales | Scale shape for identifying five fishes, with size effects | Identification method. Not a survey frame. |
| Direct-comparison-of-mitochondrial-markers | Swordfish mitochondrial markers in the Indian and Pacific oceans | Genetics. Control region understated structure relative to ND2. |
| Cephalopods-caught-in-the-outer-Patagonian-shelf | 21 cephalopod species from one 2009 slope trawl survey | A presence list from trawls. No non-detection frame for goliath. |
| Bycatch-of-large-elasmobranchs-in-the-traditional-tuna-traps | Large shark and ray bycatch in Sardinian tuna traps, 1990–2009 | Forty-two recorded events. Opportunistic bycatch, not a designed non-detection survey. |
| Assessment-of-permanent-magnets-and-electropositive-metals | Magnets tested against Galapagos sharks on baited lines | Bycatch-mitigation experiment. Shark behavior changed with the number of sharks present. |
| In-situ-observation-of-stomach-eversion-in-a-line-caught-Sh | One shortfin mako everting its stomach while on a line | Anatomical note. Not a dataset. |

---

## Findings that should change the next data step

1. The protocol citation is now backed by the paper in this folder, not only by a landing-page link. The spatial units to verify in a future table are the 200 m primary cell and the 15 m second-stage plot.
2. The paper already separates occurrence, density, and abundance. The milestone stays on occurrence given search effort. Density and abundance stay out.
3. Effort is not a single number across eras. Buddy-pair versus two buddy pairs, and the paper’s own changes in stratification, have to be fields in the schema check.
4. The 2011 domain is Keys plus Dry Tortugas. A file that also contains Miami-to-Martin or the southeast Florida region is a broader survey than this paper’s analyzed domain. Those regions should not be pooled until the table shows they share the same design.
5. Nothing in the folder clears rights, hashes a data file, or counts `EPIITAJ`. Acquisition remains blocked. No nowcast or forecast is issued.
