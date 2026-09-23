# Recommended initial wedge

**Status: RECOMMENDED, not DECIDED.**  
**Date:** 2026-09-18  
**Agent:** REQUIREMENTS_AND_WEDGE_AGENT  
**Do not copy these values into `INITIAL_*` as facts.** Founder confirmation is required. Until then `config/project_config.json` stays UNRESOLVED.

---

## Recommendation (one paragraph)

Start with **W1**: Pacific oyster (*Magallana gigas*, WoRMS AphiaID 836033) in **Washington Department of Health commercial growing areas of the Willapa Bay system (Pacific County)** for a **commercial oyster farm operator**, whose recurring decision is a **24–72 hour operational stress / disruption / work-window** — whether to mobilize crews, handle or move gear, or delay husbandry because of heat-at-low-tide, wave and wind workability, and temperature / dissolved-oxygen / salinity stress — and **not** whether shellfish are legal or safe to harvest. This is the only candidate that remains a daily operator decision when ocean salmon seasons are closed, that already has official farm-zone polygons, that can be labeled with three permissioned farms rather than a fleet, and that leaks fewer secret capture locations than Chinook or lobster. Public water-quality maps already exist (NANOOS Shellfish Growers); the product is a **confidence-aware work/stress brief**, not another viewer. USDA 2023 Census of Aquaculture records 114 Washington Pacific oyster farms and $106.801 million in sales; PSI documents 20–80% summer mortality in multiple Washington growing areas; the 2021 heat dome plus extreme low tides is a peer-reviewed mass-mortality mechanism. Willapa is recommended over “all Washington growing areas” or South Puget Sound because Pacific oyster historically dominates Willapa production and the geography is a single estuary with a named CO-OPS station (Toke Point 9440910). If the founder already has South Puget Sound farm access, swap **only** the polygon set — keep species, customer, and decision.

---

## Why W1 over W2 and W3

| Reason | Evidence | Implication |
| --- | --- | --- |
| Decision still exists if a fishery closes | CA ocean salmon **fully closed** 2023 and 2024 (PFMC/NMFS; 2024 disaster 100% revenue loss) | A Chinook charter product can have **zero** addressable days |
| Ground truth can start with 3 firms | Farm bags/beds are fixed; PSI already runs a voluntary mortality form (research-only) | Faster than 5–8 mobile capture businesses |
| Official geography | WA DOH growing-area classifications and 2025 annual reviews | No need to invent a grid that looks like a secret-spot map |
| Public covariates exist | NANOOS NVS Shellfish Growers; CO-OPS; NWS; Copernicus SST (credit required) | Baseline rules (tide × air/water heat; wave threshold) are feasible **after** rights approval |
| Privacy blast radius | Lease/farm performance is private but not a competitive “hole” in the same way as trap GPS | Still PRIVATE by default; still better than W2/W3 public maps |
| Documented biological pain | Raymond et al. 2022 *Ecology*; WSG Rapid Response; PSI 20–80%; WDFW 2018 grower reports (other basins) | Stress events are real; **farm-level WTP is still untested** |

W2 is the right wedge **if and only if** the founder has Oregon (or a single open 2026 CA zone) charter captains ready to log trips. W3 is the right wedge **if and only if** a Maine co-op will share coarsened haul CPUE. Those are relationship-gated. W1 is the default when relationships are also UNRESOLVED.

---

## What the founder must confirm (W1-specific)

Copy answers into `config/project_config.json`. Until then, nothing is locked.

1. **Accept W1** (or reject in favor of W2/W3 with a reason).
2. **Geography lock:** Willapa Bay DOH growing areas (recommended) **or** a named South Puget Sound growing-area set. Name the polygons.
3. **Customer title:** farm manager vs owner vs crew lead vs hatchery (hatchery is a different decision — reject for v0).
4. **Culture method in scope:** intertidal bag / on-bottom / floating. Heat-at-low-tide only applies if intertidal exposure exists. If the design partners are all subtidal floats, the work-window physics change — say so.
5. **Life stage:** grow-out only (recommended) vs seed/nursery. PSI notes second-year near-market animals in summer mortality.
6. **Ploidy:** diploid, triploid, or both. PSI’s SK grant is triploid-focused; do not silently mix labels.
7. **Primary outcome metric (pick one):**
   - **A.** Binary: stress/disruption event in 72h (mortality jump above farm’s own baseline, or forced postponement).
   - **B.** Workable window: crew can **workably / productively** work the tide (tide + wind/wave + heat) — operational, not biological, **not safety-certified**, not weather-safety advice.
   - **C.** Mortality band (e.g. 0–5% / 5–20% / >20% of counted bags) — needs honest counts.
8. **Forbidden output acknowledged:** FishAI will never state that shellfish are safe, legal, or approved to harvest. DOH URLs only.
9. **Pilot farms:** names or “none — need introductions via PCSGA / WSG / PSI.”
10. **Delivery:** SMS / WhatsApp / email / PDF. Not a multi-tab terminal.
11. **Storage region / security:** UNRESOLVED until answered.
12. **Interviews authorized?** Yes/no, and any operators who must not be contacted.

---

## Proposed (not decided) Section 2 fill if founder accepts W1 + Willapa

These are **recommendations** for the founder to paste after approval:

| Field | Recommended value |
| --- | --- |
| PROJECT_NAME | FishAI |
| FOUNDER_OR_ORGANIZATION | still UNRESOLVED until founder types it |
| INITIAL_SPECIES_COMMON_NAME | Pacific oyster |
| INITIAL_SPECIES_SCIENTIFIC_NAME | Magallana gigas (Thunberg, 1793) |
| INITIAL_TAXONOMIC_AUTHORITY | WoRMS |
| INITIAL_WORMS_APHIAID_OR_TAXON_ID | 836033 (also index 140656) |
| INITIAL_LIFE_STAGE_IF_RELEVANT | Farmed grow-out, mixed ploidy until partners specify |
| INITIAL_GEOGRAPHY | WA DOH commercial growing areas, Willapa Bay system, Pacific County |
| GEOGRAPHY_BOUNDARY_FORMAT | DOH growing-area polygons, EPSG:4326 |
| TARGET_COUNTRY_OR_JURISDICTION | USA / Washington |
| INITIAL_CUSTOMER_SEGMENT | Commercial Pacific oyster farm operator |
| INITIAL_USE_CASE | C. Shellfish-farm operational risk forecast |
| INITIAL_PRIMARY_DECISION_TO_IMPROVE | 24–72h stress / disruption / work-window |
| DECISION_FREQUENCY | Daily in May–September; event-driven otherwise |
| FORECAST_HORIZON | 24–72 hours |
| SPATIAL_RESOLUTION_TARGET | Growing area / private lease zone; public maps coarsened |
| TEMPORAL_RESOLUTION_TARGET | Hourly covariates; daily brief |
| PRIMARY_OUTCOME_METRIC | UNRESOLVED — founder picks A/B/C above |
| TARGET_PRODUCT_DELIVERY_FORMAT | Daily email or SMS brief (recommended) |
| REGULATORY_OR_SAFETY_CONSTRAINTS | Not food-safety, not navigation, not weather-safety advice |

---

## What this recommendation is not

- Not a claim that Willapa farms will pay.
- Not a claim that NANOOS data may be commercialized without checking each provider (NANOOS DMP: some streams have redistribution exceptions).
- Not permission to ingest.
- Not a site-suitability product (use case D) and not a closure-risk product that impersonates DOH.
- Not expansion to Manila clam, Kumamoto, or geoduck.

---

## First experiment after founder approval (do not run now)

Smallest valid experiment: **one manual 72h work/stress brief for one Willapa farm for 14 days**, using only **attributed official** tide + NWS + any grower-visible NANOOS values the farm already uses, plus a 30-second outcome form (worked Y/N; mortality noticed Y/N). Compare to the farm’s current “look at tides and the buoy” workflow. No ML. No new sensors. Stop if the farm would not change a crew call.

---

## Confidence

**Medium** that W1 is the best *starting* wedge among the three.  
**Low** that W1 is commercially viable — interviews have not happened.  
**High** that locking all Washington, or mixing food-safety into the label, would violate the north-star.
