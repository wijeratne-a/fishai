# Agent Handoff — PRODUCT_AND_MONETIZATION_AGENT

**Date:** 2026-09-18  
**Project:** Ocean Intelligence Builder / FishAI  
**Write path:** `/Users/wijeratne/dev/fishai/artifacts/product_and_monetization/`  
**Wedge lock:** **UNRESOLVED** (founder). This agent **recommends** but does not redefine a locked wedge.

---

## 1. Executive finding

The first **sellable, least-build, commercially testable** product is **not** a marine terminal and **not** a Chinook bite app.

It is a **daily email + 1-page PDF 72-hour operational stress brief** for **Pacific oyster farms in Washington**, aimed at crew/gear/handling decisions — **explicitly not food-safety, not harvest authorization, not Vibrio/HAB legality**.

**Why this wedge first**

- v0 is a **manual brief** from NANOOS + NWS + tides/waves + a farm card. No ML, no map product, no AIS.
- The buyer is a **business** with labor-dominated costs and year-round (or long-season) operations.
- Chinook is **season- and closure-gated** (2026 still includes area closures and Chinook retention bans) and **crowded** by $80–$200/yr forecast apps; legal landmines (catch guarantee, nav, weather-safety, license) are severe.
- Lobster next-trip CPUE has **larger industry dollars** (~$461M ME lobster ex-vessel, 2025 prelim.) but needs **private haul logs** from a territorial fishery; GFW AIS is the wrong object and is **noncommercial** without a custom license.

**MVP format:** daily email + PDF; WhatsApp only for Elevated/High or cannot-issue.  
**Price hypothesis:** $0 design-partner 8 weeks → $750–$1,500 / 90-day paid pilot → $400–$900 / farm / month (≤3 leases).  
**Why users log:** private weekly calibration of *their* lease, better next brief, bill credits / continuation gate, 30-second form — not “help our AI.”  
**Top substitutes:** NANOOS NVS Shellfish Growers, WDOH closure/Vp/temp tools, SoundToxins/PNW HAB (adjacent), BlueTrace/farm GIS; for the rejected-first Chinook wedge: Fishbrain, FishTrack, RipCharts, Hilton’s, ODFW/CDFW.

**Interviews completed:** **0**. Traction gates are a **plan**.

---

## 2. Evidence table

| Claim | Evidence | Strength |
|---|---|---|
| WA shellfish is a real B2B market | WA 2025 legislative assessment: $252.5M 2023 sales, $416M total impact; PCSGA cites >$270M / 3,200 jobs (older/different def.) | High (public econ) |
| Growers already have a free env ritual | NANOOS NVS Shellfish Growers; WDOH NVS temp maps; SoundToxins | High |
| Official harvest stack is separate | WDOH map viewer, closures, WAC 246-282-006 Vp plan | High |
| Oyster software $ exists | OysterTracker launched with paying farms (2018 press); evolved to BlueTrace; Taylor uses Esri | Medium (not 72h forecast WTP) |
| Chinook seasons can zero a product | ODFW 2026 seasons + in-season notices; CDFW KMZ/Fort Bragg commercial closed; Federal Register 2026 measures | High |
| Consumer fishing forecasts are cheap | Fishbrain Pro $79.99/yr; FishTrack ~$96/yr; RipCharts $99–$169/yr; Hilton $200/yr | High |
| ME lobster $ is large | DMR 2025 prelim. 78.8M lb, $461.4M; fewer trips YoY | High |
| GFW is not a lobster CPUE feed | Public map; APIs noncommercial CC BY-NC; AIS ≠ abundance; small-boat gap | High |
| GMRI already “forecasts lobster” phenology | Published seasonal timing forecast from NERACOOS temps | High |
| Farms will pay **this** brief | **None** | **Untested** |
| 15 interviews / 3 partners | **None** | **Untested** |

---

## 3. Source / license table

Product agent used **public web pages** for competitive and market context. **Not an ingest approval.**

| Source class | Example | Product use | License note |
|---|---|---|---|
| IOOS/NANOOS | NVS Shellfish Growers | v0 driver + competitor | Attribution; rights agent must classify commercial email use |
| NOAA NWS / CO-OPS / NDBC | Forecasts, tides, waves | v0 driver | USGov public; do not impersonate NWS |
| WA DOH | Map, closures, Vp | **Link only / context** | Official; never model as our food-safety output |
| SoundToxins / PNW HAB | Bulletins | Link; do not compete | Public-health adjacent |
| Copernicus Marine | Physics | Possible later driver | Account + terms; rights agent |
| Vendor marketing | Fishbrain, RipCharts, etc. | Competitive pricing | Do not scrape behind login |
| DMR / ODFW / CDFW | Landings, seasons | Context | Public; confidential microdata not ours |
| GFW | Effort map | **Do not use in commercial product** without custom license | NC API |
| Press / papers | OysterTracker, Mills 2017, Manolin 2019 price | Landscape | Cite; don’t overclaim |

Full legal classification: **DATA_RIGHTS_AND_PRIVACY_AGENT**. HUMAN LEGAL REVIEW on DUA/pilot terms.

---

## 4. Confidence and limitations

| Area | Confidence | Limitation |
|---|---|---|
| Format (email/PDF) over terminal | **High** | Matches master spec + grower ritual |
| Oyster-first vs Chinook-first | **Medium** | Ranking without interviews; NANOOS may be “good enough” |
| Price band $400–$900/mo | **Low–medium** | Analogies only; could clear at season-pack or not at all |
| Lobster as second wedge | **Medium** | High ACV, high data friction |
| Sample brief numbers | **Format only** | Fictional; not a live OSI-72 |
| Sibling science/rights artifacts | **Not merged** | Folder was empty at start of this run; orchestrator must reconcile |

---

## 5. Recommended decision

1. **Do not lock** the company wedge until founder + domain + rights + red-team read this **with** their artifacts.  
2. **For the 30-day commercial test, run Candidate A (oyster 72h ops-risk)** as specified in `pilot_offer.md`.  
3. Ship **email + PDF**, 14 contract fields, human QA, 30-second outcomes.  
4. Treat WDOH/SoundToxins as **authorities to link**, not rivals to replace.  
5. Park Chinook as a product; optional **5 dock interviews** only if founder wants a falsification set.  
6. Keep lobster as **explicit fallback** if oyster WTP fails **and** a co-op/vessel DUA is realistic.

---

## 6. Rejected alternatives

| Alternative | Why rejected *as first commercial test* |
|---|---|
| Global multi-tab terminal | Spec-forbidden; no pull; months of build |
| Chinook 24–48h encounter app | Season kill-switch, consumer-price crowding, catch/nav/weather/license landmines, needs partner catch immediately |
| Lobster CPUE as v0 | Labels + privacy + GFW temptation + slower sales; better as second |
| SMS-only | Cannot hold 14 fields; email/PDF is the archive |
| HAB/Vibrio product | Illegal/unsafe positioning vs WDOH; we lose by design |
| Public fishing heatmap | Privacy + ecological harm + Fishbrain already did the bad version |
| Hardware/sensors first | Partner-first ladder not exhausted |
| Pricing like Fishbrain ($8/mo) | Wrong buyer; cannot staff QA |
| Selling “AI abundance” | Claims policy violation |

---

## 7. Follow-up questions

1. Founder: oyster-first **yes/no**?  
2. Ten warm intros to WA growers?  
3. Domain reviewer identity?  
4. Counsel for DUA this week?  
5. Is anyone already a NANOOS power user we must beat, not ignore?  
6. Any existing farm spreadsheet of mortality we may **lawfully** see?  
7. Red team: is OSI-72 language separable from food-safety in grower speech?  
8. Rights: commercial redistribution of NANOOS plots in a **paid** PDF?  
9. Validation: what baseline is fair for n=3 leases?  
10. If interviews say “only HAB matters,” do we **stop** rather than pivot into food-safety?

---

## 8. Artifacts generated

All under `artifacts/product_and_monetization/`:

- `product_thesis.md` — three wedges, scorecard, **sample SAFE brief**  
- `MVP_workflow.md` — canonical workflow  
- `product_MVP_workflow.md` — pointer  
- `pricing_hypothesis.md`  
- `pilot_offer.md`  
- `wireframe_spec.md`  
- `outcome_capture_spec.md`  
- `partner_data_program.md`  
- `competitive_landscape.md`  
- `30_60_90_day_plan.md`  
- `agent_handoff.md` (this file)

---

## 9. Should this work be red-teamed?

**Yes.** High-severity product risks:

- Food-safety / harvest-authority **bleed** in copy or sales  
- False precision in sample-like numbers if someone forwards SAMPLE as real  
- Sensitive lease coordinates in email  
- Over-claiming uniqueness vs NANOOS  
- Chinook catch-guarantee if someone “just wants a fishing app”  
- AIS-as-abundance if lobster is revived  
- Fake traction if someone copies 30-day **targets** as results  

Handoff to **SCIENTIFIC_RED_TEAM_AGENT** and **DATA_RIGHTS_AND_PRIVACY_AGENT** before any real send.

---

## 10. Suggested next experiment

**Smallest high-value experiment:**  
In 14 days, complete **8 structured grower interviews** using the script in `30_60_90_day_plan.md`, send **one** 14-field SAMPLE (clearly labeled) to a willing reader, and attempt **one** signed 8-week $0 design-partner DUA.

**Success:** ≥5/8 say they would read a 16:30 lease email **and** ≥3 would log 30s **and** ≥1 signs.  
**Fail:** “I already have NANOOS” with no WTP **or** “just tell me if I can harvest.” Then write pivot_memo — do not build.

Do **not** ingest bulk data or train models for this experiment.
