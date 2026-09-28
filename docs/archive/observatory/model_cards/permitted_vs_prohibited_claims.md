# Permitted vs prohibited user claims

**Owner:** Species Model Cards and Scientific Model Governance  
**Date:** 2026-09-18  
**Status:** Binding copy source for Species Model Cards and for globe `claim_pack`.  
**Authority:** `artifacts/scientific_red_team/prediction_contract.md` (only approved claim language). This file **does not loosen** that contract.  
**Wedge:** UNRESOLVED. Packs exist so later UI cannot invent stronger sentences.

Product, sales, and globe agents may shorten layout. They **may not strengthen meaning**. Only a **named human domain reviewer** may add sentences.

Claim-pack ids bound on the draft cards:

| Pack id | Card |
|---|---|
| `claim_pack_W1_oyster_ops_D_v0` | `SMC-W1-OYSTER-OPS-RISK-v0-DRAFT` |
| `claim_pack_W2_chinook_encounter_C_v0` | `SMC-W2-CHINOOK-ENCOUNTER-v0-DRAFT` |
| `claim_pack_W3_lobster_cpue_C_v0` | `SMC-W3-LOBSTER-CPUE-v0-DRAFT` |

Until a card is `PUBLISHED` and `OPERATIONAL`, even **permitted** sentences must not be issued as live scores. They may appear only as SPEC examples with `NOT_PUBLISHED` chrome.

---

## Universal never-claims (all wedges, all channels including decks)

These must never appear:

- Exact counts of wild animals in an unsurveyed cell.
- “AI abundance,” “biomass,” “the stock is up/down/healthy here.”
- AIS, VMS, GFW, vessel density, or tracker pings as fish/lobster abundance.
- SST or chlorophyll as proof of presence, abundance, safety, or legality.
- Social media, forums, or unverified photos as confirmed presence.
- Guarantee of catch, harvest, survival, yield, or revenue.
- Legal fishing authorization; remaining quota as if official.
- Navigation or weather-safety advice (“it is safe to go”).
- Medical, regulatory, or environmental certification.
- Commands: “fish here,” “harvest now,” “set gear on this waypoint,” “eat these oysters.”
- Three-decimal biological probabilities; 100 m “hotspot” maps as truth.
- Silent edits to past forecasts; evaluation that uses data not available at issuance.

Confidence, if ever issued: **High / Medium / Low / None** only. No calibrated-looking percentages until a human accepts a calibration plot from **prospective** data. Ranks, not fake counts.

---

## W1 — Pacific oyster × WA × 72h ops stress

**Pack:** `claim_pack_W1_oyster_ops_D_v0`  
**Category:** **D** (operational disruption / environmental-stress **indicator**).  
**Ceiling:** not stronger than the strongest evidence tier on that output. SST-only ⇒ Low or None.

### Permitted (if a future published card exists; not live today)

- Rank of **physical/operational stress conditions** relative to **this permissioned lease**, comparable tides/season.
- Inputs named as inputs: air temperature, tide/emersion, wind/wave, in situ T/S/DO — not “caused by SST.”
- Options, not commands: “Consider shifting labor off the hottest emersion; inspect gear after wave event; increase monitoring.”
- Separate **official context** module: WA DOH growing-area / biotoxin / Vp control status with authority, timestamp, jurisdiction, source URL, boundary, last-verified time. If stale: “Official status not verified — do not harvest on the basis of this brief.”
- Evidence badge: `Evidence: Tier [1–4] · Category D · [High/Medium/Low/None] confidence`.

**Approved paragraph (only after publish gates; still not food-safety):**

> Elevated **operational stress indicator** for Lease [ID] over the next 72 hours, associated with forecast air temperature overlapping daytime emersion and [wave/wind] exposure. Comparison set: this lease, similar tides, [season]. Confidence: [Low/Medium/High]. Category D. Strongest evidence: [Tier 1 sensors / Tier 2 farm log / Tier 3 forecast only]. **This is not a food-safety determination and not harvest authorization.** Verify official growing-area and biotoxin status with the Washington State Department of Health (and tribal or FDA authorities where applicable). Satellite temperature is not oyster body temperature and is not a tissue toxin test. It does not replace the *Vibrio parahaemolyticus* control plan (WAC 246-282-006).

### Prohibited (oyster)

- Food-safety: “safe to eat,” “safe to harvest,” “legal to harvest.”
- Harvest authorization; NSSP / FDA / WA DOH / ISSC “meets requirements.”
- Model output of growing-area **open** or **closed**.
- “No *Vibrio* / no PSP / no DSP / no ASP / toxin-free / below action level.”
- Combined green/red score mixing ops stress with sanitation.
- Another farm’s mortality, yield, or lease polygon without permission.
- SST or satellite temperature as oyster **body temperature**.
- Abundance, biomass, wild-set census, bay-wide “oyster count.”
- “Harvest now,” “harvest window” as a **model** output, “eat these oysters.”
- SST ≥ 19 °C for ≥12 h as a WA mortality law (growth band, wrong variable; B-SIB-01).
- Weather-safety: “crew can safely work the tide.”
- Percent mortality to false precision; Totten / Vp Category 3 demo geography; “rank ~top 20%.”

Any sentence a reasonable operator could read as “you can sell these oysters” is prohibited.

---

## W2 — Chinook × CA/OR × 24–48h relative encounter

**Pack:** `claim_pack_W2_chinook_encounter_C_v0`  
**Category:** **C** preferred (effort-normalized encounter **rank**); **D** only if explicitly habitat/encounter **risk**, not a 48h census.  
**Horizon note:** 24–48h as a product window is allowed **only** for partner-log rank vs comparable **open** days, or an explicitly labeled seasonal climatology. **Environmental identification of 24–48h encounter is not identified** (RT-CHK-01 / B-CHK-01 **BLOCKER** for habitat-style / SST-chl models). That identifiability failure is a blocker; the horizon clock itself is not an independent extra blocker if the target stays Category C rank from logs.

### Permitted (if a future published card exists; not live today)

- Relative CPUE **rank** (lower / middle / upper tercile) vs comparable **open-season** days in a **named** PFMC/CDFW/ODFW management area, from **partner** trip logs with effort.
- Hard mask: closed or unverified regulation ⇒ **None**: “No encounter score. Fishery closed or status unverified. See NMFS/CDFW/ODFW.”
- Options: “Consider trip timing consistent with your usual grounds.” Never waypoints.
- Weather as **trip-feasibility confounder**, not “fish are here.”
- Mixed-stock disclaimer (conservation limits exist).

**Approved paragraph:**

> **Relative CPUE rank** for ocean Chinook in [management area] over the next 24–48 hours: [lower/middle/upper] third of comparable **open** days in our partner-log comparison set. Confidence: [Low/Medium]. Category C. Strongest evidence: Tier 2 charter logs (not a survey). **Not an abundance estimate and not a catch guarantee.** Not legal advice, not a license, not navigation, not weather-safety advice. Check NMFS, CDFW, and/or ODFW in-season regulations before leaving the dock. Closed areas are not scored. Chinook in this area are a mix of stocks, including units with conservation limits.

SST/chl-only ⇒ **None** (do not issue). Partner logs with effort ⇒ at most **Medium** in v1.

### Prohibited (Chinook)

- “You will catch fish,” “limits tomorrow,” “the bite is on at this lat/lon.”
- “Abundance is high in this cell.”
- A score on a **closed** area.
- Fine-scale public spot maps; listed-stock targeting language.
- Recreational retained catch described as a scientific abundance survey.
- Heatmaps titled “where the fish are”; “72% chance of limits.”
- Habitat-style 24–48h SDM from SST/chlorophyll/currents as an encounter product (not identified; **BLOCKER**).
- Juvenile chlorophyll-nearshore papers or NWFSC stoplight indicators as adult 48h bite.
- AIS of CPFVs as fish location.
- Social “limits” posts as labels.
- ~10 km / H3-6 public product cell as truth.

---

## W3 — American lobster × GOM × next-trip CPUE

**Pack:** `claim_pack_W3_lobster_cpue_C_v0`  
**Category:** **C** — expected **legal catch per defined effort** (default: per trap-haul) for the **operator’s own** footprint.  
**Scientific non-negotiable:** **catch ≠ abundance.** AIS is **banned** as abundance, as a public effort layer, and as a default training feature.

### Permitted (if a future published card exists; not live today)

- Effort-normalized catch **rank** vs **this operator’s** comparable trips (season, soak band, zone).
- Bottom temperature, soak, bait as **catchability inputs**, not “more lobsters.”
- Options: “Consider which of *your* strings to haul given soak.” Never “set 2 nm east.”
- Exact locations stay private.

**Approved paragraph:**

> **Effort-normalized catch rank** for legal American lobster on **your** gear in [zone], next haul window: [lower/middle/upper] tercile of your comparable trips with similar soak. Confidence: [Low/Medium]. Category C. Strongest evidence: Tier 2 logbook. **This is not abundance.** Catch rates move with temperature-dependent catchability, soak, bait, molt, and regulations even when local density is unchanged. AIS and vessel traffic are not lobster density and are not used here. Exact locations stay private. Not legal, navigational, or entanglement advice. Check Maine DMR / ASMFC / NOAA rules.

High confidence is **never** in v1 without prospective calibration. Missing soak/bottom T ⇒ Low.

### Prohibited (lobster)

- “This AIS hotspot is where the lobsters are.”
- “CPUE up means the stock is up” / cell-level abundance.
- Public maps of strings, high-CPUE cells, or tracker paths.
- Guaranteed landings, price, or haul.
- Advice to set on another operator’s gear.
- GFW / VMS / Addendum XXIX tracks as abundance or public effort.
- SST as lobster habitat-now or as bottom temperature.
- Soak-unnormalized landings called CPUE.
- Recommending unfished cells / new ground.
- Public choropleth of “hot cells.”

---

## Amendment

Software agents may only **tighten** this file. Adding a permitted sentence, or deleting a prohibited sentence, requires a named human domain reviewer, date, and scope recorded on the successor card.
