# Product Thesis — Ocean Intelligence Builder / FishAI

**Agent:** PRODUCT_AND_MONETIZATION_AGENT  
**Date:** 2026-09-18  
**Project state:** Wedge **UNRESOLVED**. This document designs three candidates and **recommends** a first commercial test. It does **not** lock species, geography, customer, or decision. Interviews have **not** been conducted; traction numbers below are a **plan**, not evidence.

**Recommended first commercial test (RECOMMENDED, not DECIDED):** Pacific oyster × **Willapa Bay** WA DOH growing areas × farm operator × **72-hour Category D operational stress / work-window brief** (not food-safety, not harvest authorization, not Vp).

**Recommended MVP format:** Daily **email + 1-page PDF** (WhatsApp/SMS only as an “elevated” ping). One valuable answer in under 60 seconds.

**Claims halt (2026-09-18):** Marine domain, quality/validation, product, and scientific red-team **agree** there is **no** approved customer-facing **model** claim. After a founder wedge lock, the only allowed commercial test is a **manual** decision brief. Sample copy below is **format-only**, unvalidated, and must not be forwarded as a forecast.

---

## 1. Company thesis (product translation)

The long-term vision is a trusted intelligence layer for biological, environmental, operational, regulatory, and commercial ocean conditions. That is **not** the MVP.

The MVP is:

> One species × one geography × one customer type × one recurring decision, delivered as a **safe, uncertainty-aware brief** the customer can act on tonight.

Flywheel that must be designed from day one (not a later “data moat” slide):

1. A forecast or risk score that is **better than the customer’s current 10-minute ritual** (NANOOS + weather + tides + tribal knowledge).
2. A decision they actually make (crew, gear, handling, which lease to work).
3. They log what happened in **30 seconds**.
4. Permissioned private outcomes improve **their** next brief.
5. Trust and switching costs rise. Only then expand.

If the product cannot beat a bookmark folder of free government pages, it is not a product.

---

## 2. Non-negotiable product rules

- Do **not** design a global multi-tab marine terminal.
- Every customer-facing output must contain the **14 product-output-contract fields** (Section 7).
- Suggested actions are **OPTIONS**, never commands.
- Claims stay inside the prediction-contract class for that wedge (relative operational-stress indicator, relative encounter likelihood, or effort-normalized CPUE) — never abundance counts, catch guarantees, or official harvest legality.
- Exact fishing spots and farm performance are **private by default**.
- Hardware is out of scope until partner sensors, public data, and manual logs are proven inadequate.

---

## 3. Three candidate products

### Candidate A — Oyster farm 72h ops-risk brief (RECOMMENDED)

| Field | Specification |
|---|---|
| Species | Pacific oyster (*Magallana gigas* / *Crassostrea gigas*) |
| Geography | **Recommended (not decided):** WA DOH commercial growing areas in the **Willapa Bay system** + named private lease/zone. **Do not** demo Totten / Vp Category 3 as if it were a harvest-control product. |
| Customer | Farm owner / farm manager / crew lead (B2B operations) |
| Recurring decision | In the next 72 hours, which leases need extra monitoring, delayed handling/tumbling, extra gear lashing, or crew reallocation? |
| Horizon | 72 hours, issued daily (evening, local) |
| Target class | Relative **operational stress / disruption** indicator vs comparable historical periods at that lease |
| **Must not become** | Food-safety determination, Vibrio control, biotoxin closure, NSSP classification, harvest authorization, mortality **guarantee** |
| v0 data (no model required) | **Primary:** NWS air + CO-OPS tides/emersion + wind/wave. **Supporting:** NANOOS/NVS in situ T/DO/S with lag/mismatch labeled. Optional partner sensors. SST is not body temperature. |
| Ground truth | Partner workability, handling completed Y/N, observed stress/mortality/fouling/gear damage — **not** WDOH closure as a food-safety label |
| Delivery | Email + PDF; optional WhatsApp if status = Elevated |
| Why it can sell | Year-round (or long-season) operations; labor is a dominant cost; heat, hypoxia, freshwater, and wave events have real P&L; one farm can pay for several leases |
| Why it can be built small | A human can assemble the first briefs from public nowcasts + a lease profile; no map product, no ML, no AIS |

Washington shellfish aquaculture is a real buyer market: a 2025 legislative assessment reported **$252.5 million** in 2023 sales and **$416 million** total economic impact. Growers already consume NANOOS NVS Shellfish Growers, WDOH temperature maps, and SoundToxins — all **free**. The commercial gap is **not** “ocean data exists.” The gap is a **lease-specific, forward 72h, ops-not-safety brief** with a claims contract and an outcome loop.

### Candidate B — Chinook charter 24–48h encounter brief

| Field | Specification |
|---|---|
| Species | Chinook salmon (*Oncorhynchus tshawytscha*) |
| Geography | One bounded CA/OR coastal cell set (harbor + operating range), coarsened |
| Customer | Charter captain / small fleet |
| Recurring decision | Given that the season is legally open, how do the next 24–48h rank for **relative encounter conditions** vs comparable historical trips in this operating range? |
| Horizon | 24–48 hours, issued the evening before and morning-of |
| Target class | Relative encounter likelihood / condition rank — **not** abundance, **not** catch count |
| **Must not become** | Catch guarantee; navigation; weather-safety; licensing; in-season quota advice; public spot map |
| v0 data | **Customer-facing model halted.** Later research only: open/closed mask + partner-log climatology + optional weather-workability as a **confounder** (not “fish are here”). SST/chlorophyll/currents are **not** 24–48h encounter features. |
| Ground truth | Effort-normalized catch / no-catch from partners — **never AIS as abundance** |
| Delivery | WhatsApp/SMS + PDF (captains live on phones) |
| Why it looks attractive | Fast trip cadence; easy dock interviews; obvious “will I fill the boat?” pain |
| Why it is a worse **first** commercial test | 2023–2026 West Coast Chinook opportunity has been highly constrained and in-season closures are routine (e.g. KMZ commercial closed in 2026; recreational Chinook retention bans in subareas). A product with **zero legal fishing days** cannot collect outcomes or charge. Consumer fishing apps already sell forecasts at **~$80–$200/year**. Legal/safety landmines (catch guarantee, nav, weather) are high. Exact-spot privacy is a sales blocker. |

### Candidate C — Lobster next-trip CPUE / effort brief

| Field | Specification |
|---|---|
| Species | American lobster (*Homarus americanus*) |
| Geography | One Gulf of Maine statistical area / DMR zone, coarsened |
| Customer | Commercial owner-operator (later: co-op, buyer, processor) |
| Recurring decision | For my next trip, how should I think about expected **CPUE / soak-effort** vs my own recent baseline and zonal conditions — not where everyone else’s traps are |
| Horizon | Next trip (typically 24–96 hours) |
| Target class | Expected effort-normalized CPUE **relative to the vessel’s own history** and a coarse zonal baseline |
| **Must not become** | Abundance map; public trap map; AIS-as-stock; quota advice |
| v0 data | NERACOOS buoys, NWS, DMR zonal landings (coarse, lagged), **partner haul logs** |
| Ground truth | Partner landings + trap-hauls / soak; Maine DMR harvester survey is confidential/sampled and not a substitute for a vessel log |
| Delivery | Email/PDF or WhatsApp night-before |
| Why it can be a large business | Maine lobster was **~$461 million** ex-vessel in 2025 (preliminary DMR); bait, fuel, and trip count are real costs (DMR noted ~21,000 fewer trips YoY in 2025) |
| Why it is a worse **first** build | Labels require private haul-level data. Operators are territorial. GFW AIS is **non-commercial without a custom license** and is **not abundance**. GMRI already publishes a **seasonal timing** forecast — different product, but it occupies “lobster forecast” mindshare. Scientific bar (effort confounding, soak, bait, molt timing) is high. Sales cycle is slower than a farm email. |

---

## 4. Recommendation scorecard (commercial testability × build cost)

Scores are **hypotheses for ranking**, not interview evidence. Scale: 1 = hostile, 5 = favorable for a 30-day paid-signal test.

| Criterion | A Oyster 72h | B Chinook 24–48h | C Lobster CPUE |
|---|---:|---:|---:|
| Recurring decision even if biology is noisy | 5 | 2 (season/closure gated) | 5 |
| Buyer can write a check (B2B P&L) | 4 | 2 | 4 |
| v0 possible as **manual brief** from public + 1 partner | 5 | 3 | 2 |
| Crowding by cheap/free substitutes | 3 (NANOOS/WDOH/SoundToxins) | 1 (Fishbrain, FishTrack, ODFW reports) | 3 (GMRI phenology, DMR, NERACOOS) |
| Legal / safety / claims landmines | 3 (must stay off food-safety) | 1 (catch, nav, weather, license) | 3 (confidential landings, gear maps) |
| Outcome-log latency | 4 (72h + weekly mortality) | 5 **when open** | 4 |
| Partner-data hardness | 3 | 3 | 1–2 |
| 30-day interview access | 4 (PCSGA, Sea Grant, known farms) | 5 (docks) | 3 |
| 90-day paid-recurring plausibility | 4 | 2 | 3 |
| **Commercial-test score (sum)** | **35** | **24** | **~31** |

**Most sellable with least build, and most commercially testable first: Candidate A.**

Candidate C is the strongest **second** wedge if oyster WTP fails (NANOOS “good enough”) but partner logbooks can be signed. Candidate B is a **research/interview** stream, not the first paid product, unless a captain cluster has a stable open season **and** will pay above consumer-app prices for a coarsened, non-spot brief — which should be treated as unlikely until proven.

---

## 5. Why oyster is the first product (plain language)

1. **One answer, one night.** A farm manager already plans tomorrow’s tide window in email/text. A one-page 72h ops-risk brief fits that ritual. A terminal does not.
2. **Public data is enough for v0.** Temperature, salinity, DO, waves, wind, rain, and tides exist. The first 30 days can be **analyst-assembled** briefs. That is the smallest valid commercial experiment.
3. **The customer is a business**, not a hobbyist. Labor is widely cited as a majority operating cost for oyster farms; heat-stress handling, storm lashing, and skipped work windows are dollar decisions.
4. **The season does not zero the product.** Chinook opportunity can disappear by regulation. Oysters still sit on the lease.
5. **Differentiation is claims + lease + loop**, not a new satellite. We will not pretend NANOOS does not exist. We will productize the **decision** NANOOS does not finish: “for *this* lease, next 72 hours, relative ops stress, here is what it is not, here is how to tell us if we were wrong.”

**Falsifiers (if any one is true after 30 days, do not scale oyster):**

- Three design partners say they already get this from NANOOS + a weather app and would not pay.
- They only want **harvest-legal / Vibrio / HAB** guidance (we must refuse that product).
- They will not log outcomes even with incentives.
- Domain reviewer says the 72h ops-stress target is not scientifically separable from food-safety in customer language.

---

## 6. Minimum lovable output (all wedges)

In **under 60 seconds** the user must see:

1. What changed?
2. What may happen next (horizon)?
3. Why (drivers)?
4. How confident?
5. What to **consider** doing (options)?
6. What the product is **not** allowed to mean (safety/regulatory boundary)?
7. How to report what actually happened?

Allowed v0 formats: daily/weekly email, SMS, WhatsApp, PDF, simple mobile-first map, minimal dashboard, API, spreadsheet.  
**Chosen for oyster:** daily email + PDF. Map/dashboard/API only after paid pull.

---

## 7. Product-output-contract (mandatory 14 fields)

Every customer-facing output, including WhatsApp pings that deep-link to the PDF, must include:

1. **Species and geography scope**
2. **Target definition**
3. **Forecast horizon**
4. **What the prediction means**
5. **What it does NOT mean**
6. **Data freshness**
7. **Confidence and uncertainty**
8. **Relevant inputs / drivers**
9. **Known missing inputs**
10. **Source attribution / provenance**
11. **Regulatory / safety disclaimer**
12. **Suggested action OPTIONS, not commands**
13. **Outcome-reporting mechanism**
14. **Error / feedback mechanism**

Safe language patterns — **only** the scientific red-team contract (`artifacts/scientific_red_team/prediction_contract.md`). Do not strengthen:

- Fish (Category C, if ever issued): *“Relative CPUE rank for ocean Chinook in [named open management area] over the next 24–48 hours: [lower/middle/upper] third of comparable open days in the partner-log comparison set. Confidence: [Low/Medium]. Not an abundance estimate and not a catch guarantee. Not legal advice, not a license, not navigation, not weather-safety advice. Closed areas are not scored.”*
- Shellfish (Category D): *“Elevated operational stress indicator for Lease [ID] over the next 72 hours, associated with forecast air temperature overlapping daytime emersion and [wave/wind] exposure. Comparison set: this lease, similar tides, [season]. Confidence: [Low/Medium/High]. Category D. This is not a food-safety determination and not harvest authorization. Satellite temperature is not oyster body temperature and is not a tissue toxin test. It does not replace the Vibrio parahaemolyticus control plan (WAC 246-282-006).”*

---

## 8. Sample format brief (recommended candidate) — NOT a live forecast

**STATUS: SAMPLE / FICTIONAL / NOT VALIDATED / NOT A MODEL SCORE.**  
No real farm performance is disclosed. **Do not send this to customers.** This is a **layout** of a Category D **manual** ops-stress / work-window brief after founder lock. Totten Inlet and other 2026 WA DOH Vp Category 3 areas are **forbidden** as demo geography (temperature there is already a legal harvest-control variable).

**Visible limitations (always above the fold):**

- No model has been trained. Rank bands in this mock are **illustrative terciles**, not calibrated probabilities.
- Air × tide × solar is **not** oyster body temperature. SST / DO / salinity, if shown, are **supporting covariates** with lag and spatial mismatch.
- This is **not** food-safety, **not** harvest authorization, **not** Vp/NSSP, **not** percent mortality, **not** weather-safety or navigation.
- Evidence: Tier 3 forecast-only · Category D · **Low** confidence (no on-lease sensors). SST-only issuance would be **Low** or **None**.

---

### FISHAI OPS-RISK BRIEF — SAMPLE (format only)

**Product:** 72-hour Pacific oyster **operational stress / work-window** brief (Category D)  
**Issued:** 2026-09-18 23:00 UTC (16:00 PDT)  
**Brief ID:** `OY-WA-SAMPLE-2026-09-18-B`  
**Valid for action planning:** 2026-09-18 16:00 PDT → 2026-09-21 16:00 PDT  
**Extrapolation flag:** Yes — off-lease public stations, no partner labels, no calibration.

**Headline (read this in 15 seconds):**  
Elevated **operational stress indicator** for Lease Zone B over the next 72 hours, associated with forecast **air temperature overlapping daytime emersion** and **wave/wind** exposure. Comparison set: this lease, similar tides, late-summer season. Confidence: **Low**. Category D. Strongest evidence: **Tier 3 forecast only**. **This is not a food-safety determination and not harvest authorization.** Verify official growing-area and biotoxin status with the Washington State Department of Health (and tribal or FDA authorities where applicable). Satellite temperature is not oyster body temperature and is not a tissue toxin test. It does not replace the *Vibrio parahaemolyticus* control plan (WAC 246-282-006).

---

| # | Contract field | This brief |
|---|---|---|
| 1 | Species / geography scope | Pacific oyster (*Magallana gigas* / *Crassostrea gigas*), **Washington DOH commercial growing areas in the Willapa Bay system (Pacific County)** — Nahcotta-adjacent analog, **private Lease Zone B** (intertidal longline / tumble-bag). **Not** Totten Inlet or any Vp Category 3 harvest-control area. Other leases on this farm: not in this brief. |
| 2 | Target definition | Category **D** 72h **operational disruption / environmental-stress indicator** (workability, emersion-heat exposure, wave/gear). **Not** a count of dead animals, **not** a harvest window, **not** NSSP classification. |
| 3 | Horizon | 24–72 hours from 2026-09-18 16:00 PDT (UTC + local tide clock). Update cadence: daily by 16:30 PDT; re-issue if NWS coastal headline or tide clock steps. |
| 4 | What it means | Rank of **physical/operational stress conditions** vs this lease’s comparable tides/season: **upper tercile** of that comparison set (not “top 20%,” not a probability, not a count). Interpretation: handling or unsecured gear would overlap a **higher-than-typical work-stress window** — **not** that mortality will occur. |
| 5 | What it does **NOT** mean | Not food safety; not harvest legality; not NSSP classification; not toxin absence; not guaranteed survival or yield; not other farms; not weather-safety (“safe to work”); not navigation; not oyster body temperature. |
| 6 | Data freshness | NWS coastal/air forecast: **as-of 2026-09-18 21:00 UTC**. NOAA CO-OPS tide (Toke Point 9440910 analog): harmonic as-of **2026-09-18**. Partner sensor: **none**. In-situ water T/DO/S: nearest public station **stale relative to the lease** (off-lease). **Official WDOH status last-verified:** 2026-09-18 22:10 UTC (**separate module**, not a model input). |
| 7 | Confidence / uncertainty | **Low** (allowed labels: High / Medium / Low / None only). No on-lease air/emersion logger. Public water station is off-lease. No farm outcome history. **Do not print calibrated-looking percentages.** |
| 8 | Drivers (inputs, not “caused by SST”) | **(1) Primary:** forecast **air** overlapping **daytime low-tide emersion** Sat–Sun, with solar geometry as an input — **not** SST as body temperature. **(2) Primary:** forecast **wind/seas** above this lease’s easy-work rule of thumb (workability). **(3) Supporting only:** nearest-station water T / DO / salinity with **documented lag and spatial mismatch** — shown as context, not as a kill law and not as a one-decimal “anomaly.” |
| 9 | Known missing inputs | Ploidy; culture-type detail beyond “intertidal”; handling history; disease; HAB toxin (always missing from this model); on-lease T/DO/air; last 14 days mortality/gaping; bag density; crew plan already booked. |
| 10 | Source attribution / provenance | NWS forecast; NOAA CO-OPS tides (Toke Point); optional NANOOS/IOOS in situ as supporting covariate; WDOH Commercial Shellfish Map Viewer **linked, not modeled**. Rule/analyst version: `SAMPLE-FORMAT-2026-09-18-B`. Licenses: pending DATA_RIGHTS ingest approval — this sample **ingests nothing**. |
| 11 | Regulatory / safety disclaimer | **Hard WA DOH wall:** this brief does not authorize harvest and does not mix ops-stress with sanitation. Follow WAC 246-282-006 and official growing-area / biotoxin status. Weather, tides, and on-water safety remain the operator’s responsibility. **If official status is stale:** “Official status not verified — do not harvest on the basis of this brief.” |
| 12 | Suggested action **OPTIONS** (not commands) | **A.** Consider shifting labor off the hottest daytime emersion. **B.** Consider increasing monitoring (gaping, bag movement) on the daylight tide. **C.** Consider inspecting gear after the forecast wave/wind event. **D.** Keep the current plan if your on-lease read disagrees. **Choose none of the above** if official DOH status, your Vp plan, or your own observations disagree. Never “harvest now.” |
| 13 | Outcome-reporting mechanism | 30-second form: worked this tide? Y/N; workability (ok / hard / aborted); observed protocol mortality count if any; gear loss Y/N. |
| 14 | Error / feedback mechanism | Reply “WRONG” + one sentence, or tap Report an error (wrong tide timing / wrong lease / stale DOH / sounds like harvest advice). Human ack: next business day. |

**Official growing-area / biotoxin / Vp status (MODULE B — not a model, not combined with Module A):**  
Authority: Washington State Department of Health. Jurisdiction: named Willapa growing area. Source URLs: [Commercial Shellfish Map Viewer](https://fortress.wa.gov/doh/oswpviewer/index.html) and [Growing Area Closures](https://fortress.wa.gov/doh/eh/portal/odw/si/GrowingAreaClosures.aspx). Geographic boundary: the official DOH polygon, not this lease sketch. Last verified: 2026-09-18 22:10 UTC. **If those pages conflict with anything in Module A, those pages win. No combined green/red score.**

**What changed vs yesterday (sample format):** status Typical → Elevated because **daytime emersion overlapping forecast air** and a **wind/wave workability** flag entered the 72h window — not because SST crossed 19 °C.

---

## 9. Decision economics (oyster first; others sketched)

Company evaluation is not ML metrics alone.

| Term | Oyster 72h ops-risk (hypothesis) | Chinook encounter | Lobster CPUE |
|---|---|---|---|
| Action | Extra monitor, delay tumble, reassign crew, extra lash | Change start time / general area (coarsened) / cancel if conditions poor **and** season open | Change soak, bait, trip timing, coarse area |
| Cost of action | 2–8 labor-hours + skiff fuel (~$150–$600) or delayed handling | Fuel + opportunity of a booked trip; reputation if guests skunked | Bait + fuel + time; moving gear is expensive |
| Cost of missed event | Heat-handling mortality, bag loss, wasted crew day | Empty or thin trip; refunds; bad reviews | Poor CPUE trip; wasted bait |
| Cost of false alert | Alarm fatigue; skipped productive work window | Canceled good trip | Moved gear for nothing |
| Value of true alert | Avoided mortality/gear loss; labor sent to the right lease | Higher fill-rate **if** season open | Better CPUE or fewer wasted hauls |

A model/product may progress only with: better prediction, better decision economics, lead time, unique coverage, behavior change, or WTP. **v0 can progress on WTP + behavior change even with a manual brief.**

---

## 10. What we will not build in the first 90 days

- A Bloomberg-style ocean terminal
- A public fishing-spot or farm-performance map
- A Vibrio / biotoxin / harvest-legal product
- A catch-guarantee or “go here, catch Chinook” product
- AIS-as-abundance lobster maps
- Proprietary sensors “for defensibility”
- SMS spam of all-green days

---

## 11. Founder decisions this agent needs (do not invent)

1. Confirm or reject oyster-first vs interview all three in parallel for 14 days then choose.
2. Name 10 WA growers / PCSGA contacts the founder can intro (or authorize cold outreach).
3. Accept the **food-safety firewall** in all copy and sales.
4. Accept email/PDF as the product (no app).
5. Confirm whether a domain reviewer (shellfish physiologist / extension) is available.

---

## 12. Artifact map

| File | Role |
|---|---|
| `MVP_workflow.md` | User journey, daily loop, onboarding |
| `product_MVP_workflow.md` | Pointer to canonical workflow |
| `pricing_hypothesis.md` | Price, packaging, incentives |
| `pilot_offer.md` | One-page offer a grower can sign |
| `wireframe_spec.md` | ASCII email/PDF/WhatsApp/form |
| `outcome_capture_spec.md` | 30-second form + data rights |
| `partner_data_program.md` | Farm / charter / buyer programs |
| `competitive_landscape.md` | Alternatives; not a uniqueness claim |
| `30_60_90_day_plan.md` | Traction gates as **plan** |
| `agent_handoff.md` | 10-part handoff |
